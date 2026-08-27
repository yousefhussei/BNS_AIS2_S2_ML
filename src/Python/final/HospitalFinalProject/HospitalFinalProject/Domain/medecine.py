class medicine:
    def __init__(self, medicine_id: str, name: str, price: float, quantity: int):
        self.medicine_id = medicine_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, amount: int):
        self.quantity += amount

    def to_dict(self):
        return {
            "medicine_id": self.medicine_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity
        }