from django.db import models
from django.utils import timezone
from datetime import datetime, time
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator


# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
        related_query_name='customuser'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Clinic(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

    def affiliated_doctors(self):
        return self.clinicdoctoraffiliations.count()

    def affiliated_patients(self):
        visit_patients = Patient.objects.filter(visits__clinic=self).distinct()

        appointment_patients = Patient.objects.filter(appointments__clinic=self).distinct()

        affiliated_patients = visit_patients.union(appointment_patients)

        return affiliated_patients.count()


PROCEDURES = [
    ('Cleaning', 'Cleaning'),
    ('Filling', 'Filling'),
    ('Root Canal', 'Root Canal'),
    ('Crown', 'Crown'),
    ('Teeth Whitening', 'Teeth Whitening'),
]


class Procedure(models.Model):
    name = models.CharField(max_length=255, choices=PROCEDURES, unique=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    npi = models.CharField(max_length=10,
                           validators=[RegexValidator(
                               regex=r'^\d{10}$',
                               message='NPI must be exactly 10 digits.',
                               code='invalid_npi'
                           )], unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    specialties = models.ManyToManyField(Procedure)

    def __str__(self):
        return f"{self.name} ({self.npi})"

    def affiliated_clinics(self):
        return self.clinicdoctoraffiliations.count()

    def affiliated_patients(self):
        visit_patients = Patient.objects.filter(visits__doctor=self).distinct()

        appointment_patients = Patient.objects.filter(appointments__doctor=self).distinct()

        affiliated_patients = visit_patients.union(appointment_patients)

        return affiliated_patients.count()


time_regex = [RegexValidator(
                regex=r'^(?:[01]\d|2[0-3]):(00|30)$',
                message="Time must be in the format HH:00 or HH:30.",
                code='invalid_time'
            )]


class ClinicDoctorAffiliation(models.Model):
    clinic = models.ForeignKey(Clinic, related_name='clinicdoctoraffiliations', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='clinicdoctoraffiliations', on_delete=models.CASCADE)
    office_address = models.CharField(max_length=255)

    mon_start_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    mon_end_time = models.CharField(max_length=5, validators=time_regex, blank=True)

    tue_start_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    tue_end_time = models.CharField(max_length=5, validators=time_regex, blank=True)

    wed_start_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    wed_end_time = models.CharField(max_length=5, validators=time_regex, blank=True)

    thu_start_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    thu_end_time = models.CharField(max_length=5, validators=time_regex, blank=True)

    fri_start_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    fri_end_time = models.CharField(max_length=5, validators=time_regex, blank=True)

    sat_start_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    sat_end_time = models.CharField(max_length=5, validators=time_regex, blank=True)

    sun_start_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    sun_end_time = models.CharField(max_length=5, validators=time_regex, blank=True)

    class Meta:
        unique_together = ('clinic', 'doctor')

    def __str__(self):
        return f"{self.doctor.name} at {self.clinic.name} (Office: {self.office_address})"

    def days_times(self):

        schedule = []

        # For each day, check if the start and end times are available, and append them to the list
        if self.mon_start_time != self.mon_end_time:
            schedule.append(f"Mon ({self.mon_start_time} - {self.mon_end_time})")
        if self.tue_start_time != self.tue_end_time:
            schedule.append(f"Tue ({self.tue_start_time} - {self.tue_end_time})")
        if self.wed_start_time != self.wed_end_time:
            schedule.append(f"Wed ({self.wed_start_time} - {self.wed_end_time})")
        if self.thu_start_time != self.thu_end_time:
            schedule.append(f"Thu ({self.thu_start_time} - {self.thu_end_time})")
        if self.fri_start_time != self.fri_end_time:
            schedule.append(f"Fri ({self.fri_start_time} - {self.fri_end_time})")
        if self.sat_start_time != self.sat_end_time:
            schedule.append(f"Sat ({self.sat_start_time} - {self.sat_end_time})")
        if self.sun_start_time != self.sun_end_time:
            schedule.append(f"Sun ({self.sun_start_time} - {self.sun_end_time})")

        return ", ".join(schedule) if schedule else "No working schedule available"


class Patient(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    last_4_ssn = models.CharField(max_length=4)
    gender = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    def last_visit(self):
        last_visit = self.visits.order_by('-visit_date').first()
        if last_visit:
            return last_visit

        return None

    def next_appointment(self):
        # Get the current timezone-aware datetime and split into date and time
        now = timezone.now()
        current_date = now.date()
        current_time = now.time()

        # Filter for future appointments and order by date and time
        appointments = self.appointments.filter(appointment_date__gte=current_date).order_by('appointment_date',
                                                                                             'appointment_time')

        for appointment in appointments:
            # Convert the appointment_time to a time object
            appointment_time = datetime.strptime(appointment.appointment_time,
                                                 '%H:%M').time() if appointment.appointment_time else time(0, 0)

            # If the appointment is today and the time is in the future, return it
            if appointment.appointment_date == current_date:
                if appointment_time >= current_time:  # Check if the time is now or later
                    return appointment
            else:
                return appointment

        return None


class Visit(models.Model):
    patient = models.ForeignKey(Patient, related_name='visits', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='visits', on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, related_name='visits', on_delete=models.CASCADE)
    visit_date = models.DateField()
    procedures_done = models.ForeignKey(Procedure, related_name='visits', on_delete=models.CASCADE)
    doctor_notes = models.TextField()

    def __str__(self):
        return f"Visit: {self.patient.name} with {self.doctor.name}"


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, related_name='appointments', on_delete=models.CASCADE)
    procedure = models.ForeignKey(Procedure, related_name='appointments', on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=5, validators=time_regex, blank=True)
    booked_on = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'appointment_date', 'appointment_time')

    def __str__(self):
        return f"Appointment: {self.patient.name} with {self.doctor.name} on {self.appointment_date}"
