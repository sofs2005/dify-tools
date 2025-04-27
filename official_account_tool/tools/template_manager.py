import os
from typing import Dict, Any
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from htmlmin import minify

class TemplateManager:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html']),
            # 空白控制相关
            trim_blocks=True,      # 移除块级标签后的第一个换行符
            lstrip_blocks=True,    # 移除块级标签前的空白字符
            keep_trailing_newline=False,  # 不保留末尾换行符
        )
        self.template_configs = {}
        self._load_template_configs()
    
    def _load_template_configs(self):
        """加载所有模板配置"""
        config_path = os.path.join(self.templates_dir, "configs")
        if os.path.exists(config_path):
            for file in os.listdir(config_path):
                if file.endswith(('.yaml', '.yml')):
                    with open(os.path.join(config_path, file), 'r', encoding='utf-8') as f:
                        template_id = file.rsplit('.', 1)[0]
                        self.template_configs[template_id] = yaml.safe_load(f)
    
    def get_template_params(self, template_id: str) -> Dict:
        """获取指定模板所需的参数定义"""
        return self.template_configs.get(template_id, {}).get('parameters', {})
    
    def render_template(self, template_id: str, data: Dict[str, Any]) -> str:
        """渲染模板"""
        template = self.env.get_template(f"{template_id}.html")
        rendered = template.render(**data)
        # 压缩 HTML
        return minify(rendered,
            remove_empty_space=True,      # 移除多余空格
            remove_all_empty_space=False, # 不移除所有空格
            remove_comments=True,         # 移除注释
            remove_optional_attribute_quotes=False  # 保留属性引号
        ) 