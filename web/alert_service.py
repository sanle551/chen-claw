# web/alert_service.py
import os
import json
import time
import threading
import sqlite3
import logging
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from flask import Blueprint, request, jsonify, current_app

# 复用 auth 模块的 jwt 装饰器与 DB 工具
try:
    from .auth import jwt_required, get_current_user_id, get_db, ensure_schema
except Exception:
    # 兜底（单测/导入顺序）
    def jwt_required(fn):
        def _w(*a, **k):
            raise RuntimeError("auth.jwt_required missing; ensure web/auth.py is registered before alerts")
        return _w
    def get_current_user_id():
        return None
    def get_db():
        db_path = current_app.config.get("DATABASE") or os.environ.get("DATABASE") or os.path.join(current_app.root_path, "..", "crypto.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    def ensure_schema(conn):  # 最少建表，避免首次运行崩溃
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS alert_rules(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_id TEXT NOT NULL,
            threshold_percent REAL NOT NULL DEFAULT 5.0,
            direction TEXT NOT NULL DEFAULT 'both', -- up/down/both
            enabled INTEGER NOT NULL DEFAULT 1,
            last_triggered_at TEXT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_settings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            alerts_enabled INTEGER NOT NULL DEFAULT 0,
            telegram_chat_id TEXT NULL,
            telegram_bot_token TEXT NULL
        )""")
        conn.commit()

alerts_bp = Blueprint("alerts", __name__)

LOGGER = logging.getLogger("alerts")

COINGECKO_SIMPLE_URL = "https://api.coingecko.com/api/v3/simple/price"

def _http_get_json(url: str, headers=None, q=None):
    if q:
        url = f"{url}?{urlencode(q)}"
    req = Request(url, headers=headers or {"User-Agent":"crypto-daily-analyzer/alerts"})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def fetch_24h_change(token_ids):
    """
    返回 {token_id: {'usd': price, 'usd_24h_change': pct}}，缺失的键安全忽略
    """
    if not token_ids:
        return {}
    ids = ",".join(sorted(set(token_ids)))
    data = _http_get_json(COINGECKO_SIMPLE_URL, q={
        "ids": ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    })
    return data or {}

def send_telegram_message(text: str, user_row=None):
    """
    优先使用用户级设置（user_settings.telegram_bot_token/chat_id），
    其次使用环境变量 TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID。
    """
    token = None
    chat_id = None
    if user_row:
        token = user_row.get("telegram_bot_token") or None
        chat_id = user_row.get("telegram_chat_id") or None
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        LOGGER.warning("Telegram not configured; skip push. token? %s chat_id? %s", bool(token), bool(chat_id))
        return False
    api = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        req = Request(api, data=urlencode(payload).encode("utf-8"), headers={"Content-Type":"application/x-www-form-urlencoded"})
        with urlopen(req, timeout=20) as resp:
            ok = resp.getcode() == 200
            if not ok:
                LOGGER.error("Telegram push failed: HTTP %s", resp.getcode())
            return ok
    except Exception as e:
        LOGGER.exception("Telegram push error: %s", e)
        return False

def _load_enabled_users_and_rules(conn):
    """
    返回列表: [(user_row, [rule_rows...]), ...]
    """
    c = conn.cursor()
    c.execute("""SELECT u.id AS user_id, s.alerts_enabled, s.telegram_chat_id, s.telegram_bot_token
                 FROM users u
                 LEFT JOIN user_settings s ON s.user_id = u.id
                 WHERE COALESCE(s.alerts_enabled,0)=1""")
    users = [dict(zip([d[0] for d in c.description], row)) for row in c.fetchall()]
    result = []
    for u in users:
        c.execute("""SELECT id, user_id, token_id, threshold_percent, direction, enabled, last_triggered_at
                     FROM alert_rules WHERE user_id=? AND enabled=1""", (u["user_id"],))
        rules = [dict(zip([d[0] for d in c.description], row)) for row in c.fetchall()]
        if rules:
            result.append((u, rules))
    return result

def _should_trigger(change_pct: float, rule):
    direction = (rule.get("direction") or "both").lower()
    thr = float(rule.get("threshold_percent") or 5.0)
    if direction == "up":
        return change_pct >= thr
    if direction == "down":
        return change_pct <= -thr
    return abs(change_pct) >= thr

def _already_recently_triggered(rule, minutes=30):
    ts = rule.get("last_triggered_at")
    if not ts:
        return False
    try:
        dt = datetime.fromisoformat(ts)
        return (datetime.utcnow() - dt) < timedelta(minutes=minutes)
    except Exception:
        return False

def _mark_triggered(conn, rule_id: int):
    conn.execute("UPDATE alert_rules SET last_triggered_at=? WHERE id=?", (datetime.utcnow().isoformat(timespec="seconds"), rule_id))
    conn.commit()

def alert_worker(app, interval_sec=300):
    """
    背景线程：每 interval_sec 秒检查一次。使用 app.app_context() 访问配置/日志。
    """
    with app.app_context():
        LOGGER.info("Alert worker started; interval=%ss", interval_sec)
    while True:
        try:
            with app.app_context():
                conn = get_db()
                ensure_schema(conn)  # 确保表存在
                items = _load_enabled_users_and_rules(conn)
                # 汇总需要查询的 token 列表
                need_tokens = set()
                for _, rules in items:
                    for r in rules:
                        need_tokens.add(r["token_id"])
                prices = fetch_24h_change(sorted(need_tokens))
                # 评估触发
                for user_row, rules in items:
                    for r in rules:
                        t = r["token_id"]
                        info = prices.get(t) or {}
                        chg = info.get("usd_24h_change")
                        if chg is None:
                            continue
                        try:
                            chg = float(chg)
                        except Exception:
                            continue
                        if _should_trigger(chg, r):
                            if not _already_recently_triggered(r):
                                sign = "📈" if chg >= 0 else "📉"
                                text = f"{sign} <b>{t.upper()}</b> 24h 变化 {chg:.2f}%（阈值 {r['threshold_percent']}%）"
                                if send_telegram_message(text, user_row=user_row):
                                    _mark_triggered(conn, r["id"])
                try:
                    conn.close()
                except Exception:
                    pass
        except Exception as e:
            with app.app_context():
                LOGGER.exception("Alert worker loop error: %s", e)
        time.sleep(interval_sec)

_worker_thread = None

def start_alert_worker(app, interval_sec=300):
    global _worker_thread
    if _worker_thread and _worker_thread.is_alive():
        return _worker_thread
    # 避免开发模式多进程重复启动，允许通过 env 禁用
    if os.environ.get("DISABLE_ALERT_WORKER") == "1":
        with app.app_context():
            LOGGER.info("Alert worker disabled by env")
        return None
    t = threading.Thread(target=alert_worker, args=(app, interval_sec), daemon=True)
    t.start()
    _worker_thread = t
    return t

# ------------------- REST API -------------------

@alerts_bp.route("/api/alerts", methods=["GET"])
@jwt_required
def list_alerts():
    uid = get_current_user_id()
    conn = get_db()
    ensure_schema(conn)
    cur = conn.execute("""SELECT id, token_id, threshold_percent, direction, enabled, last_triggered_at
                          FROM alert_rules WHERE user_id=? ORDER BY id DESC""", (uid,))
    rows = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    return jsonify({"items": rows})

@alerts_bp.route("/api/alerts", methods=["POST"])
@jwt_required
def create_alert():
    uid = get_current_user_id()
    payload = request.get_json(force=True, silent=True) or {}
    token_id = (payload.get("token_id") or "").strip().lower()
    thr = float(payload.get("threshold_percent") or 5.0)
    direction = (payload.get("direction") or "both").lower()
    enabled = 1 if (payload.get("enabled", True)) else 0
    if not token_id:
        return jsonify({"error":"token_id required"}), 400
    conn = get_db(); ensure_schema(conn)
    cur = conn.execute("""INSERT INTO alert_rules(user_id, token_id, threshold_percent, direction, enabled)
                          VALUES(?,?,?,?,?)""", (uid, token_id, thr, direction, enabled))
    conn.commit()
    return jsonify({"id": cur.lastrowid, "ok": True}), 201

@alerts_bp.route("/api/alerts/<int:rule_id>", methods=["PUT","PATCH"])
@jwt_required
def update_alert(rule_id):
    uid = get_current_user_id()
    payload = request.get_json(force=True, silent=True) or {}
    fields = []
    args = []
    for key in ("token_id","threshold_percent","direction","enabled"):
        if key in payload:
            fields.append(f"{key}=?")
            val = payload[key]
            if key == "token_id":
                val = (val or "").strip().lower()
            if key == "enabled":
                val = 1 if val else 0
            args.append(val)
    if not fields:
        return jsonify({"error":"no fields"}), 400
    args.extend([uid, rule_id])
    conn = get_db(); ensure_schema(conn)
    cur = conn.execute(f"UPDATE alert_rules SET {', '.join(fields)} WHERE user_id=? AND id=?", args)
    conn.commit()
    if cur.rowcount == 0:
        return jsonify({"error":"not found"}), 404
    return jsonify({"ok": True})

@alerts_bp.route("/api/alerts/<int:rule_id>", methods=["DELETE"])
@jwt_required
def delete_alert(rule_id):
    uid = get_current_user_id()
    conn = get_db(); ensure_schema(conn)
    cur = conn.execute("DELETE FROM alert_rules WHERE user_id=? AND id=?", (uid, rule_id))
    conn.commit()
    if cur.rowcount == 0:
        return jsonify({"error":"not found"}), 404
    return jsonify({"ok": True})

@alerts_bp.route("/api/alerts/toggle", methods=["POST"])
@jwt_required
def toggle_alerts():
    uid = get_current_user_id()
    payload = request.get_json(force=True, silent=True) or {}
    enabled = 1 if payload.get("enabled", True) else 0
    conn = get_db(); ensure_schema(conn)
    # upsert
    conn.execute("""INSERT INTO user_settings(user_id, alerts_enabled)
                    VALUES(?,?)
                    ON CONFLICT(user_id) DO UPDATE SET alerts_enabled=excluded.alerts_enabled""",
                 (uid, enabled))
    conn.commit()
    return jsonify({"ok": True, "enabled": bool(enabled)})
