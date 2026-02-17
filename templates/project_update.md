# {{ project_name }} - {{ version }}

{{ summary }}

{% if changes %}
## What's New

{% for change in changes %}
- {{ change }}
{% endfor %}
{% endif %}

{% if migration_notes %}
## Migration Notes

{{ migration_notes }}
{% endif %}

GitHub: {{ github_url }}
