from django.contrib.auth.models import AbstractUser
from django.db import models

from wagtail.wagtailimages.models import Image


class Author(AbstractUser):
    profile_image = models.ForeignKey(Image,
                                      blank=True,
                                      null=True,
                                      on_delete=models.SET_NULL)

    def __str__(self):
        return self.username
