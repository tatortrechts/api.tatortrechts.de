from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, IncidentSubmitted, Incident, ErrorReport

admin.site.register(User, UserAdmin)


@admin.register(IncidentSubmitted)
class IncidentSubmittedAdmin(admin.ModelAdmin):
    list_display = ("title", "location_input", "date")


@admin.register(ErrorReport)
class ErrorReportAdmin(admin.ModelAdmin):
    list_display = ("description", "email", "incident")


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    exclude = ("search_vector", "phrases")
