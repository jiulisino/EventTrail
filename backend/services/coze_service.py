import json
import requests
from flask import current_app
from typing import Dict, List, Optional, Any

class CozeService:
    """扣子平台工作流调用服务"""
    
    def __init__(self):
        self.base_url = current_app.config['COZE_BASE_URL']
        self.token = current_app.config['COZE_TOKEN']
        self.workflow_ids = current_app.config['WORKFLOW_IDS']
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _call_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> Optional[Dict]:
        """调用工作流"""
        try:
            payload = {
                'workflow_id': workflow_id,
                'parameters': parameters
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # 解析返回的content字段
                if 'content' in data:
                    return json.loads(data['content'])
                return data
            else:
                current_app.logger.error(f"Coze API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error calling Coze workflow: {str(e)}")
            return None
    
    def identify_event_name(self, input_text: str) -> Optional[str]:
        """事件名称识别和优化"""
        workflow_id = self.workflow_ids['event_name_identification']
        result = self._call_workflow(workflow_id, {'input': input_text})
        
        if result and 'event_name' in result:
            event_name = result['event_name']
            # 检查是否为固定提示语
            if event_name == "您输入的内容与事件无关，请输入事件名称。":
                return None
            return event_name
        
        return None
    
    def collect_news(self, event_name: str) -> Optional[Dict]:
        """收集事件相关新闻"""
        workflow_id = self.workflow_ids['event_collection']
        result = self._call_workflow(workflow_id, {'keyword': event_name})
        
        if result and 'event_name' in result and 'news_list' in result:
            return {
                'event_name': result['event_name'],
                'news_list': result['news_list']
            }
        
        return None
    
    def analyze_event(self, event_name: str, news_list: List[str]) -> Optional[Dict]:
        """分析事件信息"""
        workflow_id = self.workflow_ids['event_analysis']
        result = self._call_workflow(workflow_id, {
            'event_name': event_name,
            'news_list': news_list
        })
        
        if result:
            # 验证返回的数据结构
            required_fields = [
                'event_name', 'key_men', 'event_overview', 'key_point',
                'latest', 'event_cause', 'event_process', 'event_result', 'timeline'
            ]
            
            if all(field in result for field in required_fields):
                return result
        
        return None
    
    def search_and_analyze_event(self, input_text: str) -> Optional[Dict]:
        """完整的搜索和分析流程"""
        # 1. 识别和优化事件名称
        event_name = self.identify_event_name(input_text)
        if not event_name:
            return None
        
        # 2. 收集新闻
        news_data = self.collect_news(event_name)
        if not news_data:
            return None
        
        # 3. 分析事件
        analysis_result = self.analyze_event(
            news_data['event_name'], 
            news_data['news_list']
        )
        
        if analysis_result:
            # 合并新闻列表到分析结果中
            analysis_result['news_list'] = news_data['news_list']
            return analysis_result
        
        return None 