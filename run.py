from buxxel import create_app

app = create_app()

def blueprint_view_map(app):
    mapping = {}
    for rule in app.url_map.iter_rules():
        bp, view = rule.endpoint.split('.', 1) if '.' in rule.endpoint else ('main', rule.endpoint)
        mapping.setdefault(bp, []).append((view, rule.rule))
    return mapping



if __name__ == '__main__':
    print(blueprint_view_map(app))
    app.run(debug=True)