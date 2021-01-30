from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, IncidentSubmitted, Incident, ErrorReport

admin.site.register(User, UserAdmin)


@admin.register(IncidentSubmitted)
class IncidentSubmittedAdmin(admin.ModelAdmin):
    pass


@admin.register(ErrorReport)
class ErrorReportAdmin(admin.ModelAdmin):
    pass


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    exclude = ("search_vector", "phrases")
