from flask import Blueprint, request, jsonify, session
from models import db, Favorite, User
from services.coze_service import CozeService
from datetime import datetime

favorites_bp = Blueprint('favorites', __name__, url_prefix='/api/favorites')

def require_auth():
    """验证用户是否登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@favorites_bp.route('/', methods=['GET'])
def get_favorites():
    """获取用户收藏列表"""
    user = require_auth()
    if not user:
        return jsonify({'error': '请先登录'}), 401
    
    try:
        favorites = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.created_at.desc()).all()
        
        return jsonify({
            'message': '获取成功',
            'data': [favorite.to_dict() for favorite in favorites]
        }), 200
        
    except Exception as e:
        return jsonify({'error': '服务器错误'}), 500

@favorites_bp.route('/', methods=['POST'])
def add_favorite():
    """添加收藏"""
    user = require_auth()
    if not user:
        return jsonify({'error': '请先登录'}), 401
    
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['event_name', 'key_men', 'event_overview', 'key_point', 
                          'latest', 'event_cause', 'event_process', 'event_result', 'timeline']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 检查是否已收藏
        existing_favorite = Favorite.query.filter_by(
            user_id=user.id,
            event_name=data['event_name']
        ).first()
        
        if existing_favorite:
            return jsonify({'error': '该事件已收藏'}), 409
        
        # 创建收藏
        favorite = Favorite(
            user_id=user.id,
            event_name=data['event_name'],
            key_men=data['key_men'],
            event_overview=data['event_overview'],
            key_point=data['key_point'],
            latest=data['latest'],
            event_cause=data['event_cause'],
            event_process=data['event_process'],
            event_result=data['event_result'],
            timeline=data['timeline']
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'message': '收藏成功',
            'data': favorite.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器错误'}), 500

@favorites_bp.route('/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """删除收藏"""
    user = require_auth()
    if not user:
        return jsonify({'error': '请先登录'}), 401
    
    try:
        favorite = Favorite.query.filter_by(
            id=favorite_id,
            user_id=user.id
        ).first()
        
        if not favorite:
            return jsonify({'error': '收藏不存在'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器错误'}), 500

@favorites_bp.route('/<int:favorite_id>/refresh', methods=['POST'])
def refresh_favorite(favorite_id):
    """刷新事件进展"""
    user = require_auth()
    if not user:
        return jsonify({'error': '请先登录'}), 401
    
    try:
        favorite = Favorite.query.filter_by(
            id=favorite_id,
            user_id=user.id
        ).first()
        
        if not favorite:
            return jsonify({'error': '收藏不存在'}), 404
        
        coze_service = CozeService()
        
        # 重新搜索和分析事件
        result = coze_service.search_and_analyze_event(favorite.event_name)
        
        if not result:
            return jsonify({'error': '获取最新进展失败'}), 500
        
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
        
        return jsonify({
            'message': '刷新成功',
            'data': favorite.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器错误'}), 500 