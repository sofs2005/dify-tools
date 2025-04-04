from collections.abc import Generator
from typing import Any
import asyncio
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.jimeng.jimeng_generator import generate_image

class JimengTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        cookie = tool_parameters.get('cookie', '')
        prompt = tool_parameters.get('prompt', '')
        model = tool_parameters.get('model', 'jimeng-2.1')
        negative_prompt = tool_parameters.get('negative_prompt', '')
        width = int(tool_parameters.get('width', 1024))
        height = int(tool_parameters.get('height', 1024))
        sample_strength = float(tool_parameters.get('sample_strength', 0.75))
        
        try:
            # 使用 asyncio.run 运行异步函数
            result = asyncio.run(generate_image(
                cookie=cookie,
                prompt=prompt,
                model=model,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                sample_strength=sample_strength
            ))
            
            yield ToolInvokeMessage(
                type="json",
                message={
                    "json_object": {
                        "urls": result
                    }
                }
            )
            
        except Exception as e:
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"生成失败：{str(e)}"
                }
            )
            raise e 