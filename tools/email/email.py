from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.email.email_sender import EmailSender

class EmailTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = tool_parameters.get('api_key')
        from_email = tool_parameters.get('from_email')
        to_email = tool_parameters.get('to_email')
        subject = tool_parameters.get('subject')
        content = tool_parameters.get('content')
        
        try:
            sender = EmailSender(api_key)
            result = sender.send_email(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                content=content
            )
            
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"邮件发送成功",
                    "json": result
                }
            )
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"发送失败：{str(e)}"
                }
            )
            raise e