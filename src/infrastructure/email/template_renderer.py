from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path

from src.domain.interfaces import IEmailTemplateRenderer
from src.domain.errors import TemplateRenderError

__all__ = ["EmailTemplateRenderer"]


class EmailTemplateRenderer(IEmailTemplateRenderer):
    """Jinja2-based email template renderer"""

    def __init__(self, templates_directory: str | Path):
        """
        Initialize template renderer

        Args:
            templates_directory: Path to directory containing email templates
        """
        self._templates_dir = Path(templates_directory)

        if not self._templates_dir.exists():
            self._templates_dir.mkdir(parents=True, exist_ok=True)

        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=True,
        )

    def render(self, template_name: str, context: dict) -> str:
        """
        Render an email template with context

        Args:
            template_name: Name of the template file (e.g., 'password_reset.html')
            context: Dictionary with template variables

        Returns:
            str: Rendered HTML string

        Raises:
            TemplateRenderError: If template not found or rendering fails
        """
        try:
            template = self._env.get_template(template_name)
            rendered = template.render(**context)
            return rendered
        except TemplateNotFound:
            raise TemplateRenderError(f"Template '{template_name}' not found")
        except Exception as e:
            raise TemplateRenderError(f"Failed to render template: {str(e)}")
