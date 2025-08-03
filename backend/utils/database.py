from flask import current_app
from models import db

def init_db():
    """初始化数据库"""
    with current_app.app_context():
        db.create_all()
        current_app.logger.info("数据库初始化完成")

def clear_db():
    """清空数据库"""
    with current_app.app_context():
        db.drop_all()
        db.create_all()
        current_app.logger.info("数据库已清空并重新初始化") 