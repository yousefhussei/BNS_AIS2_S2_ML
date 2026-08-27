class Appointment:
    def __init__(self, appointment_id: str, patient_id: str, doctor_id: str, date_time: str, status: str = "Scheduled"):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date_time = date_time
        self.status = status

    def book_appointement(self):
        self.status = "Booked"
    def cancel_appointement(self):
        self.status = "Cancelled" 


    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "date_time": self.date_time,
            "status": self.status
        }         
