from DataAccessLayer.repository import Repository
from Domain.doctor import doctor as Doctor

class DoctorManager:
    def __init__(self):
        self.repo = Repository("doctors.json")

    def add_doctor(self, name: str, age: int, address: str, phone: str, doctor_id: str, specialization: str, departement_id: str):
        doctor = Doctor(name, age, address, phone, doctor_id, specialization, departement_id)
        self.repo.add(doctor.to_dict(), "doctor_id")
        return doctor

    def get_all_doctors(self):
        return self.repo.get_all()

    def get_doctor(self, doctor_id: str):
        return self.repo.get_by_id(doctor_id, "doctor_id")

    def delete_doctor(self, doctor_id: str):
        self.repo.delete(doctor_id, "doctor_id")