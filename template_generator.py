def fill_template(template_path, context):
    with open(template_path, 'r') as file:
        content = file.read()
    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content
