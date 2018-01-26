from wagtail.wagtailusers.forms import UserEditForm, UserCreationForm
from wagtail.wagtailimages.widgets import AdminImageChooser


class AuthorEditForm(UserEditForm):
    profile_image = AdminImageChooser()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_image"].widget = AdminImageChooser()


class AuthorCreationForm(UserCreationForm):
    profile_image = AdminImageChooser()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_image"].widget = AdminImageChooser()
