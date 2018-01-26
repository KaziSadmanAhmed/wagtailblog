from django import forms

from wagtail.wagtailadmin.forms import WagtailAdminModelForm
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Topic


class TopicAdminForm(WagtailAdminModelForm):

    # build a parent field that will show the available topics
    parent = forms.ModelChoiceField(
        required=False,
        empty_label="",
        queryset=Topic.objects.none(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]

        self.fields["parent"].queryset = Topic.objects.exclude(pk=instance.pk)
        self.fields["parent"].initial = instance.get_parent()

    def save(self, commit=True):
        parent = self.cleaned_data["parent"]
        instance = super().save(commit=False)

        is_new = instance.id is None
        is_root = False

        if not parent:
            is_root = True
        elif is_new and Topic.objects.count() == 0:
            is_root = True
        elif not is_new and instance.is_root():
            is_root = True

        # saving / creating
        if is_root and is_new and commit:
            # adding the root
            instance = Topic.add_root(instance=instance)
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
Topic.base_form_class = TopicAdminForm


class TopicAdmin(ModelAdmin):
    model = Topic
    menu_icon = "folder-inverse"
    menu_order = 200
    add_to_settings_menu = False
    list_display = ("name_with_depth", "parent_name")
    search_fields = ("name",)


modeladmin_register(TopicAdmin)
