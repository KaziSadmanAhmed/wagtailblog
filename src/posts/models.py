from django.db import models
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from treebeard.mp_tree import MP_Node

from wagtail.wagtailcore.models import Page
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailimages.models import Image
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from Blog.utils import pagination_generator
from comments.forms import CommentForm


class Topic(MP_Node):
    """
        Topics can be nested and ordered.
        Root (id 1) cannot be deleted, can be edited.
        User should not edit path, depth, numchild directly.
    """

    name = models.CharField(max_length=30, unique=True)

    # any other fields for the Topic/Category can go here
    # eg. slug, date, description

    # may need to rework node_order_by to be orderable
    # careful - cannot change after initial data is set up
    node_order_by = ("name",)

    panels = [
        FieldPanel("name"),
        FieldPanel("parent")
        # parent is not a field on the model,
        # it is built in the TopicAdminForm form class
    ]

    # this is just a convenience function to make the names appear with lines
    # eg root | - first child
    def name_with_depth(self):
        depth = "— " * (self.get_depth() - 1)
        return depth + self.name
    name_with_depth.short_description = "Name"

    # another convenience function - just for use in modeladmin index
    def parent_name(self):
        if not self.is_root():
            return self.get_parent().name
        return None

    def __str__(self):
        return self.name_with_depth()


class Tag(TaggedItemBase):
    content_object = ParentalKey("PostPage", related_name="posts")


class PostPage(Page):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    image = models.ForeignKey(
                Image,
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name="posts")

    content = RichTextField(blank=True)
    text = models.TextField(blank=True)
    read_time = models.PositiveIntegerField(blank=True, null=True)
    topic = models.ForeignKey(Topic,
                              blank=True,
                              null=True,
                              related_name="posts",
                              on_delete=models.SET_NULL)
    tags = ClusterTaggableManager(through=Tag, blank=True)

    search_fields = Page.search_fields + [
                        index.SearchField("title"),
                        index.SearchField("text")
                    ]

    content_panels = Page.content_panels + [
                        ImageChooserPanel("image"),
                        FieldPanel("content", classname="full"),
                        MultiFieldPanel([
                            FieldPanel("tags"),
                            FieldPanel("topic")
                        ], heading="Meta"),
                        # InlinePanel does not get the base_class_form
                        # InlinePanel("comments", label="Comments")
                    ]

    def get_read_time(self):
        if self.read_time < 1:
            return "less than 1 minute"
        else:
            return "{} minutes".format(self.read_time)

    def get_context(self, request):
        posts = PostPage.objects.live()[:10].reverse()
        context = super().get_context(request)
        context["posts"] = posts
        context["comment_form"] = CommentForm()
        return context

    def serve(self, request):
        if request.method == "POST":
            comment_form = CommentForm(request.POST,
                                       author=request.user,
                                       post=self,
                                       parent_id=request.POST.get("parent_id"))
            # Redirect to page using GET if success
            if comment_form.is_valid():
                comment_form.save()
                return redirect(request.path)

            # Overwrite the context with the current one if fails
            # and render with the context
            # Need to add messages framework and better error display
            # or just make the whole commenting client-side with ajax w/ api
            context = self.get_context(request)
            context["comment_form"] = comment_form
            return render(request, self.get_template(request), context)

        return super().serve(request)


class TopicIndexPage(RoutablePageMixin, Page):

    @route(r"^$")
    def index(self, request):
        # Raise 404 if not topic supplied
        raise Http404

    @route(r"^(?P<topic_query>\w+)/$")
    def topic_index(self, request, topic_query):
        # Get topic and posts
        topic = get_object_or_404(Topic, name=topic_query)
        posts = []
        for i in Topic.get_annotated_list(topic):
            for j in i[0].posts.all():
                posts.append(j)

        # Pagination
        pagination_data = pagination_generator(request, posts)

        # Update template context
        context = {
            "self": self,
            "posts": posts
        }

        context["query_string"] = request.GET.urlencode()
        context["query"] = topic_query
        context["page"] = pagination_data["page"]
        context["posts_per_page"] = pagination_data["posts_per_page"]
        context["pagination_limit"] = pagination_data["pagination_limit"]

        return render(request, self.template, context)


class TagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag_query = request.GET.get("q")

        if tag_query:
            posts = PostPage.objects.live().filter(
                                                tags__name=tag_query
                                            ).reverse()
        else:
            posts = PostPage.objects.none()

        # Pagination
        pagination_data = pagination_generator(request, posts)

        # Update template context
        context = super().get_context(request)
        context["query_string"] = request.GET.urlencode()
        context["query"] = tag_query
        context["page"] = pagination_data["page"]
        context["posts_per_page"] = pagination_data["posts_per_page"]
        context["pagination_limit"] = pagination_data["pagination_limit"]
        return context


class SearchPage(Page):

    def get_context(self, request):

        # Search query
        search_query = request.GET.get("q")

        if search_query:
            posts = PostPage.objects.live().reverse().search(search_query)
        else:
            posts = PostPage.objects.none()

        # Pagination
        pagination_data = pagination_generator(request, posts)

        # Update template context
        context = super().get_context(request)
        context["query_string"] = request.GET.urlencode()
        context["query"] = search_query
        context["search_query"] = search_query
        context["page"] = pagination_data["page"]
        context["posts_per_page"] = pagination_data["posts_per_page"]
        context["pagination_limit"] = pagination_data["pagination_limit"]
        return context
