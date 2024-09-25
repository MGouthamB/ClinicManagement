from django.shortcuts import render, redirect
from .models import Clinic, Doctor, ClinicDoctorAffiliation, Procedure, Patient, Visit, Appointment
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth import login as user_login
from django.contrib.auth import logout as user_logout
from django.contrib.auth.decorators import login_required

# For Rest APIs

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ClinicSerializer, DoctorSerializer, PatientSerializer

# Create your views here.


def check_message(request):
    """
    A generic function to check if there are any messages
    which are forwarded from previous page to display in the current page
    """

    msg = ""

    if "message" in request.session:
        msg, request.session["message"] = request.session["message"], ""

    return msg


@login_required
def home(request):
    """
    Displays Home Page.
    """

    return render(request, "home.html")


@login_required
def clinics(request):
    """
    Displays Clinics List Page.
    """

    clinics_obj = Clinic.objects.all()
    return render(request, "clinics.html", {'clinics': clinics_obj})


@login_required
def add_clinic(request):
    """
    If the request is a GET method, function displays a form page to add Clinic.
    If the request is a POST method, function submits the details to add Clinic and stores in Data Base.
    """

    msg = check_message(request)
    if request.method == 'POST':
        try:
            clinic = Clinic()
            clinic.name = request.POST["name"]
            clinic.email = request.POST["email"]
            clinic.phone_number = request.POST["phone_number"]
            clinic.city = request.POST["city"]
            clinic.state = request.POST["state"]
            clinic.save()
            request.session["message"] = "Added Clinic Successfully!"
            return redirect(f'/clinics/{clinic.id}')
        except Exception as e:
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/add_clinic')
    else:
        return render(request, "clinic_details.html", {"msg": msg})


@login_required
def clinics_details(request, id):
    """
    Displays and provide edit form of a clinic with given 'id'.

    Args:
        id (int): Clinic ID from Clinic Table.
    """

    msg = check_message(request)
    clinic = Clinic.objects.get(id=id)
    all_doctors = Doctor.objects.all()
    affiliated_doctors = ClinicDoctorAffiliation.objects.filter(clinic=clinic)
    return render(request, "clinic_details.html",
                  {'clinic': clinic, "doctors": all_doctors, "msg": msg, "affiliated_doctors": affiliated_doctors})


@login_required
def edit_clinic_details(request, id):
    """
    If request method is POST, edits the clinic with 'id',
    with the new information provided.

     Args:
        id (int): Clinic ID from Clinic Table.
     """

    if request.method == "POST":
        try:
            clinic = Clinic.objects.get(id=id)
            clinic.name = request.POST["name"]
            clinic.email = request.POST["email"]
            clinic.phone_number = request.POST["phone_number"]
            clinic.city = request.POST["city"]
            clinic.state = request.POST["state"]
            clinic.save()

            request.session["message"] = "Changes made Successfully!"
            return redirect(f'/clinics/{id}')
        except Exception as e:
            print(e)
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/clinics/{id}')
    return HttpResponse("Invalid")


def apply_working_schedule(obj, request):
    obj.office_address = request.POST['cad_off_addr']
    obj.mon_start_time = request.POST['mondayStartTime']
    obj.mon_end_time = request.POST['mondayEndTime']
    obj.tue_start_time = request.POST['tuesdayStartTime']
    obj.tue_end_time = request.POST['tuesdayEndTime']
    obj.wed_start_time = request.POST['wednesdayStartTime']
    obj.wed_end_time = request.POST['wednesdayEndTime']
    obj.thu_start_time = request.POST['thursdayStartTime']
    obj.thu_end_time = request.POST['thursdayEndTime']
    obj.fri_start_time = request.POST['fridayStartTime']
    obj.fri_end_time = request.POST['fridayEndTime']
    obj.sat_start_time = request.POST['saturdayStartTime']
    obj.sat_end_time = request.POST['saturdayEndTime']
    obj.sun_start_time = request.POST['sundayStartTime']
    obj.sun_end_time = request.POST['sundayEndTime']

    return obj


