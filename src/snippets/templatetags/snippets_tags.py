from django import template

from home.models import SiteSettings

register = template.Library()


# Header snippets
@register.inclusion_tag("snippets/header.html", takes_context=True)
def header(context):
    return {
        "header": SiteSettings.for_site(context["request"].site).header,
        "request": context["request"]
    }


# Subheader snippets
@register.inclusion_tag("snippets/subheader.html", takes_context=True)
def subheader(context):
    return {
        "subheader": SiteSettings.for_site(context["request"].site).subheader,
        "request": context["request"]
    }


# Menu snippets
@register.inclusion_tag("snippets/menu.html", takes_context=True)
def menu(context):
    return {
        "menu": SiteSettings.for_site(context["request"].site).main_menu
    }


# Cards snippets
@register.inclusion_tag("snippets/cards.html", takes_context=False)
def cards(posts):
    return {
        "posts": posts
    }


# Sidebar snippets
@register.inclusion_tag("snippets/sidebar.html", takes_context=False)
def sidebar(posts):
    return {
        "posts": posts
    }


# Footer snippets
@register.inclusion_tag("snippets/footer.html", takes_context=False)
def footer():
    pass


# Pagination snippets
@register.inclusion_tag("snippets/pagination.html", takes_context=False)
def pagination(query_string, page, posts_per_page, pagination_limit):
    return {
        "query_string": query_string,
        "page": page,
        "posts_per_page": posts_per_page,
        "pagination_limit": pagination_limit,
        "pagination_limit_neg": pagination_limit * -1
    }
