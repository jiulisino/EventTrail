import os
from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from config import config
from models import db
from routes.auth import auth_bp
from routes.events import events_bp
from routes.favorites import favorites_bp
from utils.database import init_db

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(favorites_bp)
    
    # 初始化数据库
    with app.app_context():
        init_db()
    
    # 配置定时任务
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=refresh_all_favorites,
        trigger="cron",
        hour=6,
        minute=0,
        id="refresh_favorites",
        replace_existing=True
    )
    scheduler.start()
    
    @app.route('/')
    def index():
        return {'message': '来龙去脉事件追踪器API', 'status': 'running'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    
    return app

def refresh_all_favorites():
    """定时刷新所有收藏事件（每日上午6点执行）"""
    from services.coze_service import CozeService
    from models import Favorite
    
    app = Flask(__name__)
    app.config.from_object(config['default'])
    db.init_app(app)
    
    with app.app_context():
        try:
            coze_service = CozeService()
            favorites = Favorite.query.all()
            
            for favorite in favorites:
                try:
                    # 重新搜索和分析事件
                    result = coze_service.search_and_analyze_event(favorite.event_name)
                    
                    if result:
                        # 更新收藏信息
                        favorite.key_men = result['key_men']
                        favorite.event_overview = result['event_overview']
                        favorite.key_point = result['key_point']
                        favorite.latest = result['latest']
                        favorite.event_cause = result['event_cause']
                        favorite.event_process = result['event_process']
                        favorite.event_result = result['event_result']
                        favorite.timeline = result['timeline']
                        favorite.last_refresh = datetime.utcnow()
                        
                        db.session.commit()
                        app.logger.info(f"已更新收藏事件: {favorite.event_name}")
                    
                except Exception as e:
                    app.logger.error(f"更新收藏事件失败 {favorite.event_name}: {str(e)}")
                    db.session.rollback()
                    continue
            
            app.logger.info("定时刷新收藏事件完成")
            
        except Exception as e:
            app.logger.error(f"定时任务执行失败: {str(e)}")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 