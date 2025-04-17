from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.juejin_publisher import JuejinPublisher

class JuejinTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cookies = tool_parameters.get('cookies')
        title = tool_parameters.get('title')
        content = tool_parameters.get('content')
        category_id = tool_parameters.get('category_id')
        
        # 将逗号分隔的字符串转换为列表
        column_ids = [x.strip() for x in tool_parameters.get('column_ids', '').split(',') if x.strip()]
        theme_ids = [x.strip() for x in tool_parameters.get('theme_ids', '').split(',') if x.strip()]
        tag_ids = [x.strip() for x in tool_parameters.get('tag_ids', '').split(',') if x.strip()]
        
        try:
            publisher = JuejinPublisher()
            publisher.set_cookies(cookies)
            
            # 创建草稿
            draft_result = publisher.create_draft(title=title, content=content)
            draft_id = draft_result['id']
            
            # 更新草稿属性
            publisher.update_draft(
                draft_id=draft_id,
                title=title,
                content=content,
                category_id=category_id,
                column_ids=column_ids,
                theme_ids=theme_ids,
                tag_ids=tag_ids
            )
            
            # 计算文章字数
            word_count = len(content)
            
            # 发布文章
            publish_result = publisher.publish_article(draft_id=draft_id, word_count=word_count)
            
            yield ToolInvokeMessage(
                type="json",
                message={
                    "json_object": publish_result
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