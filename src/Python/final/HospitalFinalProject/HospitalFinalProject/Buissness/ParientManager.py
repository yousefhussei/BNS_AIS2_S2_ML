from DataAccessLayer.repository import Repository
from DataAccessLayer.json_db_context import JsonDbContext
from Domain.Patient import Patient

class PatientManager:

    def __init__(self):
        self.repo = Repository("patients.json")

    def register_patient(self , name:str , age:int , address:str , phone:str , patient_id:str , medical_history:str):
        patient = Patient(name , age , address , phone , patient_id , medical_history)
        self.repo.add(patient.to_dict() , "patient_id")
    def get_all_patients(self):
        return self.repo.get_all()

    def get_patient(self, patient_id: str):
        return self.repo.get_by_id(patient_id, "patient_id")

    def delete_patient(self, patient_id: str):
        self.repo.delete(patient_id, "patient_id")        