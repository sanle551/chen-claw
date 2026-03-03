# web/auth.py
import os
import hmac
import base64
import json
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, render_template, redirect, make_response

try:
    import jwt as pyjwt  # PyJWT，如果没有则使用 itsdangerous 兜底
except Exception:
    pyjwt = None

try:
    from werkzeug.security import generate_password_hash, check_password_hash
except Exception:
    # 兜底实现（不推荐生产）
    import hashlib
    def generate_password_hash(pw):
        return "sha256$" + hashlib.sha256(pw.encode("utf-8")).hexdigest()
    def check_password_hash(ph, pw):
        if ph.startswith("sha256$"):
            return ph.split("$",1)[1] == generate_password_hash(pw).split("$",1)[1]
        return False

auth_bp = Blueprint("auth", __name__)
LOGGER = logging.getLogger("auth")

# ---------- DB Helpers ----------
def _default_db_path():
    # 优先 Flask config，其次环境变量，其次项目根目录 crypto.db
    return current_app.config.get("DATABASE") or os.environ.get("DATABASE") or os.path.join(current_app.root_path, "..", "crypto.db")

def get_db():
    path = _default_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS user_settings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        alerts_enabled INTEGER NOT NULL DEFAULT 0,
        telegram_chat_id TEXT NULL,
        telegram_bot_token TEXT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS watchlist(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_id TEXT NOT NULL,
        UNIQUE(user_id, token_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS alert_rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_id TEXT NOT NULL,
        threshold_percent REAL NOT NULL DEFAULT 5.0,
        direction TEXT NOT NULL DEFAULT 'both',
        enabled INTEGER NOT NULL DEFAULT 1,
        last_triggered_at TEXT NULL
    )""")
    conn.commit()

# ---------- JWT ----------
def _secret():
    return current_app.config.get("SECRET_KEY") or os.environ.get("APP_SECRET") or "dev-secret-change-me"

def _jwt_encode(payload: dict, exp_minutes=60*24):
    # 优先 PyJWT，否则 itsdangerous 风格（非严格 JWT）
    exp = int(time.time()) + exp_minutes*60
    payload = dict(payload)
    payload["exp"] = exp
    if pyjwt:
        token = pyjwt.encode(payload, _secret(), algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token
    else:
        # 简易 HMAC token：header.payload.signature（Base64URL）
        header = {"alg":"HS256","typ":"JWT"}
        def b64url(d):
            s = base64.urlsafe_b64encode(json.dumps(d, separators=(",",":")).encode("utf-8")).rstrip(b"=")
            return s.decode("ascii")
        h = b64url(header)
        p = b64url(payload)
        sig = base64.urlsafe_b64encode(hmac.new(_secret().encode("utf-8"), f"{h}.{p}".encode("ascii"), "sha256").digest()).rstrip(b"=").decode("ascii")
        return f"{h}.{p}.{sig}"

def _jwt_decode(token: str):
    if pyjwt:
        return pyjwt.decode(token, _secret(), algorithms=["HS256"])
    # 简易 HMAC 校验与 exp 检查
    try:
        h, p, s = token.split(".")
        sig = base64.urlsafe_b64encode(hmac.new(_secret().encode("utf-8"), f"{h}.{p}".encode("ascii"), "sha256").digest()).rstrip(b"=").decode("ascii")
        if not hmac.compare_digest(sig, s):
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(p + "==").decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
        return payload
    except Exception as e:
        raise ValueError("invalid token") from e

def get_current_user_id():
    # 仅在 jwt_required 环境下被调用
    return getattr(request, "_user_id", None)

def jwt_required(fn):
    @wraps(fn)
    def _w(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error":"missing bearer token"}), 401
        token = auth.split(" ",1)[1].strip()
        try:
            payload = _jwt_decode(token)
        except Exception:
            return jsonify({"error":"invalid token"}), 401
        request._user_id = int(payload.get("uid"))
        return fn(*args, **kwargs)
    return _w

# ---------- Auth APIs ----------
@auth_bp.route("/auth/register", methods=["GET","POST"])
def register():
    conn = get_db(); ensure_schema(conn)
    if request.method == "GET":
        return render_template("login.html", mode="register")
    data = request.get_json(silent=True) or request.form or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error":"username/password required"}), 400
    try:
        conn.execute("INSERT INTO users(username, password_hash, created_at) VALUES(?,?,?)",
                     (username, generate_password_hash(password), datetime.utcnow().isoformat(timespec="seconds")))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error":"username exists"}), 409
    return jsonify({"ok": True})

@auth_bp.route("/auth/login", methods=["GET","POST"])
def login():
    conn = get_db(); ensure_schema(conn)
    if request.method == "GET":
        return render_template("login.html", mode="login")
    data = request.get_json(silent=True) or request.form or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    cur = conn.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error":"invalid credentials"}), 401
    token = _jwt_encode({"uid": row["id"]}, exp_minutes=60*24*7)
    # 表单模式下设置 cookie，API 模式下返回 JSON
    if request.is_json:
        return jsonify({"token": token})
    resp = make_response(redirect("/"))
    resp.set_cookie("token", token, httponly=True, max_age=7*24*3600, samesite="Lax")
    return resp

@auth_bp.route("/auth/logout", methods=["POST","GET"])
def logout():
    # JWT 为无状态；表单模式下清 cookie
    if request.method == "GET":
        resp = make_response(redirect("/auth/login"))
        resp.delete_cookie("token")
        return resp
    return jsonify({"ok": True})

# ---------- User Settings ----------
@auth_bp.route("/api/user/settings", methods=["GET","PATCH"])
@jwt_required
def user_settings():
    uid = get_current_user_id()
    conn = get_db(); ensure_schema(conn)
    if request.method == "GET":
        cur = conn.execute("""SELECT alerts_enabled, telegram_chat_id, telegram_bot_token
                              FROM user_settings WHERE user_id=?""", (uid,))
        row = cur.fetchone()
        if not row:
            return jsonify({"alerts_enabled": False, "telegram_chat_id": None, "telegram_bot_token": None})
        return jsonify({k: row[k] for k in row.keys()})
    data = request.get_json(force=True, silent=True) or {}
    fields, args = [], []
    for k in ("alerts_enabled","telegram_chat_id","telegram_bot_token"):
        if k in data:
            fields.append(f"{k}=?")
            v = data[k]
            if k == "alerts_enabled":
                v = 1 if v else 0
            args.append(v)
    if not fields:
        return jsonify({"error":"no fields"}), 400
    # upsert
    args.extend([uid])
    conn.execute(f"""INSERT INTO user_settings(user_id, {', '.join([f.split('=')[0] for f in fields])})
                     VALUES(?, {', '.join(['?']*len(fields))})
                     ON CONFLICT(user_id) DO UPDATE SET {', '.join(fields)}
                  """, tuple([uid] + args[:-1]))
    conn.commit()
    return jsonify({"ok": True})

# ---------- Watchlist ----------
@auth_bp.route("/api/watchlist", methods=["GET","POST"])
@jwt_required
def watchlist():
    uid = get_current_user_id()
    conn = get_db(); ensure_schema(conn)
    if request.method == "GET":
        cur = conn.execute("SELECT token_id FROM watchlist WHERE user_id=? ORDER BY token_id", (uid,))
        return jsonify({"items":[r["token_id"] for r in cur.fetchall()]})
    data = request.get_json(force=True, silent=True) or {}
    token_id = (data.get("token_id") or "").strip().lower()
    if not token_id:
        return jsonify({"error":"token_id required"}), 400
    try:
        conn.execute("INSERT INTO watchlist(user_id, token_id) VALUES(?,?)", (uid, token_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    return jsonify({"ok": True})

@auth_bp.route("/api/watchlist/<token_id>", methods=["DELETE"])
@jwt_required
def watchlist_delete(token_id):
    uid = get_current_user_id()
    conn = get_db(); ensure_schema(conn)
    conn.execute("DELETE FROM watchlist WHERE user_id=? AND token_id=?", (uid, token_id.lower()))
    conn.commit()
    return jsonify({"ok": True})

# ---------- Simple login page ----------
# 模板: web/templates/login.html