@login_required
def add_clinic_aff_doc(request, id):
    """
    If request method is POST, adds the doctor affiliation for the clinic with 'id',given the information

    Args:
    id (int): Clinic ID from Clinic Table.
    """

    if request.method == "POST":
        try:
            clinic_aff_doc = ClinicDoctorAffiliation()
            clinic_aff_doc.clinic = Clinic.objects.get(id=id)
            clinic_aff_doc.doctor = Doctor.objects.get(id=int(request.POST['cad_name']))
            clinic_aff_doc = apply_working_schedule(clinic_aff_doc, request)
            clinic_aff_doc.full_clean()
            clinic_aff_doc.save()

            request.session["message"] = "Added Successfully!"
            return redirect(f'/clinics/{id}')
        except Exception as e:
            print(e)
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/clinics/{id}')

    msg = check_message(request)
    clinic = Clinic.objects.get(id=id)
    all_doctors = Doctor.objects.all()
    return render(request, "clinic_aff_doctor.html",
                  {"doctors": all_doctors, "msg": msg, "clinic": clinic})


@login_required
def edit_clinic_aff_doc(request, clinic_id, id):
    """
    If request method is POST, edits the doctor affiliation for the clinic,given the information

    Args:
        id (int): Affiliation ID from ClinicDoctorAffiliation Table.
        clinic_id (int): Clinic ID from Clinic Table.
    """

    if request.method == "POST":
        try:
            clinic_aff_doc = ClinicDoctorAffiliation.objects.get(id=id)
            clinic_aff_doc.office_address = request.POST['cad_off_addr']
            clinic_aff_doc = apply_working_schedule(clinic_aff_doc, request)
            clinic_aff_doc.full_clean()
            clinic_aff_doc.save()

            request.session["message"] = "Changes made Successfully!"
            return redirect(f'/clinics/{clinic_id}')
        except Exception as e:
            print(e)
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/clinics/{clinic_id}')

    msg = check_message(request)
    clinic = Clinic.objects.get(id=clinic_id)
    affiliation = ClinicDoctorAffiliation.objects.get(id=id)
    return render(request, "clinic_aff_doctor.html",
                  {"affiliation": affiliation, "msg": msg, "clinic": clinic})


@login_required
def delete_clinic_aff_doc(request, clinic_id, id):
    """
    If request method is POST, deletes the doctor affiliation for the clinic.

    Args:
        id (int): Affiliation ID from ClinicDoctorAffiliation Table.
        clinic_id (int): Clinic ID from Clinic Table.
    """

    if request.method == "POST":
        try:
            clinic_aff_doc = ClinicDoctorAffiliation.objects.get(id=id)
            clinic_aff_doc.delete()

            request.session["message"] = "Deleted Successfully!"
            return redirect(f'/clinics/{clinic_id}')
        except Exception as e:
            print(e)
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/clinics/{clinic_id}')

    return "Invalid Request"


@login_required
def doctors(request):
    """
    Displays Doctors List Page.
    """
    doctors_obj = Doctor.objects.all()
    return render(request, "doctors.html", {'doctors': doctors_obj})


@login_required
def add_doctor(request):
    """
    GET : function displays a form page to add Doctor.
    POST: function submits the details to add Doctor and stores in Data Base.
    """

    msg = check_message(request)
    if request.method == 'POST':
        try:
            doctor = Doctor()
            doctor.npi = request.POST['npi']
            doctor.name = request.POST['name']
            doctor.email = request.POST['email']
            doctor.phone_number = request.POST['phone_number']
            doctor.full_clean()
            doctor.save()
            try:
                doctor.specialties.set(Procedure.objects.filter(id__in=map(int, request.POST.getlist('procedures'))))
                doctor.full_clean()
                doctor.save()
                request.session["message"] = "Added Doctor Successfully!"
                return redirect(f'/doctors/{doctor.id}')
            except Exception as e:
                doctor.delete()
                request.session["message"] = "Error: " + e.__str__()
                return redirect(f'/add_doctor')

        except Exception as e:
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/add_doctor')
    else:
        procedures = Procedure.objects.all()
        return render(request, "doctor_details.html", {"msg": msg, 'procedures': procedures})


