from rest_framework import serializers
from .models import Clinic, Doctor, Patient, Procedure


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'phone_number', 'city', 'state', 'email']


class DoctorSerializer(serializers.ModelSerializer):
    specialties = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Doctor
        fields = ['id', 'npi', 'name', 'email', 'phone_number', 'specialties']

    def validate_specialties(self, specialties):
        """
        Convert procedure names to their corresponding IDs
        """

        procedure_ids = []

        procedures = {
            'cleaning': 1,
            'filling': 2,
            'root canal': 3,
            'crown': 4,
            'teeth whitening': 6
        }

        for specialty in specialties:
            procedure_id = procedures.get(specialty.lower())
            if procedure_id:
                procedure_ids.append(procedure_id)
            else:
                raise serializers.ValidationError(f"Procedure '{specialty}' not found.")

        return procedure_ids

    def create(self, validated_data):
        specialties_data = validated_data.pop('specialties')

        doctor = Doctor.objects.create(**validated_data)

        doctor.specialties.set(specialties_data)

        return doctor


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'address', 'phone_number', 'date_of_birth', 'last_4_ssn', 'gender']
