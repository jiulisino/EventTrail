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
    
    def _call_workflow(self, workflow_id: str, parameters: Dict[str, Any], timeout: int = 60) -> Optional[Dict]:
        """调用工作流"""
        try:
            payload = {
                'workflow_id': workflow_id,
                'parameters': parameters
            }
            
            current_app.logger.info(f"Calling Coze API: {self.base_url}, payload: {payload}")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            current_app.logger.info(f"Coze API response status: {response.status_code}, content: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # 检查是否有data字段且是字符串类型
                    if 'data' in data and isinstance(data['data'], str):
                        try:
                            # 尝试解析data字段中的JSON字符串
                            return json.loads(data['data'])
                        except json.JSONDecodeError as e:
                            current_app.logger.error(f"JSON decode error in data field: {str(e)}, data: {data['data']}")
                            return None
                    return data
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"JSON decode error: {str(e)}, response text: {response.text}")
                    return None
            else:
                current_app.logger.error(f"Coze API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout as e:
            current_app.logger.error(f"Coze API timeout error: {str(e)}")
            # 对于超时错误，可以考虑增加重试逻辑
            return None
        except Exception as e:
            current_app.logger.error(f"Error calling Coze workflow: {str(e)}")
            return None
    
    def identify_event_name(self, input_text: str) -> Optional[str]:
        """事件名称识别和优化"""
        workflow_id = self.workflow_ids['event_name_identification']
        result = self._call_workflow(workflow_id, {'input': input_text})
        
        if result:
            # 检查result是否直接包含event_name字段
            if 'event_name' in result:
                event_name = result['event_name']
                # 检查是否为固定提示语
                if event_name == "您输入的内容与事件无关，请输入事件名称。" or event_name == "无法回应该搜索。":
                    return None
                return event_name
            # 检查result是否包含data字段且data是字典
            elif 'data' in result and isinstance(result['data'], dict) and 'event_name' in result['data']:
                event_name = result['data']['event_name']
                # 检查是否为固定提示语
                if event_name == "您输入的内容与事件无关，请输入事件名称。" or event_name == "无法回应该搜索。":
                    return None
                return event_name
        
        current_app.logger.warning(f"Failed to identify event name from result: {result}")
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
        # 增加分析事件的超时时间
        result = self._call_workflow(workflow_id, {
            'event_name': event_name,
            'news_list': news_list
        }, timeout=120)
        
        if result:
            # 验证返回的数据结构
            required_fields = [
                'event_name', 'key_men', 'event_overview', 'key_point',
                'latest', 'event_cause', 'event_process', 'event_result', 'timeline'
            ]
            
            # 放宽验证要求，即使缺少某些字段也返回结果
            if 'event_name' in result:
                return result
        
        current_app.logger.warning(f"Event analysis returned incomplete data for: {event_name}")
        # 分析失败时，返回包含新闻列表的基本信息
        return {
            'event_name': event_name,
            'news_list': news_list,
            'event_overview': '事件分析超时，仅返回新闻列表',
            'key_point': '事件分析超时'
        }
    
    def search_and_analyze_event(self, input_text: str) -> Optional[Dict]:
        """完整的搜索和分析流程"""
        # 1. 识别和优化事件名称
        event_name = self.identify_event_name(input_text)
        if not event_name:
            current_app.logger.warning(f"Could not identify event name for input: {input_text}")
            # 重新调用工作流以获取具体错误信息
            workflow_id = self.workflow_ids['event_name_identification']
            raw_result = self._call_workflow(workflow_id, {'input': input_text})
            
            # 检查具体错误类型
            error_message = "您输入的内容与事件无关，请输入事件名称。"
            if raw_result:
                # 直接检查返回的原始结果中是否包含特定错误字符串
                result_str = str(raw_result)
                if "无法回应该搜索。" in result_str:
                    error_message = "无法回应该搜索。"
                     
            # 返回包含错误信息的字典
            return {'error': error_message}
        
        current_app.logger.info(f"Identified event name: {event_name}")
        
        # 2. 收集新闻
        news_data = self.collect_news(event_name)
        if not news_data:
            current_app.logger.warning(f"Could not collect news for event: {event_name}")
            return None
        
        current_app.logger.info(f"Collected {len(news_data['news_list'])} news items for event: {event_name}")
        
        # 3. 分析事件
        analysis_result = self.analyze_event(
            news_data['event_name'], 
            news_data['news_list']
        )
        
        # 合并新闻列表到分析结果中
        analysis_result['news_list'] = news_data['news_list']
        return analysis_result
        
        # 如果分析失败，仍然返回新闻数据
        current_app.logger.warning(f"Event analysis failed for: {event_name}, returning news data only")
        return {
            'event_name': news_data['event_name'],
            'news_list': news_data['news_list'],
            'event_overview': '事件分析失败，仅返回新闻列表',
            'key_point': '事件分析失败'
        }