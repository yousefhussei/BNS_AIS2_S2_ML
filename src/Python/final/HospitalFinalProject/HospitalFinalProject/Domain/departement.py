class Departement:

    def __init__(self , department_id:str , name:str):
        self.department_id = department_id
        self.name = name
        self.doctors = []
        self.nurses = []
        self.patients = []

    def add_doctor(self , doctor_id:str):
        if doctor_id not in self.doctors:
            self.doctors.append(doctor_id)
    def add_nurse(self , nurse_id:str):

        if nurse_id not in self.nurses:
            self.nurses.append(nurse_id)

    def add_patient(self, patient_id: str):
        if patient_id not in self.patients:
            self.patients.append(patient_id)

    def to_dict(self):
        return{

            "department_id": self.departement_id,
            "name": self.name,
            "doctors": self.doctors,
            "nurses": self.nurses,
            "patients": self.patients




        }                           