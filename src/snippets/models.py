from django.db import models

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.wagtailcore.models import Orderable
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


@register_snippet
class Menu(ClusterableModel):
    name = models.CharField(max_length=50)

    panels = [
        FieldPanel("name"),
        InlinePanel("items", label="Items")
    ]

    def __str__(self):
        return self.name


class MenuItem(Orderable, models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=1000)
    menu = ParentalKey(Menu,
                       on_delete=models.CASCADE,
                       related_name="items")

    def __str__(self):
        return self.name


@register_snippet
class Header(models.Model):
    image = models.OneToOneField(
                Image,
                null=True,
                blank=True,
                on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)

    panels = [
        ImageChooserPanel("image"),
        FieldPanel("title"),
        FieldPanel("subtitle")
    ]

    def __str__(self):
        return "{} - {}".format(self.title, self.subtitle)


@register_snippet
class Subheader(models.Model):
    image = models.OneToOneField(
                Image,
                null=True,
                blank=True,
                on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)

    panels = [
        ImageChooserPanel("image"),
        FieldPanel("title"),
        FieldPanel("subtitle")
    ]

    def __str__(self):
        return "{} - {}".format(self.title, self.subtitle)
