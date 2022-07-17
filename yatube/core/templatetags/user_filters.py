from django import template


register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter(name='uglify')
def uglify(value):
    y = ''
    for c in range(len(value)):
        if c % 2 == 0:
            y += value[c].lower()
        else:
            y += value[c].upper()
    return y
