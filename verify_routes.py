#!/usr/bin/env python3
"""Quick script to verify Flask routes are correctly configured"""

from timeapp import create_app

app = create_app()

print("=" * 60)
print("REGISTERED ROUTES")
print("=" * 60)

routes = []
for rule in app.url_map.iter_rules():
    methods = rule.methods if rule.methods else set()
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(sorted(methods - {'HEAD', 'OPTIONS'})),
        'path': str(rule)
    })

# Sort by path
routes.sort(key=lambda x: x['path'])

for route in routes:
    print(f"{route['path']:30} -> {route['endpoint']:30} [{route['methods']}]")

print("=" * 60)
print(f"Total routes: {len(routes)}")
print("=" * 60)
