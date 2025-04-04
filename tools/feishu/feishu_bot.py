import requests
import json

class FeishuBot:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
    
    def get_tenant_access_token(self):
        """获取 tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()["tenant_access_token"]
    
    def send_message(self, receive_id, content, msg_type="text", receive_id_type="user_id"):
        """发送消息"""
        if not self.tenant_access_token:
            self.tenant_access_token = self.get_tenant_access_token()
            
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.tenant_access_token}"
        }
        
        if msg_type == "text":
            content = json.dumps({"text": content})
            
        params = {
            "receive_id_type": receive_id_type
        }
        
        data = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }
        
        response = requests.post(url, headers=headers, params=params, json=data)
        return response.json()