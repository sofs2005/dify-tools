import os
from typing import Dict, Any
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateManager:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html'])
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
        return template.render(**data) 