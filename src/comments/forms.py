from django import forms
from django.contrib.auth.models import AnonymousUser

from .models import Comment


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(),
                                   required=False)
    name = forms.CharField(max_length=255,
                           widget=forms.TextInput(
                               attrs={"placeholder": "Name"}
                           ))
    email = forms.EmailField(max_length=255,
                             required=False,
                             widget=forms.TextInput(
                                 attrs={"placeholder": "Email"}
                             ))

    class Meta:
        model = Comment
        fields = ("name", "email", "message")
        widgets = {
            "message": forms.Textarea(attrs={"placeholder": "Message"})
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop("author", None)
        self.post = kwargs.pop("post", None)
        self.parent_id = kwargs.pop("parent_id", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.parent_id:
            try:
                parent = Comment.objects.get(id=self.parent_id)
                self.parent = parent
            except Comment.DoesNotExist:
                raise forms.ValidationError("Comment does not exist")
        else:
            self.parent = None

        if self.parent:
            try:
                self.post.comments.get(id=self.parent.id)
            except Comment.DoesNotExist:
                raise forms.ValidationError("Cannot reply to comment from"
                                            "another page")

        # Make name field non-required if user is logged in and active
        if self.author.is_authenticated and self.author.is_active:
            del self.errors["name"]

    def save(self, commit=True):
        if self.author:
            if not self.author.is_active or isinstance(self.author, AnonymousUser):
                self.author = None
            else:
                self.cleaned_data["name"] = self.author.get_full_name()

        instance = super().save(commit=False)
        instance.post = self.post

        if not self.parent:
            instance = instance.add_root(instance=instance)
        elif self.parent.is_root():
            self.parent.add_child(instance=instance)

        if self.author:
            instance.author = self.author
            if self.author.is_superuser or self.author.is_staff:
                instance.live = True

        instance.save()
