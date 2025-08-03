import random
import string
from datetime import datetime, timedelta
from flask import current_app
from models import db, VerificationCode

class SMSService:
    """短信验证码服务（模拟实现）"""
    
    def __init__(self):
        self.code_length = current_app.config['SMS_CODE_LENGTH']
        self.expire_minutes = current_app.config['SMS_CODE_EXPIRE_MINUTES']
    
    def generate_code(self) -> str:
        """生成验证码"""
        return ''.join(random.choices(string.digits, k=self.code_length))
    
    def send_code(self, phone: str) -> bool:
        """发送验证码（模拟）"""
        try:
            # 生成验证码
            code = self.generate_code()
            
            # 设置过期时间
            expires_at = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
            
            # 保存到数据库
            verification_code = VerificationCode(
                phone=phone,
                code=code,
                expires_at=expires_at
            )
            
            db.session.add(verification_code)
            db.session.commit()
            
            # 模拟发送短信（实际项目中这里会调用短信服务商的API）
            current_app.logger.info(f"模拟发送验证码到 {phone}: {code}")
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"发送验证码失败: {str(e)}")
            db.session.rollback()
            return False
    
    def verify_code(self, phone: str, code: str) -> bool:
        """验证验证码"""
        try:
            # 查找最新的未使用验证码
            verification_code = VerificationCode.query.filter_by(
                phone=phone,
                used=False
            ).order_by(VerificationCode.created_at.desc()).first()
            
            if not verification_code:
                return False
            
            # 检查是否过期
            if verification_code.is_expired():
                return False
            
            # 检查验证码是否匹配
            if verification_code.code != code:
                return False
            
            # 标记为已使用
            verification_code.used = True
            db.session.commit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"验证验证码失败: {str(e)}")
            db.session.rollback()
            return False
    
    def is_rate_limited(self, phone: str) -> bool:
        """检查是否被频率限制"""
        # 检查最近1分钟内是否已发送过验证码
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        
        recent_code = VerificationCode.query.filter_by(phone=phone).filter(
            VerificationCode.created_at > one_minute_ago
        ).first()
        
        return recent_code is not None 