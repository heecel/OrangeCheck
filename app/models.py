from sqlalchemy import Column, Integer, String, ForeignKey, Date
from .database import Base

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True) # Например, "ИС-21"

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    group_id = Column(Integer, ForeignKey("groups.id"))

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(String) # Дата занятия
    status = Column(String) # "present" или "absent"