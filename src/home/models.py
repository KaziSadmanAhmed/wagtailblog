from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.db import models

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


from Blog.utils import pagination_generator
from snippets.models import Header, Subheader, Menu


@register_setting
class SiteSettings(BaseSetting):
    header = models.ForeignKey(Header,
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL,
                               help_text="Header to display on homepage")
    subheader = models.ForeignKey(Subheader,
                                  blank=True,
                                  null=True,
                                  on_delete=models.SET_NULL,
                                  help_text="Header to display on child pages")
    main_menu = models.ForeignKey(Menu,
                                  blank=True,
                                  null=True,
                                  help_text="Main navigation menu")
    comment_image = models.ForeignKey(Image,
                                      blank=True,
                                      null=True,
                                      on_delete=models.SET_NULL,
                                      help_text="Default image for comment")
    posts_per_page = models.PositiveIntegerField(default=12)
    pagination_limit = models.PositiveIntegerField(default=5)

    panels = [
        SnippetChooserPanel("header"),
        SnippetChooserPanel("subheader"),
        SnippetChooserPanel("main_menu"),
        ImageChooserPanel("comment_image"),
        MultiFieldPanel([
            FieldPanel("posts_per_page"),
            FieldPanel("pagination_limit")
        ], heading="Pagination")
    ]

    class Meta:
        verbose_name = "Site"


class HomePage(Page):

    def get_context(self, request):

        # Get posts
        PostPage = apps.get_model("posts", "PostPage")
        posts = PostPage.objects.live().reverse()

        # Pagination
        pagination_data = pagination_generator(request, posts)

        # Update template context
        context = super().get_context(request)
        context["query_string"] = request.GET.urlencode()
        context["page"] = pagination_data["page"]
        context["posts_per_page"] = pagination_data["posts_per_page"]
        context["pagination_limit"] = pagination_data["pagination_limit"]
        return context
