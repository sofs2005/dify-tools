from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .weixin_publisher import WeixinPublisher

class WeChatTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        title = tool_parameters.get('title')
        content = tool_parameters.get('content')
        image_url = tool_parameters.get('image_url')
        app_id = tool_parameters.get('wechat_app_id')
        app_secret = tool_parameters.get('wechat_app_secret')
        
        # 获取新增的参数，使用默认值
        need_open_comment = int(tool_parameters.get('need_open_comment', '0'))
        only_fans_can_comment = int(tool_parameters.get('only_fans_can_comment', '0'))
        auto_publish = bool(tool_parameters.get('auto_publish', '0') == '1')
        content_source_url = tool_parameters.get('content_source_url', '')
        
        try:
            publisher = WeixinPublisher(app_id, app_secret)
            result = publisher.publish_article(
                title=title,
                content=content,
                image_url=image_url,
                need_open_comment=need_open_comment,
                only_fans_can_comment=only_fans_can_comment,
                content_source_url=content_source_url,
                auto_publish=auto_publish
            )
            
            status = "已发布" if not result.get('is_draft') else "已保存到草稿箱"
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"文章《{title}》{status}\n文章ID：{result['weixin_media_id']}"
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