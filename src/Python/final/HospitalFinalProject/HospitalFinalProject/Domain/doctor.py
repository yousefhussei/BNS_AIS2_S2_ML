from Domain.Person import Person



class doctor(Person):

    def __init__(self , name:str , age:int ,address:str , phone:str , doctor_id:str , specialization:str , departement_id:str ) :
        super().__init__(name , age , address , phone)
        self.doctor_id = doctor_id
        self.specialization = specialization
        self.departement_id = departement_id

    def prescribe_mediation(self):
        pass
    def add_medical_record(self):
        pass
    def to_dict(self):
        return {
            "doctor_id": self.doctor_id,
            "name": self.name,
            "age": self.age,
            "address": self.address,
            "phone": self.phone,
            "specialization": self.specialization,
            "department_id": self.departement_id
        }