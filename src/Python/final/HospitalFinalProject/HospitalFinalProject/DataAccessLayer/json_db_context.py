import os
import json

class JsonDbContext:
    @staticmethod
    def ensure_file(file_path: str):
        # التأكد من وجود مجلد data_files وإنشاء الملف لو لم يكن موجوداً
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    @staticmethod
    def read_data(file_path: str) -> list:
        JsonDbContext.ensure_file(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def write_data(file_path: str, data: list):
        JsonDbContext.ensure_file(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)