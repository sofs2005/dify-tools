import json
import requests

class ToutiaoPublisher:
    def __init__(self):
        self.session = requests.Session()
        self.cookies_str = ''
        
    def set_cookies(self, cookies: str):
        """设置 cookies"""
        self.cookies_str = cookies
        if isinstance(cookies, str):
            for item in cookies.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    self.session.cookies[key] = value
    
    
    def upload_image(self, image_url: str) -> dict:
        """上传图片
        Args:
            image_url: 图片URL
        Returns:
            dict: 上传结果
        """
        headers = {
            'cookie': self.cookies_str
        }
        
        # 构建 multipart/form-data 请求体
        data = {
            'imageUrl': image_url
        }
        
        response = self.session.post(
            'https://mp.toutiao.com/spice/image',
            params={
                'upload_source': '20020002',
                'need_enhance': 'true',
                'aid': '1231',
                'device_platform': 'web',
                'scene': 'paste'
            },
            headers=headers,
            data=data
        )
        
        result = response.json()
        if not result.get('data'):
            raise Exception(result.get('message', '图片上传失败'))
            
        return result['data']
    
    def publish_article(self, title: str, content: str, cover_image: str = None) -> dict:
        """发布文章"""
        try:
            # 处理封面图片
            pgc_feed_covers = []
            if cover_image:
                image_result = self.upload_image(cover_image)
                if image_result:
                    pgc_feed_covers.append({
                        'id': 0,
                        'url': image_result['url'],
                        'uri': image_result['web_uri'],
                        'origin_uri': image_result['web_uri'],
                        'ic_uri': '',
                        'thumb_width': image_result.get('width', 0),
                        'thumb_height': image_result.get('height', 0)
                    })
            
            # 发布文章
            response = self.session.post(
                'https://mp.toutiao.com/mp/agw/article/publish',
                params={'source': 'mp', 'type': 'article'},
                data={
                    'title': title,
                    'content': content,
                    'article_ad_type': 2,
                    'article_type': 0,
                    'from_diagnosis': 0,
                    'save': 0,
                    'pgc_id': 0,
                    'pgc_feed_covers': json.dumps(pgc_feed_covers)
                }
            )
            
            result = response.json()
            if not result.get('data'):
                raise Exception(result.get('message', '发布失败'))
                
            return result['data']
            
        except Exception as e:
            raise Exception(f'发布文章失败: {str(e)}')