from django import template
from django.template.defaultfilters import stringfilter

from bs4 import BeautifulSoup
from wagtail.utils.pagination import replace_page_in_query

register = template.Library()


@register.filter
@stringfilter
def replace_page(query_string, page_number):
    return replace_page_in_query(query_string, page_number)


@register.filter
@stringfilter
def update_value(elem, value):
    elem = BeautifulSoup(elem, "lxml").input
    elem.attrs.update({"value": value})
    return elem
