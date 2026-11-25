"""Keep repeated Thebe initialization from declaring the same JS constants twice."""


def prepare_page(app, pagename, templatename, context, doctree):
    seen = set()
    scripts = []
    for script in context.get('script_files', []):
        body = getattr(script, 'attributes', {}).get('body', '') or ''
        if 'const THEBE_JS_URL' in body:
            if body in seen:
                continue
            seen.add(body)
        scripts.append(script)
    context['script_files'] = scripts


def setup(app):
    app.connect('html-page-context', prepare_page, priority=999)
    return {'version': '1.0', 'parallel_read_safe': True, 'parallel_write_safe': True}
