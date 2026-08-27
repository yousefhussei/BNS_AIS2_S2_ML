from DataAccessLayer.repository import Repository
from Domain.medecine import medicine as Medicine

class PharmacyManager:
    def __init__(self):
        self.repo = Repository("medicines.json")

    def add_medicine(self, medicine_id: str, name: str, price: float, quantity: int):
        med = Medicine(medicine_id, name, price, quantity)
        self.repo.add(med.to_dict(), "medicine_id")
        return med

    def get_all_medicines(self):
        return self.repo.get_all()

    def update_stock(self, medicine_id: str, quantity: int):
        med_data = self.repo.get_by_id(medicine_id, "medicine_id")
        if med_data:
            med_data["quantity"] += quantity
            self.repo.add(med_data, "medicine_id")