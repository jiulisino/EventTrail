from flask import Blueprint, request, jsonify, session
from models import db, User
from services.sms_service import SMSService
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

@auth_bp.route('/send-code', methods=['POST'])
def send_code():
    """发送验证码"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        
        if not phone:
            return jsonify({'error': '手机号不能为空'}), 400
        
        if not validate_phone(phone):
            return jsonify({'error': '手机号格式不正确'}), 400
        
        sms_service = SMSService()
        
        # 检查频率限制
        if sms_service.is_rate_limited(phone):
            return jsonify({'error': '发送过于频繁，请稍后再试'}), 429
        
        # 发送验证码
        if sms_service.send_code(phone):
            return jsonify({'message': '验证码发送成功'}), 200
        else:
            return jsonify({'error': '验证码发送失败'}), 500
            
    except Exception as e:
        return jsonify({'error': '服务器错误'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        code = data.get('code', '').strip()
        
        if not phone or not code:
            return jsonify({'error': '手机号和验证码不能为空'}), 400
        
        if not validate_phone(phone):
            return jsonify({'error': '手机号格式不正确'}), 400
        
        # 验证验证码
        sms_service = SMSService()
        if not sms_service.verify_code(phone, code):
            return jsonify({'error': '验证码错误或已过期'}), 400
        
        # 检查用户是否已存在
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            return jsonify({'error': '该手机号已注册'}), 409
        
        # 创建新用户
        user = User(phone=phone)
        db.session.add(user)
        db.session.commit()
        
        # 设置session
        session['user_id'] = user.id
        session['phone'] = user.phone
        
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': user.id,
                'phone': user.phone
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器错误'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        code = data.get('code', '').strip()
        
        if not phone or not code:
            return jsonify({'error': '手机号和验证码不能为空'}), 400
        
        if not validate_phone(phone):
            return jsonify({'error': '手机号格式不正确'}), 400
        
        # 验证验证码
        sms_service = SMSService()
        if not sms_service.verify_code(phone, code):
            return jsonify({'error': '验证码错误或已过期'}), 400
        
        # 查找用户
        user = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({'error': '用户不存在，请先注册'}), 404
        
        # 设置session
        session['user_id'] = user.id
        session['phone'] = user.phone
        
        return jsonify({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'phone': user.phone
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': '服务器错误'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'message': '登出成功'}), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'phone': user.phone,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    }), 200 