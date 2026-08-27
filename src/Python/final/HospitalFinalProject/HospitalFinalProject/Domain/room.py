class room:
    def __init__(self, room_number: str, room_type: str, status: str = "Available"):
        self.room_number = room_number
        self.room_type = room_type
        self.status = status # Available or Occupied

    def assign_patient(self, patient_id: str):
        self.status = "Occupied"

    def free_room(self):
        self.status = "Available"

    def to_dict(self):
        return {
            "room_number": self.room_number,
            "room_type": self.room_type,
            "status": self.status
        }