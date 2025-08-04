from flask import Blueprint, request, jsonify
from services.coze_service import CozeService

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

@events_bp.route('/search', methods=['POST'])
def search_event():
    """搜索和分析事件"""
    try:
        data = request.get_json()
        input_text = data.get('input', '').strip()
        
        if not input_text:
            return jsonify({'error': '请输入事件名称'}), 400
        
        coze_service = CozeService()
        
        # 执行完整的搜索和分析流程
        result = coze_service.search_and_analyze_event(input_text)
        
        # 检查是否有错误信息
        if result and 'error' in result:
            return jsonify({'error': result['error']}), 400

        if not result:
            return jsonify({'error': '处理失败，请重试。'}), 400
        
        return jsonify({
            'message': '搜索成功',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': '服务器错误'}), 500

@events_bp.route('/analyze', methods=['POST'])
def analyze_event():
    """分析事件（单独接口）"""
    try:
        data = request.get_json()
        event_name = data.get('event_name', '').strip()
        news_list = data.get('news_list', [])
        
        if not event_name:
            return jsonify({'error': '事件名称不能为空'}), 400
        
        if not news_list:
            return jsonify({'error': '新闻列表不能为空'}), 400
        
        coze_service = CozeService()
        result = coze_service.analyze_event(event_name, news_list)
        
        if not result:
            return jsonify({'error': '事件分析失败'}), 500
        
        return jsonify({
            'message': '分析成功',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': '服务器错误'}), 500

@events_bp.route('/news', methods=['POST'])
def get_news():
    """获取新闻列表（单独接口）"""
    try:
        data = request.get_json()
        event_name = data.get('event_name', '').strip()
        
        if not event_name:
            return jsonify({'error': '事件名称不能为空'}), 400
        
        coze_service = CozeService()
        result = coze_service.collect_news(event_name)
        
        if not result:
            return jsonify({'error': '获取新闻失败'}), 500
        
        return jsonify({
            'message': '获取成功',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': '服务器错误'}), 500