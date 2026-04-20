from fastapi import FastAPI

app = FastAPI()

# Функция получения списка студентов
@app.get("/students")
def get_students():
    return [{"id": 1, "name": "Иванов Иван"}, {"id": 2, "name": "Петров Петр"}]

# Функция отметки посещаемости
@app.post("/attendance")
def mark_attendance(student_id: int, status: str):
    return {"message": f"Студент {student_id} отмечен как {status}"}