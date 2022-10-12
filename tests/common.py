from jinja2 import BaseLoader, Environment


def mock_apply_template_on_contents(contents, template, context, *_, **__):
    """Mock apply_template_on_contents with real jinja."""
    assert template == "jinja"
    loader = Environment(loader=BaseLoader)
    template = loader.from_string(contents)
    return template.render(**context)


def mock_get_file_str(template_name, *_, **__):
    """Remove salt:// prefix in path file."""
    template_name = template_name[7:]
    with open(template_name, encoding="utf-8") as fd:
        content = fd.read()
        return content
