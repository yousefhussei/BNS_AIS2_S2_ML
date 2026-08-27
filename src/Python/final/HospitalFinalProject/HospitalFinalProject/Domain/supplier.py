class supplier:
    def __init__(self, supplier_id: str, name: str, contact_info: str):
        self.supplier_id = supplier_id
        self.name = name
        self.contact_info = contact_info
        self.supplied_medicines = []

    def to_dict(self):
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "contact_info": self.contact_info,
            "supplied_medicines": self.supplied_medicines
        }