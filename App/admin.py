from django.contrib import admin
from .models import Clinic, Doctor, ClinicDoctorAffiliation, Patient, Visit, Appointment, CustomUser
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# Register your models here.


class CustomUserAdmin(UserAdmin):

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Clinic)
admin.site.register(Doctor)
admin.site.register(ClinicDoctorAffiliation)
admin.site.register(Patient)
admin.site.register(Visit)
admin.site.register(Appointment)