@login_required
def doctor_details(request, id):
    """
    Displays and provide edit form of a doctor with given 'id'.

    Args:
        id (int): Doctor ID from Doctor Table.
    """

    msg = check_message(request)
    doctor = Doctor.objects.get(id=id)
    procedures = Procedure.objects.all()
    affiliated_clinics = ClinicDoctorAffiliation.objects.filter(doctor=doctor)
    visit_patients = Patient.objects.filter(visits__doctor=doctor).distinct()
    appointment_patients = Patient.objects.filter(appointments__doctor=doctor).distinct()
    affiliated_patients = visit_patients.union(appointment_patients)
    return render(request, "doctor_details.html",
                  {'doctor': doctor, "msg": msg, 'procedures': procedures,
                   'affiliated_clinics': affiliated_clinics, 'affiliated_patients': affiliated_patients})


@login_required
def edit_doctor_details(request, id):
    """
    If request method is POST, edits the clinic with 'id',with the new information provided.

    Args:
    id (int): Clinic ID from Clinic Table.
    """

    if request.method == "POST":
        try:
            doctor = Doctor.objects.get(id=id)
            doctor.npi = request.POST['npi']
            doctor.name = request.POST['name']
            doctor.email = request.POST['email']
            doctor.phone_number = request.POST['phone_number']
            doctor.specialties.set(Procedure.objects.filter(id__in=map(int, request.POST.getlist('procedures'))))
            doctor.full_clean()
            doctor.save()

            request.session["message"] = "Changes made Successfully!"
            return redirect(f'/doctors/{id}')
        except Exception as e:
            print(e)
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/doctors/{id}')
    return HttpResponse("Invalid")


@login_required
def patients(request):
    """
        Displays Patients List Page.
    """
    patients_obj = Patient.objects.all()
    return render(request, "patients.html", {'patients': patients_obj})


@login_required
def patient_details(request, id):
    """
    Displays and provide edit form of a patient with given 'id'.

    Args:
        id (int): Doctor ID from Patient Table.
    """

    msg = check_message(request)
    patient = Patient.objects.get(id=id)
    try:
        visits = Visit.objects.filter(patient=patient)
    except Visit.DoesNotExist as e:
        visits = None

    # print(patient.next_appointment().appointment_time)

    return render(request, "patient_details.html",
                  {'patient': patient, "msg": msg, 'visits': visits, 'appointment': patient.next_appointment()})


@login_required
def add_patient(request):
    """
    GET : function displays a form page to add Patient.
    POST : function submits the details to add Patient and stores in Data Base."""

    msg = check_message(request)
    if request.method == 'POST':
        try:
            patient = Patient()
            patient.name = request.POST['name']
            patient.address = request.POST['address']
            patient.phone_number = request.POST['phone_number']
            patient.date_of_birth = request.POST['date']
            patient.last_4_ssn = request.POST['ssn']
            patient.gender = request.POST['gender']
            patient.save()

            request.session["message"] = "Added Clinic Successfully!"
            return redirect(f'/patients/{patient.id}')
        except Exception as e:
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/add_patient')
    else:
        return render(request, "patient_details.html", {"msg": msg})


@login_required
def edit_patient_details(request, id):
    """
    If request method is POST, edits the patient with 'id',with the new information provided.

    Args:
        id (int): Patient ID from Patient Table.
    """

    if request.method == "POST":
        try:
            patient = Patient.objects.get(id=id)
            patient.name = request.POST['name']
            patient.address = request.POST['address']
            patient.phone_number = request.POST['phone_number']
            patient.date_of_birth = request.POST['date']
            patient.last_4_ssn = request.POST['ssn']
            patient.gender = request.POST['gender']
            patient.save()

            request.session["message"] = "Changes made Successfully!"
            return redirect(f'/patients/{id}')
        except Exception as e:
            print(e)
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/patients/{id}')
    return HttpResponse("Invalid")


