from django.contrib.gis import admin
from quakes.models import *


class QuakeAdmin(admin.OSMGeoAdmin):
    list_display = ('src', 'eqid', 'version', 'datetime', 'magnitude', 'depth', 'nst', 'region')

admin.site.register(Quake, QuakeAdmin)
