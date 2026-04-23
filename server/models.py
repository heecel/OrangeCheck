# models.py
# Описывает таблицы базы данных с помощью SQLAlchemy

from flask_sqlalchemy import SQLAlchemy

# Создаем объект db, через который будем работать с БД
db = SQLAlchemy()

# --- Таблица 1: Пользователи (Users) ---
class User(db.Model):
    __tablename__ = 'users' # Имя таблицы в БД
    
    id = db.Column(db.Integer, primary_key=True)    # Уникальный ID
    login = db.Column(db.String(80), unique=True, nullable=False) # Логин (уникальный)
    password = db.Column(db.String(200), nullable=False) # Пароль (пока будем хранить как есть, без хэша)
    role = db.Column(db.String(20), nullable=False)  # Роль: 'admin' или 'teacher'

# --- Таблица 2: Группы (Groups) ---
class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # Название (уникальное, например "ИС-21")
    
    students = db.relationship('Student', backref='group', lazy=True) # Связь "одна группа - много студентов"

# --- Таблица 3: Студенты (Students) ---
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Имя и фамилия
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False) # Внешний ключ на таблицу groups
    email = db.Column(db.String(120), unique=True, nullable=False) # Email (уникальный)
    
    attendances = db.relationship('Attendance', backref='student', lazy=True) # Связь "один студент - много записей о посещаемости"

# --- Таблица 4: Посещаемость (Attendance) ---
class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False) # Внешний ключ на таблицу students
    date = db.Column(db.String(10), nullable=False) # Дата в формате "YYYY-MM-DD"
    status = db.Column(db.String(10), nullable=False) # Статус: 'present' или 'absent'