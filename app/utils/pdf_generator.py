import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def generate_pdf(data: dict, output_path: str):
    template = env.get_template("report_template.html")
    html_out = template.render(**data, logo_path=os.path.join(STATIC_DIR, 'logo.png'))
    HTML(string=html_out, base_url=STATIC_DIR).write_pdf(output_path)