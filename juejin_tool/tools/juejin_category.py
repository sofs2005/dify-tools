import requests
from typing import Dict, Any, List
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from collections.abc import Generator

class JuejinCategoryTool(Tool):
    """掘金分类查询工具"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def get_categories(self, cookies: str) -> List[Dict[str, Any]]:
        """获取分类列表"""
        url = "https://api.juejin.cn/tag_api/v1/query_category_list"
        
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
        
        try:
            response = requests.post(url, headers=headers, params=params, json={})
            response.raise_for_status()
            result = response.json()
            
            if result.get('err_no') != 0:
                raise Exception(result.get('err_msg', '获取分类列表失败'))
                
            return result['data']
            
        except Exception as e:
            raise Exception(f"获取分类列表失败: {str(e)}")
            
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cookies = tool_parameters.get('cookies')
        
        try:
            categories = self.get_categories(cookies)
            
            # 格式化分类信息，只返回 category 字段
            formatted_categories = []
            for item in categories:
                if 'category' in item:
                    category = item['category']
                    formatted_categories.append(category)
            
            yield ToolInvokeMessage(
                type="json",
                message={
                    "json_object": {
                        "categories": formatted_categories
                    }
                }
            )
            
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"获取分类列表失败：{str(e)}"
                }
            )
            raise e
        

if __name__ == "__main__":
    tool = JuejinCategoryTool()
    tool.invoke({
        "cookie": "__tea_cookie_tokens_2608=%257B%2522user_unique_id%2522%253A%25227293505961473721866%2522%252C%2522web_id%2522%253A%25227293505961473721866%2522%252C%2522timestamp%2522%253A1723558763718%257D; _tea_utm_cache_2608={%22utm_source%22:%22ryfzk%22}; passport_csrf_token=0fd949943a63a81fbaef594336b4f027; passport_csrf_token_default=0fd949943a63a81fbaef594336b4f027; n_mh=2dgc2pDTwPUy1tkpcppyQfE7oH_oAHzVusCToUVuoJg; sid_guard=ed0e2e13925faa082a6e278ca556b6eb%7C1738236685%7C31536000%7CFri%2C+30-Jan-2026+11%3A31%3A25+GMT; uid_tt=0b7fc34ae7b989f8cfc740b7b38b134b; uid_tt_ss=0b7fc34ae7b989f8cfc740b7b38b134b; sid_tt=ed0e2e13925faa082a6e278ca556b6eb; sessionid=ed0e2e13925faa082a6e278ca556b6eb; sessionid_ss=ed0e2e13925faa082a6e278ca556b6eb; is_staff_user=false; sid_ucp_v1=1.0.0-KDNlZWVlZjIyOTcyZWI3YTllZDhmZWY0NmUxYjYzYjdjMDYwODg1NzAKFwiTsdC_yczGBBCNxu28BhiwFDgCQPEHGgJscSIgZWQwZTJlMTM5MjVmYWEwODJhNmUyNzhjYTU1NmI2ZWI; ssid_ucp_v1=1.0.0-KDNlZWVlZjIyOTcyZWI3YTllZDhmZWY0NmUxYjYzYjdjMDYwODg1NzAKFwiTsdC_yczGBBCNxu28BhiwFDgCQPEHGgJscSIgZWQwZTJlMTM5MjVmYWEwODJhNmUyNzhjYTU1NmI2ZWI; store-region=cn-jx; store-region-src=uid; csrf_session_id=3fcf816bfef09b8d956d403c0f296f52; _tea_utm_cache_576092=undefined"
    })
