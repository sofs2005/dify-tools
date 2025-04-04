from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.feishu.feishu_bot import FeishuBot

class FeishuTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        app_id = tool_parameters.get('app_id')
        app_secret = tool_parameters.get('app_secret')
        user_id = tool_parameters.get('user_id')
        message = tool_parameters.get('message')
        
        try:
            bot = FeishuBot(app_id, app_secret)
            result = bot.send_message(user_id, message)
            
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"消息发送成功",
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