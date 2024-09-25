from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("home", views.home, name="home"),

    path("clinics", views.clinics, name="clinics"),
    path("add_clinic", views.add_clinic, name="add_clinic"),
    path("clinics/<int:id>", views.clinics_details, name="clinics_details"),
    path("edit_clinic/<int:id>", views.edit_clinic_details, name="edit_clinic_details"),
    path("add_clinic_aff_doc/<int:id>", views.add_clinic_aff_doc, name="add_clinic_aff_doc"),
    path("edit_clinic_aff_doc/<int:clinic_id>/<int:id>", views.edit_clinic_aff_doc, name="edit_clinic_aff_doc"),
    path("delete_clinic_aff_doc/<int:clinic_id>/<int:id>", views.delete_clinic_aff_doc, name="delete_clinic_aff_doc"),

    path("doctors", views.doctors, name="doctors"),
    path("add_doctor", views.add_doctor, name="add_doctor"),
    path("doctors/<int:id>", views.doctor_details, name="doctors_details"),
    path("edit_doctor/<int:id>", views.edit_doctor_details, name="edit_doctor_details"),

    path("patients", views.patients, name="patients"),
    path("add_patient", views.add_patient, name="add_patient"),
    path("patients/<int:id>", views.patient_details, name="patient_details"),
    path("edit_patient/<int:id>", views.edit_patient_details, name="edit_patient_details"),

    path("add_appointment/<int:id>", views.add_appointment, name="add_appointment"),

    path("add_visit/<int:id>", views.add_visit, name="add_visit"),

    path("get_blocked_times/<int:doctorId>/<int:clinicId>/<int:procedureId>", views.get_blocked_times, name="get_blocked_times"),
    path('get_clinics_by_procedure/<int:procedureId>/', views.get_clinics_by_procedure,name='get_clinics_by_procedure'),
    path('get_doctors_by_clinic/<int:clinicId>/<int:procedureId>/', views.get_doctors_by_clinic,name='get_doctors_by_clinic'),

    path("home", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("logout", views.logout, name="logout"),

    path('api/add_patient/', views.add_patient_api, name='add-patient'),
    path('api/add_doctor/', views.add_doctor_api, name='add-doctor'),
    path('api/add_clinic/', views.add_clinic_api, name='add-clinic'),
    path('api/get_clinic/<int:clinic_id>/', views.get_clinic_api, name='get-clinic'),
]