@login_required
def add_appointment(request, id):
    """
    GET : function displays a form page to add Appointment.
    POST : function submits the details to add Appointment and stores in Data Base.
    """

    msg = check_message(request)
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(id=int(request.POST['doctor']))
            specialties = {procedure[0]: procedure[1] for procedure in doctor.specialties.values_list()}
            if int(request.POST['procedure']) not in specialties.keys():
                request.session["message"] = "Error: Doctor and procedure doesn't match"
                return redirect(f'/add_appointment/{id}')

            clinic = Clinic.objects.get(id=int(request.POST['clinic']))
            affiliation = ClinicDoctorAffiliation.objects.get(clinic=clinic, doctor=doctor)
            patient = Patient.objects.get(id=id)

            appointment = Appointment()
            appointment.doctor = doctor
            appointment.clinic = clinic
            appointment.patient = patient
            appointment.appointment_date = datetime.strptime(request.POST['date'], '%Y-%m-%d')
            appointment.appointment_time = request.POST['time']
            appointment.procedure = Procedure.objects.get(id=int(request.POST['procedure']))
            appointment.save()

            request.session["message"] = "Added Appointment Successfully!"
            return redirect(f'/patients/{patient.id}')

        except Exception as e:
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/add_appointment/{id}')
    else:
        procedures = Procedure.objects.all()
        doctors = Doctor.objects.all()
        clinics = Clinic.objects.all()
        patient = Patient.objects.get(id=id)
        return render(request, "add_appointment_visit.html",
                      {"msg": msg, 'procedures': procedures, 'patient': patient,
                       "doctors": doctors, "clinics": clinics, "appointment": True})


