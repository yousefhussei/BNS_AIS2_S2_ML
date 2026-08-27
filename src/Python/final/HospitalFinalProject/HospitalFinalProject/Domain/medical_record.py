class medical_record:
    def __init__(self, record_id: str, patient_id: str, diagnosis: str, prescription: str, date: str):
        self.record_id = record_id
        self.patient_id = patient_id
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.date = date

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "patient_id": self.patient_id,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "date": self.date
        }