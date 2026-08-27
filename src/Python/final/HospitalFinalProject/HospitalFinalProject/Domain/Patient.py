
from Domain.Person import Person
class Patient(Person):

    def __init__(self , name:str , age:int , address:str , phone:str , patient_id:str = "" , medical_history:str = ""):

        super().__init__(name , age , address , phone)
        self.patient_id = patient_id
        self.medical_history = medical_history
    def view_record(self) -> str:
        return f"Patient_id : {self.patient_id} , Name:{self.name} , History : {self.medical_history}"

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "address": self.address,
            "phone": self.phone,
            "PatientID": self.patient_id,
            "medical_history": self.medical_history
        }


class InPatient(Patient):

    def __init__(self, name: str, age: int, address: str, phone: str, patient_id: str, medical_history: str, 
                 admission_date: str, discharge_date: str, room_number: str, status: str):
        super().__init__(name, age, address, phone, patient_id, medical_history)
        self.admission_date = admission_date
        self.discharge_date = discharge_date
        self.room_number = room_number
        self.status = status
    def room_check(self) ->str:
        return f"Patient {self.name} is in Room {self.room_number}"    

    def to_dic(self):
        d = super().to_dict()
        d.update({

            "patient_type": "InPatient",
            "admission_date": self.admission_date,
            "discharge_date": self.discharge_date,
            "room_number": self.room_number,
            "status": self.status


        })
        return d

class OutPatient(Patient):
    def __init__(self, name: str, age: int, address: str, phone: str, patient_id: str, medical_history: str, visit_date: str):
        super().__init__(name, age, address, phone, patient_id, medical_history)
        self.visit_date = visit_date

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "patient_type": "OutPatient",
            "visit_date": self.visit_date
        })
        return d   


    






