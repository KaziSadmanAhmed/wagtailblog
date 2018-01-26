from django import forms

from wagtail.wagtailadmin.forms import WagtailAdminModelForm
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Comment


class CommentAdminForm(WagtailAdminModelForm):

    # build a parent field that will show the available topics
    parent = forms.ModelChoiceField(
        required=False,
        empty_label="",
        queryset=Comment.objects.none(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]

        self.fields["parent"].queryset = Comment.objects.exclude(pk=instance.pk)
        self.fields["parent"].initial = instance.get_parent()

    def save(self, commit=True):
        parent = self.cleaned_data["parent"]
        instance = super().save(commit=False)

        is_new = instance.id is None
        is_root = False

        if not parent:
            is_root = True
        elif is_new and Comment.objects.count() == 0:
            is_root = True
        elif not is_new and instance.is_root():
            is_root = True

        # saving / creating
        if is_root and is_new and commit:
            # adding the root
            instance = Comment.add_root(instance=instance)
        elif is_new and commit:
            # adding a new child under the seleced parent
            instance = parent.add_child(instance=instance)
        elif not is_new and instance.get_parent() != parent and commit:
            # moving the instance to under a new parent, editing existing node
            # must use "sorted-child" - will base sorting on node_order_by
            instance.move(parent, pos="sorted-child")
        elif commit:
            # no moving required, just save
            instance.save()

        return instance


# tell Wagtail to use our form class override
Comment.base_form_class = CommentAdminForm


class CommentAdmin(ModelAdmin):
    model = Comment
    menu_icon = "plus"
    menu_order = 300
    list_display = ("get_post_with_link",
                    "author",
                    "name_with_depth",
                    "email",
                    "message",
                    "created",
                    "live",
                    "flagged")
    search_fields = ("name", "email", "message")


modeladmin_register(CommentAdmin)
