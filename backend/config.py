import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///eventtrail.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 扣子平台配置
    COZE_TOKEN = 'pat_bfFS5ooxdOoj9xpCK8VS9sSOlWWdkHdzs18TAv6u0pixs3aP3vTX4w6AWx6F5wKa'
    COZE_BASE_URL = 'https://api.coze.cn/v1/workflow/run'
    
    # 工作流ID
    WORKFLOW_IDS = {
        'event_name_identification': '7534025846535258151',
        'event_collection': '7529567713032601643',
        'event_analysis': '7527334340147150857',
        'event_update': '7534551436102254644'
    }
    
    # 短信验证码配置（模拟）
    SMS_CODE_EXPIRE_MINUTES = 5
    SMS_CODE_LENGTH = 6
    
    # 定时任务配置
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Asia/Shanghai"
    
    # 跨域配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}