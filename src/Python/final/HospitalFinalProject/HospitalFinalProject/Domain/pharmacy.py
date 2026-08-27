class pharmacy:
    def __init__(self, pharmacy_id: str, location: str):
        self.pharmacy_id = pharmacy_id
        self.location = location
        self.medicines = []

    def add_medicine(self, medicine_id: str):
        if medicine_id not in self.medicines:
            self.medicines.append(medicine_id)

    def to_dict(self):
        return {
            "pharmacy_id": self.pharmacy_id,
            "location": self.location,
            "medicines": self.medicines
        }