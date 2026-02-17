# {{ title }}

{{ introduction }}

{% if prerequisites %}
## Prerequisites

{% for prereq in prerequisites %}
- {{ prereq }}
{% endfor %}
{% endif %}

{% if steps %}
## Steps

{% for step in steps %}
### Step {{ loop.index }}: {{ step.title }}

{{ step.content }}

{% endfor %}
{% endif %}

{% if conclusion %}
## Conclusion

{{ conclusion }}
{% endif %}

{% if github_url %}
Full source code: {{ github_url }}
{% endif %}
