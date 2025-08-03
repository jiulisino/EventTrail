from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联收藏
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.phone}>'

class VerificationCode(db.Model):
    """验证码模型"""
    __tablename__ = 'verification_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<VerificationCode {self.phone}>'

class Favorite(db.Model):
    """收藏事件模型"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    key_men = db.Column(db.Text)
    event_overview = db.Column(db.Text)
    key_point = db.Column(db.Text)
    latest = db.Column(db.Text)
    event_cause = db.Column(db.Text)
    event_process = db.Column(db.Text)
    event_result = db.Column(db.Text)
    timeline = db.Column(db.JSON)  # 存储时间线数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_refresh = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'event_name': self.event_name,
            'key_men': self.key_men,
            'event_overview': self.event_overview,
            'key_point': self.key_point,
            'latest': self.latest,
            'event_cause': self.event_cause,
            'event_process': self.event_process,
            'event_result': self.event_result,
            'timeline': self.timeline,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None
        }
    
    def __repr__(self):
        return f'<Favorite {self.event_name}>' 