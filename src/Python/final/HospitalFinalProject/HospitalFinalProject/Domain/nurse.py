from Domain.Person import Person

class nurse(Person):
    def __init__(self, name: str, age: int, address: str, phone: str, nurse_id: str, department_id: str):
        super().__init__(name, age, address, phone)
        self.nurse_id = nurse_id
        self.department_id = department_id

    def assist_doctor(self):
        pass

    def monitor_patient(self):
        pass

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "nurse_id": self.nurse_id,
            "department_id": self.department_id
        })
        return d