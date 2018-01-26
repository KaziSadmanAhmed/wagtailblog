from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from vizhash import Vizhash
from io import BytesIO
from bs4 import BeautifulSoup

from wagtail.wagtailimages.models import Image
from wagtail.wagtailcore import hooks

from .models import PostPage


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def generate_photo(request, page):
    if isinstance(page, PostPage) and not page.photo:
        im = Vizhash(page.title, 64).identicon()
        buffer = BytesIO()
        im.save(fp=buffer, format="PNG")
        content_file = ContentFile(buffer.getvalue())
        image_file = InMemoryUploadedFile(
            content_file,
            None,
            page.title,
            "image/png",
            content_file.tell,
            len(buffer.getvalue()),
            None)
        image = Image(
            title=page.title,
            file=image_file,
            width=im.width,
            height=im.height,
            created_at=page.created,
            file_size=len(buffer.getvalue()))
        image.save()
        page.photo = image
        page.save()


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def strip_tags(request, page):
    if isinstance(page, PostPage):
        soup = BeautifulSoup(page.content, "lxml")

        for p in soup.find_all("p"):
            p.replace_with(p.text + " ")

        text = " ".join(soup.text.replace("\n", " ").replace("\t", " ").split())
        page.text = text
        page.save()


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def gen_read_time(request, page):
    if isinstance(page, PostPage):
        AVG_READ_TIME = 200  # wpm
        words = len(page.text.split())
        read_time = round(words / AVG_READ_TIME)
        page.read_time = read_time
        page.save()
