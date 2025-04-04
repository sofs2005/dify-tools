import requests
from typing import Dict, Any, List
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from collections.abc import Generator

class JuejinThemeTool(Tool):
    """掘金话题查询工具"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def get_themes(self, cookies: str, cursor: str = "0", limit: int = 10) -> List[Dict[str, Any]]:
        """获取话题列表
        Args:
            cookies: 登录凭证
            cursor: 分页游标
            limit: 每页数量
        """
        url = "https://api.juejin.cn/tag_api/v1/theme/list_by_hot"
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "cookie": cookies,
            "referer": "https://juejin.cn/"
        }
        
        params = {
            "aid": "2608",
            "uuid": "7293505961473721866"
        }
        
        data = {
            "cursor": cursor,
            "keyword": "",
            "limit": limit,
            "theme_type": 1
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('err_no') != 0:
                raise Exception(result.get('err_msg', '获取话题列表失败'))
                
            return result['data']
            
        except Exception as e:
            raise Exception(f"获取话题列表失败: {str(e)}")
            
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cookies = tool_parameters.get('cookies')
        cursor = tool_parameters.get('cursor', '0')
        limit = tool_parameters.get('limit', 10)
        
        try:
            themes = self.get_themes(cookies, cursor, limit)
            
            # 格式化话题信息，返回 theme 字段
            formatted_themes = []
            for item in themes:
                if 'theme' in item:
                    formatted_themes.append(item['theme'])
            
            yield ToolInvokeMessage(
                type="json",
                message={
                    "json_object": {
                        "themes": formatted_themes
                    }
                }
            )
            
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"获取话题列表失败：{str(e)}"
                }
            )
            raise e 