from django.conf.urls.defaults import *
from quakes.views import earthquakes, earthquake_display


urlpatterns = patterns('',
    (r'^json/$', earthquakes),

    (r'^', earthquake_display),
)
