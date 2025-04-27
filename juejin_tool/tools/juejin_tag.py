import requests
from typing import Dict, Any, List
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from collections.abc import Generator

class JuejinTagTool(Tool):
    """掘金标签查询工具"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def get_tags(self, cookies: str, cursor: str = "0", key_word: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """获取标签列表
        Args:
            cookies: 登录凭证
            cursor: 分页游标
            key_word: 搜索关键词
            limit: 每页数量
        """
        url = "https://api.juejin.cn/tag_api/v1/query_tag_list"
        
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
            "key_word": key_word,
            "limit": limit,
            "sort_type": 1
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('err_no') != 0:
                raise Exception(result.get('err_msg', '获取标签列表失败'))
                
            return result['data']
            
        except Exception as e:
            raise Exception(f"获取标签列表失败: {str(e)}")
            
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cookies = tool_parameters.get('cookies')
        cursor = tool_parameters.get('cursor', '0')
        limit = tool_parameters.get('limit', 10)
        
        try:
            tags = self.get_tags(cookies=cookies, cursor=cursor, limit=limit)
            
            # 格式化标签信息，直接返回 tag 字段
            formatted_tags = []
            for item in tags:
                if 'tag' in item:
                    formatted_tags.append(item['tag'])
            
            yield ToolInvokeMessage(
                type="json",
                message={
                    "json_object": {
                        "tags": formatted_tags
                    }
                }
            )
            
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"获取标签列表失败：{str(e)}"
                }
            )
            raise e 