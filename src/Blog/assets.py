from django.conf import settings

from django_assets import Bundle, register
from webassets.filter import get_filter


libsass = get_filter("libsass", style="compressed")

css_libs = Bundle(
    settings.BASE_DIR + "/assets/styles/css/libs/normalize.css",
    filters="cssutils",
    output="css/libs.css"
)

css_custom = Bundle(
    settings.BASE_DIR + "/assets/styles/sass/base.sass",
    filters=libsass,
    output="css/style.css",
    depends="/**/*.sass",

)

register("css_libs", css_libs)
register("css_custom", css_custom)
