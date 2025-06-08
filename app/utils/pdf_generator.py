import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def generate_pdf(data: dict, output_path: str):
    """
    Render an HTML template with the provided data and export it as a PDF.

    Args:
        data (dict): A dictionary of values to inject into the template.
        output_path (str): Full path where the generated PDF will be saved.

    Raises:
        jinja2.TemplateNotFound: If the specified template does not exist.
        weasyprint.WeasyPrintError: If PDF generation fails.
    """
    # Load the template file
    template = env.get_template("report_template.html")

    # Render HTML with dynamic data and logo path
    html_out = template.render(
        **data,
        logo_path=os.path.join(STATIC_DIR, 'logo.png')
    )

    # Generate and write the PDF to the specified file
    HTML(string=html_out, base_url=STATIC_DIR).write_pdf(output_path)