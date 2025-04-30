import openpyxl

from typing import Dict, List
from io import BytesIO

from fastapi import UploadFile

from src.models import Roles


class Parser:
    def __init__(self, file: UploadFile):
        self.file = file
        # Используем BytesIO для работы с файлом в памяти
        self.file_content = BytesIO(self.file.file.read())
        self.workbook = openpyxl.load_workbook(self.file_content)
        self.sheet = self.workbook.active

    def parse_users(self) -> List[Dict]:
        users = []
        for row in self.sheet.iter_rows(min_row=2, values_only=True):
            if row[0] is None:  # Пропускаем пустые строки
                break

            users.append({
                "surname": str(row[0]),
                "name": str(row[1]),
                "patronymic": str(row[2]),
                "role": Roles.student,
                "phone": str(row[3]),
                "login": str(row[4]),
                "password": str(row[5])
            })

        return users


if __name__ == "__main__":
    pass
    # path = "students.xlsx"
    # parser = Parser(path)
    # users_parsed = parser.parse_users()
    # print(users_parsed)
