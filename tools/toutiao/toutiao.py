from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.toutiao.toutiao_publisher import ToutiaoPublisher

class ToutiaoTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cookies = tool_parameters.get('cookies')
        title = tool_parameters.get('title')
        content = tool_parameters.get('content')
        cover_image = tool_parameters.get('cover_image')
        
        try:
            publisher = ToutiaoPublisher()
            publisher.set_cookies(cookies)
            
            result = publisher.publish_article(
                title=title,
                content=content,
                cover_image=cover_image
            )
            
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"文章《{title}》发布成功",
                    "json": result
                }
            )
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"发布失败：{str(e)}"
                }
            )
            raise e