import requests
from typing import Dict, Any, List
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from collections.abc import Generator

class JuejinColumnTool(Tool):
    """掘金专栏查询工具"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def get_columns(self, cookies: str, cursor: str = "0", limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户专栏列表
        Args:
            cookies: 登录凭证
            cursor: 分页游标
            limit: 每页数量
        """
        url = "https://api.juejin.cn/content_api/v1/column/self_center_list"
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "cookie": cookies,
            "referer": "https://juejin.cn/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }
        
        params = {
            "aid": "2608",
            "uuid": "7293505961473721866"
        }
        
        data = {
            "user_id": "2562294138804371",
            "cursor": cursor,
            "keyword": "",
            "limit": limit
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()

            if result.get('err_no') != 0:
                raise Exception(result.get('err_msg', '获取专栏列表失败'))
                
            return result['data']
            
        except Exception as e:
            raise Exception(f"获取专栏列表失败: {str(e)}")
            
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cookies = tool_parameters.get('cookies')
        cursor = tool_parameters.get('cursor', '0')
        limit = tool_parameters.get('limit', 10)
        
        try:
            columns = self.get_columns(cookies, cursor, limit)

            # 格式化专栏信息，返回 column_version 字段
            formatted_columns = []
            for item in columns:
                if 'column_version' in item:
                    formatted_columns.append(item['column_version'])
            
            yield ToolInvokeMessage(
                type="json",
                message={
                    "json_object": {
                        "columns": formatted_columns
                    }
                }
            )
            
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"获取专栏列表失败：{str(e)}"
                }
            )
            raise e 