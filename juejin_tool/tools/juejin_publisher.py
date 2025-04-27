import requests
from typing import Dict, Any, Optional

class JuejinPublisher:
    """掘金发布工具类"""
    
    def __init__(self):
        """初始化"""
        self.session = requests.Session()
        self.cookies_str = ''
        
    def set_cookies(self, cookies: str):
        """设置cookies"""
        self.cookies_str = cookies
        if isinstance(cookies, str):
            for item in cookies.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    self.session.cookies[key] = value
                    
    def create_draft(self, title: str, content: str) -> Dict[str, Any]:
        """创建文章草稿"""
        url = "https://api.juejin.cn/content_api/v1/article_draft/create"
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "cookie": self.cookies_str,
            "referer": "https://juejin.cn/"
        }
        
        params = {
            "aid": "2608",
            "uuid": "7293505961473721866"
        }
        
        data = {
            "category_id": "0",
            "tag_ids": [],
            "link_url": "",
            "cover_image": "",
            "title": title,
            "brief_content": "",
            "edit_type": 10,
            "html_content": "deprecated",
            "mark_content": content,
            "theme_ids": [],
            "pics": []
        }
        
        try:
            response = self.session.post(url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('err_no') != 0:
                raise Exception(result.get('err_msg', '创建草稿失败'))
                
            return result['data']
            
        except Exception as e:
            raise Exception(f"创建草稿失败: {str(e)}")

    def publish_article(self, draft_id: str, word_count: int) -> Dict[str, Any]:
        """发布文章"""
        url = "https://api.juejin.cn/content_api/v1/article/publish"
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "cookie": self.cookies_str,
            "referer": "https://juejin.cn/"
        }
        
        params = {
            "aid": "2608",
            "uuid": "7293505961473721866"
        }
        
        data = {
            "draft_id": draft_id,
            "sync_to_org": False,
            "column_ids": [],
            "theme_ids": [],
            "encrypted_word_count": 1077848,
            "origin_word_count": word_count
        }
        
        try:
            response = self.session.post(url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('err_no') != 0:
                raise Exception(result.get('err_msg', '发布文章失败'))
                
            return result
            
        except Exception as e:
            raise Exception(f"发布文章失败: {str(e)}")

    def update_draft(self, 
                    draft_id: str,
                    title: str,
                    content: str,
                    category_id: str = "6809637767543259144",  # 默认分类
                    column_ids: list = None,  # 专栏ID列表
                    theme_ids: list = None,   # 话题ID列表
                    tag_ids: list = None,     # 标签ID列表
                    brief_content: str = "",
                    cover_image: str = "") -> Dict[str, Any]:
        """更新文章草稿
        Args:
            draft_id: 草稿ID
            title: 文章标题
            content: 文章内容
            category_id: 文章分类ID
            column_ids: 专栏ID列表
            theme_ids: 话题ID列表
            tag_ids: 标签ID列表
            brief_content: 文章简介
            cover_image: 封面图片
        """
        url = "https://api.juejin.cn/content_api/v1/article_draft/update"
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "cookie": self.cookies_str,
            "referer": "https://juejin.cn/"
        }
        
        params = {
            "aid": "2608",
            "uuid": "7293505961473721866"
        }
        
        data = {
            "id": draft_id,
            "category_id": category_id,
            "column_ids": column_ids or [],
            "theme_ids": theme_ids or [],
            "tag_ids": tag_ids or [],
            "link_url": "",
            "cover_image": cover_image,
            "title": title,
            "brief_content": brief_content,
            "edit_type": 10,
            "html_content": "deprecated",
            "mark_content": content,
            "theme_ids": [],
            "pics": []
        }
        
        try:
            response = self.session.post(url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('err_no') != 0:
                raise Exception(result.get('err_msg', '更新草稿失败'))
                
            return result['data']
            
        except Exception as e:
            raise Exception(f"更新草稿失败: {str(e)}") 