from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, IncidentSubmitted, Incident

admin.site.register(User, UserAdmin)


@admin.register(IncidentSubmitted)
class IncidentSubmittedAdmin(admin.ModelAdmin):
    pass


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    pass
