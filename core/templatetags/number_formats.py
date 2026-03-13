from django import template
from django.utils.formats import number_format

register = template.Library()


@register.filter
def moeda_br(value):
    if value in (None, ""):
        return "-"
    return number_format(value, decimal_pos=2, use_l10n=True, force_grouping=True)
