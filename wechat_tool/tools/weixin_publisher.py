import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class WeixinPublisher:
    def __init__(self, app_id: str, app_secret: str, token_service_url: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_service_url = token_service_url

    def ensure_access_token(self) -> str:
        """从服务获取access_token"""
        try:
            # 构建请求参数
            params = {
                'app_id': self.app_id,
                'app_secret': self.app_secret
            }
            
            # 发送请求
            response = requests.get(
                self.token_service_url,
                params=params,
                timeout=10  # 设置超时时间
            )
            
            # 检查响应状态码
            if response.status_code != 200:
                raise ValueError(f"Token服务响应错误: HTTP {response.status_code}")
            
            data = response.json()
            
            if not data.get('access_token'):
                raise ValueError(f"获取access_token失败: {data}")
            
            return data['access_token']
            
        except requests.exceptions.Timeout:
            raise ValueError("Token服务请求超时")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Token服务请求失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"调用token服务失败: {str(e)}")

    def process_content_images(self, content: str) -> str:
        """处理文章内容中的图片"""
        import re
        img_regex = r'<img[^>]+src="([^"]+)"[^>]*>'
        processed_content = content
        
        for match in re.finditer(img_regex, content):
            original_url = match.group(1)
            try:
                new_url = self.upload_content_image(original_url)
                processed_content = processed_content.replace(original_url, new_url)
            except Exception as e:
                print(f"处理文章内图片失败: {str(e)}")
                continue
                
        return processed_content

    def upload_content_image(self, image_url: str) -> str:
        """上传文章内容图片"""
        token = self.ensure_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        
        # 下载图片
        img_response = requests.get(image_url)
        img_data = img_response.content
        
        # 上传图片
        files = {
            'media': ('image.jpg', img_data, 'image/jpeg')
        }
        response = requests.post(url, files=files)
        result = response.json()
        
        if 'url' not in result:
            raise ValueError(f"上传图片失败: {json.dumps(result)}")
        
        return result['url']

    def upload_image(self, image_url: Optional[str]) -> Optional[str]:
        """上传封面图片（永久素材）"""
        if not image_url:
            return "SwCSRjrdGJNaWioRQUHzgF68BHFkSlb_f5xlTquvsOSA6Yy0ZRjFo0aW9eS3JJu_"
            
        token = self.ensure_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
        
        # 下载图片
        img_response = requests.get(image_url)
        img_data = img_response.content
        
        # 上传图片
        files = {
            'media': ('image.jpg', img_data, 'image/jpeg')
        }
        response = requests.post(url, files=files)
        result = response.json()
        
        if 'media_id' not in result:
            raise ValueError(f"上传图片失败: {json.dumps(result)}")
        
        return result['media_id']

    def publish_article(self, title: str, content: str, image_url: Optional[str] = None,
                       need_open_comment: int = 0, only_fans_can_comment: int = 0,
                       content_source_url: str = "", auto_publish: bool = False) -> Dict[str, Any]:
        """发布文章到微信公众号"""
        try:
            # 1. 上传封面图片
            thumb_media_id = self.upload_image(image_url)
            
            # 2. 处理文章内容中的图片
            processed_content = self.process_content_images(content)
            
            # 3. 生成摘要
            digest = content[:120] if len(content) > 120 else content
            
            # 4. 上传草稿
            media_id = self.upload_draft(
                title, processed_content, digest, thumb_media_id,
                need_open_comment, only_fans_can_comment, content_source_url
            )
            
            # 5. 如果选择自动发布，则发布文章
            if auto_publish:
                publish_id = self.publish_draft(media_id)
                
                # 6. 轮询检查发布状态
                is_published = False
                for _ in range(10):
                    time.sleep(3)
                    is_published = self.get_publish_status(publish_id)
                    if is_published:
                        break
                        
                if not is_published:
                    raise ValueError("发布超时或失败")
            
            return {
                "weixin_media_id": media_id,
                "publish_url": f"https://mp.weixin.qq.com/s/{media_id}",
                "publish_platform": "weixin",
                "publish_time": datetime.now().isoformat(),
                "is_draft": not auto_publish
            }
            
        except Exception as e:
            raise Exception(f"微信发布失败: {str(e)}")

    def upload_draft(self, title: str, content: str, digest: str, thumb_media_id: Optional[str], 
                    need_open_comment: int = 0, only_fans_can_comment: int = 0, 
                    content_source_url: str = "") -> str:
        """上传草稿"""
        token = self.ensure_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        
        articles = [{
            "title": title,
            "author": "AI助手",
            "digest": digest,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": need_open_comment,
            "only_fans_can_comment": only_fans_can_comment,
            "content_source_url": content_source_url
        }]
        
        response = requests.post(
            url, 
            data=json.dumps({"articles": articles}, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        data = response.json()
        
        if data.get("errcode"):
            raise ValueError(f"上传草稿失败: {data.get('errmsg')}")
        return data["media_id"]

    def publish_draft(self, media_id: str) -> str:
        """发布草稿箱中的文章"""
        token = self.ensure_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"
        
        response = requests.post(url, json={"media_id": media_id})
        data = response.json()
        
        if data.get("errcode"):
            raise ValueError(f"发布文章失败: {data.get('errmsg')}")
        
        return data["publish_id"]

    def get_publish_status(self, publish_id: str) -> bool:
        """查询发布状态"""
        token = self.ensure_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={token}"
        
        response = requests.post(url, json={"publish_id": publish_id})
        data = response.json()
        
        if data.get("errcode"):
            raise ValueError(f"查询发布状态失败: {data.get('errmsg')}")
        
        # publish_status: 0:发布中，1:发布成功，2:发布失败，3:已删除
        return data.get("publish_status") == 1 