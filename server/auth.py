# auth.py
# Здесь описана вся логика работы с JWT-токенами и проверка прав

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Импортируем секретный ключ из config.py и нашу модель User
from config import Config
from models import User

# Функция для создания JWT-токена
def create_token(user):
    """
    Создает JWT-токен для пользователя.
    Внутри токена 'зашиты' id пользователя и его роль.
    """
    payload = {
        'user_id': user.id,
        'role': user.role,
        # Токен будет действителен 24 часа
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token

# Декоратор для защиты маршрутов (требует авторизацию)
def login_required(f):
    """
    Этот декоратор мы будем 'навешивать' на наши API-функции.
    Он проверяет, есть ли в запросе правильный JWT-токен.
    """
    f
    def decorated(*args, **kwargs):
        token = None
        # Проверяем заголовок Authorization: Bearer <токен>
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1]  # Забираем токен после слова "Bearer"
        
        if not token:
            return jsonify({'error': 'Токен отсутствует. Авторизуйтесь.'}), 401
        
        try:
            # Расшифровываем токен
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            # Находим пользователя в БД по ID из токена
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Пользователь не найден.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Срок действия токена истек.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Недействительный токен.'}), 401
            
        # Если всё хорошо, выполняем саму функцию-маршрут и передаем ей пользователя
        return f(current_user, *args, **kwargs)
    return decorated

# Декоратор для проверки роли (например, доступ только для админа)
def admin_required(f):
    """
    Декоратор, который пускает только пользователей с ролью 'admin'.
    Должен использоваться ПОСЛЕ @login_required.
    """
    f
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Доступ запрещен. Требуются права администратора.'}), 403
        return f(current_user, *args, **kwargs)
    return decorated