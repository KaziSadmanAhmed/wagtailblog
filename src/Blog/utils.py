from wagtail.utils.pagination import paginate

from django.apps import apps


def pagination_generator(request, posts):
    SiteSettings = apps.get_model("home", "SiteSettings")
    posts_per_page = SiteSettings.for_site(request.site).posts_per_page
    pagination_limit = SiteSettings.for_site(request.site).pagination_limit

    paginator, page = paginate(request, posts, per_page=posts_per_page)

    return {
        "paginator": paginator,
        "page": page,
        "posts_per_page": posts_per_page,
        "pagination_limit": pagination_limit
    }
