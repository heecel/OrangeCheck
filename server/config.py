# config.py
# Хранит все настройки нашего приложения в одном месте

class Config:
    # Секретный ключ для подписи JWT-токенов. В реальном проекте он должен быть сложным!
    SECRET_KEY = 'super-secret-key-12345-change-me'
    
    # Путь к файлу базы данных SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///orangecheck.db'
    
    # Отключаем отслеживание изменений (экономит ресурсы)
    SQLALCHEMY_TRACK_MODIFICATIONS = False