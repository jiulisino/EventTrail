from flask import Blueprint, request, jsonify
import uuid
import concurrent.futures
from services.coze_service import CozeService
from flask import Blueprint, request, jsonify, current_app
from models import db, EventAnalysis
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

# 用于存储异步分析任务的结果
analysis_results = {}

# 异步执行事件分析的函数
def async_analyze_event(event_id, event_name, news_list):
    try:
        # 延迟导入create_app，避免循环导入
        from app import create_app
        
        # 创建一个新的应用上下文
        app = create_app()
        with app.app_context():
            coze_service = CozeService()
            result = coze_service.analyze_event(event_name, news_list)
            
            # 存储分析结果
            analysis_results[event_id] = {
                'status': 'completed',
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # 将结果存储到数据库
            analysis = EventAnalysis.query.get(event_id)
            if analysis:
                analysis.result = result
                analysis.status = 'completed'
                analysis.completed_at = datetime.utcnow()
                db.session.commit()
        
    except Exception as e:
        # 延迟导入create_app，避免循环导入
        from app import create_app
        
        # 在异常处理中也创建应用上下文，确保logger能正常工作
        app = create_app()
        with app.app_context():
            current_app.logger.error(f"异步分析事件失败: {str(e)}")
        
        analysis_results[event_id] = {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

@events_bp.route('/search', methods=['POST'])
def search_event():
    """搜索事件并立即返回新闻列表，同时异步分析事件"""
    try:
        data = request.get_json()
        input_text = data.get('input', '').strip()
        
        if not input_text:
            return jsonify({'error': '请输入事件名称'}), 400
        
        coze_service = CozeService()
        
        # 1. 识别和优化事件名称
        event_name = coze_service.identify_event_name(input_text)
        if not event_name:
            current_app.logger.warning(f"无法识别事件名称: {input_text}")
            return jsonify({'error': '您输入的内容与事件无关，请输入事件名称。'}), 400
        
        # 2. 收集新闻
        news_data = coze_service.collect_news(event_name)
        if not news_data:
            current_app.logger.warning(f"无法收集新闻: {event_name}")
            return jsonify({'error': '无法获取相关新闻，请重试。'}), 500
        
        # 生成唯一的事件ID
        event_id = str(uuid.uuid4())
        
        # 3. 创建事件分析记录并保存到数据库
        with current_app.app_context():
            analysis = EventAnalysis(
                id=event_id,
                event_name=news_data['event_name'],
                status='pending'
            )
            db.session.add(analysis)
            db.session.commit()
        
        # 4. 异步执行事件分析
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(async_analyze_event, event_id, news_data['event_name'], news_data['news_list'])
        
        # 4. 立即返回新闻列表
        return jsonify({
            'message': '新闻列表获取成功，事件分析正在进行中',
            'data': {
                'event_id': event_id,
                'event_name': news_data['event_name'],
                'news_list': news_data['news_list'],
                'analysis_status': 'pending'
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"搜索事件失败: {str(e)}")
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

@events_bp.route('/analysis/<event_id>', methods=['GET'])
def get_event_analysis(event_id):
    """查询事件分析结果"""
    try:
        # 首先检查内存中的结果
        if event_id in analysis_results:
            result = analysis_results[event_id]
            return jsonify({
                'message': '查询成功',
                'data': result
            }), 200
        
        # 如果内存中没有，查询数据库
        with current_app.app_context():
            analysis = EventAnalysis.query.get(event_id)
            if not analysis:
                return jsonify({'error': '找不到事件分析记录'}), 404
            
            return jsonify({
                'message': '查询成功',
                'data': {
                    'status': analysis.status,
                    'data': analysis.result,
                    'timestamp': analysis.updated_at.isoformat() if analysis.updated_at else None
                }
            }), 200
        
    except Exception as e:
        current_app.logger.error(f"查询事件分析结果失败: {str(e)}")
        return jsonify({'error': '服务器错误'}), 500