@login_required
def get_blocked_times(request, doctorId, clinicId, procedureId):
    """
    Args:
    :param request:
    :param doctorId:
    :param clinicId:
    :param procedureId:
    :return: Returns the doctor blocked time for appointment booking for a patient
    """

    try:
        doctor = Doctor.objects.get(id=doctorId)
        clinic = Clinic.objects.get(id=clinicId)
        procedure = Procedure.objects.get(id=procedureId)

        date_str = request.GET['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        day_of_week = date_obj.weekday()

        affiliation = ClinicDoctorAffiliation.objects.get(doctor=doctor, clinic=clinic)

        start_time = None
        end_time = None

        if day_of_week == 0:  # Monday
            start_time = affiliation.mon_start_time
            end_time = affiliation.mon_end_time
        elif day_of_week == 1:  # Tuesday
            start_time = affiliation.tue_start_time
            end_time = affiliation.tue_end_time
        elif day_of_week == 2:  # Wednesday
            start_time = affiliation.wed_start_time
            end_time = affiliation.wed_end_time
        elif day_of_week == 3:  # Thursday
            start_time = affiliation.thu_start_time
            end_time = affiliation.thu_end_time
        elif day_of_week == 4:  # Friday
            start_time = affiliation.fri_start_time
            end_time = affiliation.fri_end_time
        elif day_of_week == 5:  # Saturday
            start_time = affiliation.sat_start_time
            end_time = affiliation.sat_end_time
        elif day_of_week == 6:  # Sunday
            start_time = affiliation.sun_start_time
            end_time = affiliation.sun_end_time

        doctor_appointments = Appointment.objects.filter(doctor=doctor, clinic=clinic, appointment_date=date_obj)

        if start_time and end_time:
            return JsonResponse({'start': start_time, 'end': end_time,
                                 'list': [time.appointment_time for time in doctor_appointments]})
        else:
            return JsonResponse({'start': '00:00', 'end': '00:00', 'list': []})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Error, Please try again!'}, status=500)


@login_required
def get_doctors_by_clinic(request, clinicId, procedureId):
    """
    :param request: The HTTP request object
    :param clinicId: The ID of the clinic
    :param procedureId: The ID of the procedure
    :return: JSON response containing a list of doctors associated with the clinic and the specified procedure
    """
    try:
        # Fetch the procedure by procedureId
        procedure = Procedure.objects.get(id=procedureId)

        # Fetch doctors who are affiliated with the clinic and have the selected procedure as a specialty
        doctors = ClinicDoctorAffiliation.objects.filter(
            clinic_id=clinicId,
            doctor__specialties=procedure
        ).values_list('doctor__id', 'doctor__name', 'doctor__npi').distinct()

        # Create a list of doctors to return as JSON
        doctor_list = [{'id': d[0], 'name': d[1], 'npi': d[2]} for d in doctors]

        return JsonResponse({'doctors': doctor_list})
    except Procedure.DoesNotExist:
        return JsonResponse({'error': 'Procedure not found'}, status=404)
    except Clinic.DoesNotExist:
        return JsonResponse({'error': 'Clinic not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Error fetching doctors'}, status=500)


@login_required
def get_clinics_by_procedure(request, procedureId):
    """
    :param request: The HTTP request object
    :param procedureId: The ID of the procedure
    :return: JSON response containing a list of clinics where doctors perform the specified procedure
    """
    try:
        # Fetch the procedure by procedureId
        procedure = Procedure.objects.get(id=procedureId)

        # Fetch the clinics where doctors associated with the procedure are affiliated
        clinics = ClinicDoctorAffiliation.objects.filter(doctor__specialties=procedure).values_list('clinic__id', 'clinic__name').distinct()

        # Create a list of clinics to return as JSON
        clinic_list = [{'id': c[0], 'name': c[1]} for c in clinics]

        return JsonResponse({'clinics': clinic_list})
    except Procedure.DoesNotExist:
        return JsonResponse({'error': 'Procedure not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Error fetching clinics'}, status=500)


@login_required
def add_visit(request, id):
    """
    GET : function displays a form page to add visit for the patient with given id.

    POST : function submits the details to add visit for the patient and stores in Data Base.
    """

    msg = check_message(request)
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(id=int(request.POST['doctor']))
            specialties = {procedure[0]: procedure[1] for procedure in doctor.specialties.values_list()}
            if int(request.POST['procedure']) not in specialties.keys():
                request.session["message"] = "Error: Doctor and procedure doesn't match"
                return redirect(f'/add_visit/{id}')

            clinic = Clinic.objects.get(id=int(request.POST['clinic']))
            affiliation = ClinicDoctorAffiliation.objects.get(clinic=clinic, doctor=doctor)
            patient = Patient.objects.get(id=id)

            visit = Visit()
            visit.doctor = doctor
            visit.clinic = clinic
            visit.patient = patient
            visit.visit_date = datetime.strptime(request.POST['date'], '%Y-%m-%d')
            visit.procedures_done = Procedure.objects.get(id=int(request.POST['procedure']))
            visit.doctor_notes = request.POST['doctor_notes']
            visit.save()

            request.session["message"] = "Added Visit Successfully!"
            return redirect(f'/patients/{patient.id}')

        except Exception as e:
            request.session["message"] = "Error: " + e.__str__()
            return redirect(f'/add_visit/{id}')
    else:
        procedures = Procedure.objects.all()
        doctors = Doctor.objects.all()
        clinics = Clinic.objects.all()
        patient = Patient.objects.get(id=id)
        return render(request, "add_appointment_visit.html",
                      {"msg": msg, 'procedures': procedures, 'patient': patient,
                       "doctors": doctors, "clinics": clinics})


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                user_login(request, user)
                return redirect('home')
            else:
                request.session["message"] = "Invalid Credentials..!, Please check the details"
                return redirect('login')
        except Exception as e:
            request.session["message"] = "Error: " + e.__str__()
            return redirect('login')
    msg = check_message(request)
    print(msg)
    return render(request, "login.html", {'msg': msg})


@login_required
def logout(request):
    user_logout(request)
    return redirect('login')


# REST APIs

# Add Patient
@api_view(['POST'])
def add_patient_api(request):
    if request.method == 'POST':
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Add Doctor
@api_view(['POST'])
def add_doctor_api(request):
    if request.method == 'POST':
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Add Clinic
@api_view(['POST'])
def add_clinic_api(request):
    if request.method == 'POST':
        serializer = ClinicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get Clinic Information
@api_view(['GET'])
def get_clinic_api(request, clinic_id):
    try:
        clinic = Clinic.objects.get(id=clinic_id)
    except Clinic.DoesNotExist:
        return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ClinicSerializer(clinic)
        return Response(serializer.data, status=status.HTTP_200_OK)
