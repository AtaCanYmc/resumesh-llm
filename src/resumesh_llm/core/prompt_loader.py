import os

from jinja2 import Template

from resumesh_llm.core.exceptions import ConfigurationError


class PromptLoader:
    """Helper service to dynamically load and render prompt templates using Jinja2.

    Prompts are stored inside the package structure under 'prompts/' to allow
    independent versioning and editing of prompt text files.
    """

    @staticmethod
    def load_and_render(domain: str, template_name: str, **kwargs) -> str:
        """Loads a prompt template text file and renders it using the provided keyword arguments.

        Args:
            domain: Sub-folder name representing the domain (e.g. 'github', 'rxresume').
            template_name: Basename of the template (e.g. 'summarize_repo_user').
            kwargs: Values to render inside the template using Jinja2 syntax.

        Returns:
            The rendered prompt string.

        Raises:
            ConfigurationError: If the template file cannot be found or read.
        """
        # Resolve package directories
        core_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.dirname(core_dir)
        template_path = os.path.join(
            package_dir, "prompts", domain, f"{template_name}.txt"
        )

        if not os.path.exists(template_path):
            raise ConfigurationError(
                f"Prompt template file could not be found at path: '{template_path}'"
            )

        try:
            with open(template_path, encoding="utf-8") as f:
                content = f.read()

            template = Template(content)
            return template.render(**kwargs)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load or render prompt template '{template_name}': {str(e)}"
            ) from e
