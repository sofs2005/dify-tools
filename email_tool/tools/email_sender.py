import resend

class EmailSender:
    def __init__(self, api_key):
        resend.api_key = api_key
    
    def send_email(self, from_email, to_email, subject, content, html_content=None):
        """发送邮件"""
        params = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "text": content,
        }
        
        if html_content:
            params["html"] = html_content
            
        response = resend.Emails.send(params)
        return response