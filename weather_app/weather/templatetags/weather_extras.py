from django import template

register = template.Library()


@register.filter
def wind_direction(degree):
    if degree is None:
        return '—'
    dirs = ['С', 'С-В', 'В', 'Ю-В', 'Ю', 'Ю-З', 'З', 'С-З']
    ix = int((float(degree) + 22.5) / 45) % 8
    return dirs[ix]
