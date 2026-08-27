from DataAccessLayer.json_db_context import JsonDbContext

class Repository:
    def __init__(self, filename: str):
        # تحديد مسار ملفات الـ JSON في مجلد data_files
        self.file_path = f"data_files/{filename}"

    def get_all(self) -> list:
        return JsonDbContext.read_data(self.file_path)

    def save_all(self, data: list):
        JsonDbContext.write_data(self.file_path, data)

    def add(self, item_dict: dict, id_field: str):
        items = self.get_all()
        # منع التكرار وتحديث العنصر إذا كان موجوداً مسبقاً بنفس الـ ID
        items = [i for i in items if i.get(id_field) != item_dict.get(id_field)]
        items.append(item_dict)
        self.save_all(items)

    def get_by_id(self, item_id: str, id_field: str) -> dict:
        items = self.get_all()
        for item in items:
            if str(item.get(id_field)) == str(item_id):
                return item
        return None

    def delete(self, item_id: str, id_field: str):
        items = self.get_all()
        items = [i for i in items if str(i.get(id_field)) != str(item_id)]
        self.save_all(items)