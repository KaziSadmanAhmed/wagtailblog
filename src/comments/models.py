from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

from treebeard.mp_tree import MP_Node
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from .managers import CommentManager


class Comment(MP_Node):
    post = ParentalKey("posts.PostPage", related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    message = models.TextField(max_length=2000)
    created = models.DateTimeField(default=timezone.now)
    live = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)

    node_order_by = ("created",)

    objects = CommentManager()

    panels = [
        FieldPanel("post"),
        FieldPanel("parent"),
        FieldPanel("author"),
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("message", classname="full"),
        FieldPanel("live"),
        FieldPanel("flagged")
    ]

    def get_post_with_link(self):
        html = """
                <a href="{}" target="_blank">{}</a>
        """.format(self.post.get_url(), self.post.title)
        return mark_safe(html)
    get_post_with_link.short_description = "Post"
    get_post_with_link.admin_order_field = "post__title"

    def get_name(self):
        if self.author:
            return self.author.get_full_name()
        else:
            return self.name

    # this is just a convenience function to make the names appear with lines
    # eg root | - first child
    def name_with_depth(self):
        depth = "— " * (self.get_depth() - 1)
        return depth + self.get_name()
    name_with_depth.short_description = "Name"

    # another convenience function - just for use in modeladmin index
    def parent_name(self):
        if not self.is_root():
            return self.get_parent().get_name()
        return None

    # Implement maximum depth level of 2
    # Does not work when moving to another node
    # Setting the value of path.max_length did not work
    def save(self, *args, **kwargs):
        if self.get_depth() > 2:
            raise ValidationError("Maximum depth level limit of 2 reached")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_with_depth()
