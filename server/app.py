# app.py
# Главный файл приложения. Здесь всё собирается воедино.

from flask import Flask, request, jsonify
from config import Config
from models import db, User, Group, Student, Attendance
from routes import api_bp
from auth import create_token

def create_app():
    """Функция, которая создает и настраивает Flask-приложение."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Регистрируем blueprint с API-маршрутами
    # ВАЖНО: убираем url_prefix='/api', чтобы проверить, регистрируются ли маршруты
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from flask_cors import CORS
    CORS(app)
    
    return app

app = create_app()

# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>OrangeCheck API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 700px; margin: 50px auto; padding: 20px; }
            h1 { color: #ff6b35; }
            code { background: #f4f4f4; padding: 3px 8px; border-radius: 4px; }
            li { margin: 8px 0; }
        </style>
    </head>
    <body>
        <h1>🟠 OrangeCheck API</h1>
        <p>Сервер учёта посещаемости студентов <strong>успешно запущен!</strong></p>
        <hr>
        <h3>Доступные маршруты API:</h3>
        <ul>
            <li><code>POST /login</code> — авторизация и получение JWT-токена</li>
            <li><code>GET /api/students</code> — список всех студентов</li>
            <li><code>POST /api/students</code> — добавить нового студента</li>
            <li><code>PUT /api/students/&lt;id&gt;</code> — редактировать студента</li>
            <li><code>DELETE /api/students/&lt;id&gt;</code> — удалить студента</li>
            <li><code>GET /api/students/search?q=...</code> — поиск студентов</li>
            <li><code>GET /api/groups</code> — список всех групп</li>
            <li><code>POST /api/groups</code> — создать новую группу</li>
            <li><code>POST /api/attendance</code> — отметить посещаемость</li>
            <li><code>GET /api/attendance</code> — получить записи о посещаемости</li>
            <li><code>GET /api/attendance/stats</code> — статистика посещаемости</li>
        </ul>
        <hr>
        <p><strong>Тестовые данные для входа:</strong></p>
        <ul>
            <li>Администратор: <code>admin</code> / <code>admin123</code></li>
            <li>Преподаватель: <code>teacher1</code> / <code>teach123</code></li>
        </ul>
        <p><em>Для тестирования API используйте <strong>Thunder Client</strong> в VS Code.</em></p>
        <p><em>Для работы с интерфейсом откройте файл <strong>client/index.html</strong></em></p>
    </body>
    </html>
    '''

# ========== АВТОРИЗАЦИЯ ==========
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('login') or not data.get('password'):
        return jsonify({'error': 'Необходимо указать логин и пароль.'}), 400
        
    user = User.query.filter_by(login=data['login']).first()
    
    if user and user.password == data['password']:
        token = create_token(user)
        return jsonify({
            'token': token,
            'user': {
                'login': user.login,
                'role': user.role
            }
        }), 200
    else:
        return jsonify({'error': 'Неверный логин или пароль.'}), 401

# ========== СОЗДАНИЕ БАЗЫ ДАННЫХ ==========
with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(login='admin').first():
        admin = User(login='admin', password='admin123', role='admin')
        teacher = User(login='teacher1', password='teach123', role='teacher')
        db.session.add(admin)
        db.session.add(teacher)
        
        group1 = Group(name='ИС-21')
        group2 = Group(name='ИС-22')
        db.session.add(group1)
        db.session.add(group2)
        db.session.flush()
        
        student1 = Student(name='Иван Иванов', group_id=group1.id, email='ivanov@example.com')
        student2 = Student(name='Анна Петрова', group_id=group1.id, email='petrova@example.com')
        student3 = Student(name='Алексей Смирнов', group_id=group2.id, email='smirnov@example.com')
        db.session.add(student1)
        db.session.add(student2)
        db.session.add(student3)
        
        db.session.commit()
        print(">>> База данных создана. Тестовые пользователи: admin/admin123, teacher1/teach123")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🟠 Сервер OrangeCheck запущен!")
    print("📋 Главная страница: http://127.0.0.1:5000")
    print("📋 Фронтенд: откройте client/index.html в браузере")
    print("🛑 Остановка: Ctrl+C")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)