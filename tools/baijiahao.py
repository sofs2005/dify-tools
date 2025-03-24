from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.baijiahao_publisher import BaijiahaoPublisher

class BaijiahaoTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cookies = tool_parameters.get('cookies')
        title = tool_parameters.get('title')
        content = tool_parameters.get('content')
        cover_image = tool_parameters.get('cover_image')
        
        # 获取配置参数
        auto_publish = tool_parameters.get('auto_publish', '1') == '1'
        enable_ttv = tool_parameters.get('enable_ttv', '1') == '1'
        enable_reward = tool_parameters.get('enable_reward', '1') == '1'
        is_aigc = tool_parameters.get('is_aigc', '0') == '1'
        allow_reprint = tool_parameters.get('allow_reprint', '0') == '1'
        cover_layout = tool_parameters.get('cover_layout', 'one')
        
        # 获取新增的图片处理参数
        abstract_from = tool_parameters.get('abstract_from', '3')
        enable_beautify = tool_parameters.get('enable_beautify', 'false')
        enable_filter = tool_parameters.get('enable_filter', 'false')
        
        # 获取摘要相关参数
        abstract = tool_parameters.get('abstract', '')
        
        try:
            # 初始化发布器
            publisher = BaijiahaoPublisher()
            publisher.set_main_cookies(cookies)
            
            # 处理封面图片
            cover_images = []
            if cover_image:
                # 分割图片路径
                image_paths = [p.strip() for p in cover_image.split(',')]
                
                # 根据布局检查图片数量
                if cover_layout == 'three' and len(image_paths) < 3:
                    raise Exception('三图布局需要提供3张图片路径，以逗号分隔')
                elif cover_layout == 'one' and len(image_paths) < 1:
                    raise Exception('单图布局需要提供至少1张图片路径')
                    
                # 上传图片
                for path in image_paths[:3]:  # 最多取前3张
                    images = publisher.upload_image(path)
                    if images:
                        cover_images.append({
                            "src": images[0]["url"],
                            "machine_chooseimg": 0,
                            "isLegal": 0
                        })
            
            # 保存文章
            save_result = publisher.save_article(
                title=title,
                content=content,
                is_original=True
            )
            
            if auto_publish:
                # 发布文章
                result = publisher.publish_article(
                    article_id=save_result['article_id'],
                    title=title,
                    content=content,
                    cover_images=cover_images,
                    activity_list=[
                        {"id": "ttv", "is_checked": "1" if enable_ttv else "0"},
                        {"id": "reward", "is_checked": "1" if enable_reward else "0"},
                        {"id": "aigc_bjh_status", "is_checked": "1" if is_aigc else "0"}
                    ],
                    source_reprinted_allow="1" if allow_reprint else "0",
                    cover_layout=cover_layout,
                    abstract_from=abstract_from,
                    abstract=abstract,
                    isBeautify=enable_beautify,
                    usingImgFilter=enable_filter
                )
                status = "已发布"
            else:
                status = "已保存到草稿箱"
                result = save_result
            
            yield ToolInvokeMessage(
                type="text",
                message={
                    "text": f"文章《{title}》{status}\n文章ID：{result['article_id']}"
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