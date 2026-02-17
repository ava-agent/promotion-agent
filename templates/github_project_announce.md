# {{ project_name }}

{{ description }}

{% if features %}
## Key Features

{% for feature in features %}
- {{ feature }}
{% endfor %}
{% endif %}

## Getting Started

```bash
{% if install_command %}
{{ install_command }}
{% else %}
git clone {{ github_url }}
{% endif %}
```

Check it out on GitHub: {{ github_url }}

{% if tags %}
Tags: {{ tags | join(', ') }}
{% endif %}
