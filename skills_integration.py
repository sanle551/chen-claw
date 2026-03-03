"""
技能整合模块 - 将技能系统集成到主应用
"""
import os
import json
import logging
from pathlib import Path

LOGGER = logging.getLogger("skills_integration")

class SkillsIntegration:
    """技能整合器"""
    
    def __init__(self, app=None):
        self.app = app
        self.enabled_skills = []
        self.skill_instances = {}
        self.load_enabled_skills()
        
    def load_enabled_skills(self):
        """加载启用的技能列表"""
        skills_dir = Path(__file__).parent / "skills"
        enabled_file = skills_dir / "enabled.json"
        
        if enabled_file.exists():
            with open(enabled_file) as f:
                self.enabled_skills = json.load(f)
        
        LOGGER.info(f"已加载 {len(self.enabled_skills)} 个技能: {self.enabled_skills}")
    
    def initialize_skills(self):
        """初始化所有启用的技能"""
        skills_dir = Path(__file__).parent / "skills"
        
        for skill_name in self.enabled_skills:
            try:
                # 查找技能模块
                for category in ["core", "data", "analysis"]:
                    skill_path = skills_dir / category / skill_name
                    if skill_path.exists():
                        # 动态导入技能
                        self._load_skill(skill_name, skill_path)
                        break
            except Exception as e:
                LOGGER.error(f"加载技能 {skill_name} 失败: {e}")
    
    def _load_skill(self, name: str, path: Path):
        """加载单个技能"""
        import importlib.util
        
        init_file = path / "__init__.py"
        if not init_file.exists():
            LOGGER.warning(f"技能 {name} 缺少 __init__.py")
            return
        
        # 动态导入
        spec = importlib.util.spec_from_file_location(f"skills.{name}", init_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 获取技能实例
        if hasattr(module, 'price_monitor'):
            self.skill_instances['price_monitor'] = module.price_monitor
            LOGGER.info(f"✅ 价格监控技能已加载")
        
        if hasattr(module, 'push_manager'):
            self.skill_instances['push_manager'] = module.push_manager
            LOGGER.info(f"✅ 推送管理技能已加载")
        
        if hasattr(module, 'ai_hub'):
            self.skill_instances['ai_hub'] = module.ai_hub
            LOGGER.info(f"✅ AI中心技能已加载")
    
    def get_skill(self, name: str):
        """获取技能实例"""
        return self.skill_instances.get(name)
    
    def setup_routes(self):
        """设置技能相关的路由"""
        if not self.app:
            return
        
        # 价格监控相关路由
        if 'price_monitor' in self.skill_instances:
            monitor = self.skill_instances['price_monitor']
            
            @self.app.route('/api/price/<symbol>')
            def get_price(symbol):
                data = monitor.get_price(symbol)
                if data:
                    return {'success': True, 'data': data}
                return {'success': False, 'error': 'Price not found'}, 404
            
            @self.app.route('/api/price/subscribe', methods=['POST'])
            def subscribe_price():
                # WebSocket或轮询订阅
                return {'success': True, 'message': 'Subscribed'}
        
        # 推送相关路由
        if 'push_manager' in self.skill_instances:
            push = self.skill_instances['push_manager']
            
            @self.app.route('/api/push/register', methods=['POST'])
            def register_push():
                data = request.get_json()
                sub_id = push.register_subscription(data.get('subscription'))
                return {'success': True, 'subscription_id': sub_id}
        
        LOGGER.info("✅ 技能路由已设置")
    
    def start_background_tasks(self):
        """启动后台任务"""
        # 价格监控
        if 'price_monitor' in self.skill_instances:
            monitor = self.skill_instances['price_monitor']
            monitor.start_monitoring(['BTC', 'ETH', 'SOL'], interval=60)
            LOGGER.info("✅ 价格监控后台任务已启动")

# 全局实例
skills_integration = None

def init_skills(app=None):
    """初始化技能系统"""
    global skills_integration
    skills_integration = SkillsIntegration(app)
    skills_integration.initialize_skills()
    
    if app:
        skills_integration.setup_routes()
    
    return skills_integration

def get_skills():
    """获取技能整合器"""
    return skills_integration
