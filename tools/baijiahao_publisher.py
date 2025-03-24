import requests
import json
import time
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class BaijiahaoPublisher:
    """百家号发布工具类 - 新版实现"""
    
    def __init__(self):
        """初始化"""
        self.version = '0.0.1'
        self.session = requests.Session()
        self.main_cookies = None  # 存储主认证信息
        self.edit_token = None    # 存储操作token
        
        # 设置基础请求头
        self.session.headers.update({
            'Origin': 'https://baijiahao.baidu.com',
            'Referer': 'https://baijiahao.baidu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def set_main_cookies(self, cookies: str):
        """设置主认证cookies
        
        Args:
            cookies: 完整的cookies字符串
        """
        self.main_cookies_str = cookies  # 保存完整的cookies字符串
        
        # 同时也解析成字典形式
        cookie_dict = {}
        for item in cookies.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        self.main_cookies = cookie_dict
        self.session.cookies.update(cookie_dict)
        
    def refresh_token(self) -> str:
        """刷新认证token"""
        response = self.session.get('https://baijiahao.baidu.com/builder/rc/edit')
        response.raise_for_status()
        
        # 查找 auth token
        mark_str = 'window.__BJH__INIT__AUTH__="'
        auth_start = response.text.find(mark_str)
        if auth_start == -1:
            raise Exception('主认证已失效，请重新设置cookies')
            
        # 修改结束标记的查找方式
        auth_end = response.text.find('",window.user_id=', auth_start)
        if auth_end == -1:
            auth_end = response.text.find('",window.__BJH__EDIT_', auth_start)
        
        if auth_end == -1:
            raise Exception('无法提取token')
            
        self.edit_token = response.text[auth_start + len(mark_str):auth_end]
        
        return self.edit_token
            
    def get_meta_data(self) -> Dict[str, Any]:
        """获取账号元数据"""
        if not self.edit_token:
            self.refresh_token()
            
        url = f'https://baijiahao.baidu.com/builder/app/appinfo?_={int(time.time() * 1000)}'
        
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['errmsg'] != 'success':
            # token可能过期，尝试刷新
            self.refresh_token()
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data['errmsg'] != 'success':
                raise Exception('获取账号信息失败')
                
        account_info = data['data']['user']
        return {
            'uid': account_info['userid'],
            'title': account_info['name'],
            'avatar': account_info['avatar'],
            'type': 'baijiahao',
            'displayName': '百家号',
            'supportTypes': ['html'],
            'home': 'https://baijiahao.baidu.com/',
            'icon': 'https://www.baidu.com/favicon.ico?t=20171027'
        }
            
            
    def _get_auth_token(self) -> str:
        """获取认证 token"""
        response = self.session.get('https://baijiahao.baidu.com/builder/rc/edit')
        response.raise_for_status()
        
        # 查找 auth token
        mark_str = 'window.__BJH__INIT__AUTH__="'
        auth_start = response.text.find(mark_str)
        if auth_start == -1:
            raise Exception('登录已失效')
            
        auth_end = response.text.find('",window.__BJH__EDIT_', auth_start)
        auth_token = response.text[auth_start + len(mark_str):auth_end]
        
        return auth_token
        
        
    def save_article(self,
                            title: str,
                            content: str) -> Dict[str, Any]:
        """保存文章为草稿"""
            
        # 构建表单数据
        form_data = {
            'title': title,
            'content': content,
            'type': 'news'
        }
        
        # 更新请求头
        headers = {
            'Token': self.edit_token,
            'Cookie': self.main_cookies_str,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # 发送请求
        response = self.session.post(
            'https://baijiahao.baidu.com/pcui/article/save?callback=bjhdraft',
            headers=headers,
            cookies=self.main_cookies,
            data=form_data
        )
        response.raise_for_status()
        
        # 处理 jsonp 响应
        text = response.text
        if text.startswith('bjhdraft('):
            text = text[9:-1]

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            raise Exception("解析响应失败")
        
        article_id = result['ret']['article_id']
        return {
            'status': 'success',
            'article_id': article_id,
            'draft_link': f'https://baijiahao.baidu.com/builder/rc/edit?type=news&article_id={article_id}'
        }
    
    def publish_article(self, 
                       article_id: str,
                       title: str, 
                       content: str,
                       cover_images: Optional[List[Dict[str, str]]] = None,
                       activity_list: Optional[List[Dict[str, str]]] = None,
                       source_reprinted_allow: str = "0",
                       cover_layout: str = "one",
                       abstract_from: str = "3",
                       abstract: str = "",
                       isBeautify: str = "false",
                       usingImgFilter: str = "false") -> Dict[str, Any]:
        """
        发布文章接口
        Args:
            article_id: 文章ID
            title: 文章标题
            content: 文章内容
            cover_images: 封面图片列表,格式为[{src: "图片url"}]
            activity_list: 活动列表配置,格式为[{id: "ttv", is_checked: "1"}]
            source_reprinted_allow: 是否允许转载 "0"-不允许 "1"-允许
            cover_layout: 封面布局 "one"-单图 "three"-三图
            abstract_from: 摘要来源 "1"-手动输入 "2"-文章开头 "3"-自动生成
            abstract: 手动输入的摘要内容(当abstract_from="1"时使用)
            isBeautify: 是否美化图片 "true"-是 "false"-否
            usingImgFilter: 是否使用图片滤镜 "true"-是 "false"-否
        """
        url = 'https://baijiahao.baidu.com/pcui/article/publish'
        
        # 默认封面图片
        if not cover_images:
            cover_images = []
        
        # 默认活动列表
        if not activity_list:
            activity_list = [
                {"id": "ttv", "is_checked": "1"},
                {"id": "reward", "is_checked": "1"},
                {"id": "aigc_bjh_status", "is_checked": "0"}
            ]
        
        # 构建封面图片映射
        cover_images_map = []
        for img in cover_images:
            cover_images_map.append({
                "src": img["src"],
                "origin_src": img["src"]
            })
        
        # 构建活动列表参数
        activity_list_params = {}
        for idx, activity in enumerate(activity_list):
            activity_list_params[f"activity_list[{idx}][id]"] = activity["id"]
            activity_list_params[f"activity_list[{idx}][is_checked]"] = activity["is_checked"]
        
        form_data = {
            "type": "news",
            "title": title,
            "content": content,
            "abstract": abstract,
            "len": str(len(content)),
            **activity_list_params,  # 展开活动列表参数
            "source_reprinted_allow": source_reprinted_allow,
            "abstract_from": abstract_from,
            "isBeautify": isBeautify,
            "usingImgFilter": usingImgFilter,
            "cover_layout": cover_layout,
            "cover_images": json.dumps([{
                "src": img["src"],
                "machine_chooseimg": 0,
                "isLegal": 0
            } for img in cover_images]),
            "_cover_images_map": json.dumps(cover_images_map),
            "cover_source": "upload",
            "subtitle": "",
            "bjhtopic_id": "",
            "bjhtopic_info": "",
            "clue": "",
            "bjhmt": "",
            "order_id": "",
            "aigc_rebuild": "",
            "image_edit_point": json.dumps([{
                "img_type": "cover",
                "img_num": {
                    "template": 0,
                    "font": 0,
                    "filter": 0,
                    "paster": 0,
                    "cut": 0,
                    "any": 0
                }
            }, {
                "img_type": "body", 
                "img_num": {
                    "template": 0,
                    "font": 0,
                    "filter": 0,
                    "paster": 0,
                    "cut": 0,
                    "any": 0
                }
            }]),
            "article_id": article_id
        }

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://baijiahao.baidu.com',
            'Referer': f'https://baijiahao.baidu.com/builder/rc/edit?type=news&article_id={article_id}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'Token': self.edit_token
        }

        response = self.session.post(
            url,
            headers=headers,
            cookies=self.main_cookies,
            data=form_data,
            params={'type': 'news', 'callback': 'bjhpublish'}
        )
        
        return response.json()
        
    def upload_image(self, image_source: str, is_url: bool = False) -> List[Dict[str, str]]:
        """上传图片
        
        Args:
            image_source: 图片来源，可以是本地文件路径或URL
            is_url: 是否是URL，默认为False
            
        Returns:
            上传结果列表
        """
        try:
            # 构建基础数据
            data = {
                'type': 'image',
                'app_id': '1589639493090963',
                'is_waterlog': '1',
                'save_material': '1',
                'no_compress': '0',
                'is_events': '',
                'article_type': 'news'
            }
            
            if is_url:
                # 如果是URL，直接使用URL上传
                data['url'] = image_source
                files = None
            else:
                # 如果是本地文件，需要放在项目的 images 目录下
                if not image_source.startswith('images/'):
                    image_source = f'images/{image_source}'
                files = {
                    'media': ('image.jpg', open(image_source, 'rb'), 'image/jpeg')
                }
            
            # 发送请求
            response = self.session.post(
                'https://baijiahao.baidu.com/pcui/picture/uploadproxy',
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            if result['errmsg'] != 'success':
                raise Exception(result['errmsg'])
                
            return [{
                'url': result['ret']['https_url']
            }]
            
        except Exception as e:
            raise Exception(f'上传图片失败: {str(e)}')