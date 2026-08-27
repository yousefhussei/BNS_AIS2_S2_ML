from DataAccessLayer.repository import Repository
from Domain.appointement import Appointment

class AppointmentManager:
    def __init__(self):
        self.repo = Repository("appointments.json")

    def book_appointment(self, appointment_id: str, patient_id: str, doctor_id: str, date_time: str):
        appt = Appointment(appointment_id, patient_id, doctor_id, date_time, "Booked")
        self.repo.add(appt.to_dict(), "appointment_id")
        return appt

    def get_all_appointments(self):
        return self.repo.get_all()

    def cancel_appointment(self, appointment_id: str):
        appt_data = self.repo.get_by_id(appointment_id, "appointment_id")
        if appt_data:
            appt_data["status"] = "Cancelled"
            self.repo.add(appt_data, "appointment_id")