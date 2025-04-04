import json
from collections.abc import Generator
from typing import Any
from tools.wechat.template.template_manager import TemplateManager

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TemplateTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_manager = TemplateManager()

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        template_id = tool_parameters.get('template_id')
        template_params_str = tool_parameters.get('template_params')
        
        try:
            template_params_str = template_params_str.replace('\\', '')

            # 解析 JSON 字符串为字典
            template_params = json.loads(template_params_str)
            
            # 使用解析后的参数进行渲染
            result = self.template_manager.render_template(template_id, template_params)
            
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": result,
                    "json": result
                }
            )
        except json.JSONDecodeError as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"JSON 解析失败：{str(e)}"
                }
            )
            raise e
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"渲染失败：{str(e)}"
                }
            )
            raise e
