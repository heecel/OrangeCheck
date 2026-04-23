# routes.py
# Описывает все обработчики URL (эндпоинты) для нашего API

from flask import Blueprint, request, jsonify
from models import db, Student, Group, Attendance
from auth import login_required, admin_required

# Создаем "blueprint" (набор маршрутов). Все URL будут начинаться с /api
api_bp = Blueprint('api', __name__)

# ========== Маршруты для студентов ==========

@api_bp.route('/students', methods=['GET'], endpoint='get_students')
@login_required
def get_students(current_user):
    """Получение списка всех студентов (F-08, F-11)"""
    students = Student.query.all()
    output = []
    for student in students:
        student_data = {
            'id': student.id,
            'name': student.name,
            'group': student.group.name,
            'email': student.email
        }
        output.append(student_data)
    return jsonify({'data': output}), 200

@api_bp.route('/students', methods=['POST'], endpoint='add_student')
@login_required
@admin_required
def add_student(current_user):
    """Добавление нового студента (F-03)"""
    data = request.get_json()
    new_student = Student(
        name=data['name'],
        group_id=data['group_id'],
        email=data['email']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'message': 'Студент успешно добавлен.', 'id': new_student.id}), 201

@api_bp.route('/students/<int:student_id>', methods=['PUT'], endpoint='edit_student')
@login_required
@admin_required
def edit_student(current_user, student_id):
    """Редактирование информации о студенте (F-03)"""
    student = Student.query.get_or_404(student_id)
    data = request.get_json()
    
    if 'name' in data:
        student.name = data['name']
    if 'group_id' in data:
        group = Group.query.get(data['group_id'])
        if not group:
            return jsonify({'error': 'Группа не найдена.'}), 400
        student.group_id = data['group_id']
    if 'email' in data:
        student.email = data['email']
        
    db.session.commit()
    return jsonify({'message': 'Информация о студенте обновлена.'}), 200

@api_bp.route('/students/<int:student_id>', methods=['DELETE'], endpoint='delete_student')
@login_required
@admin_required
def delete_student(current_user, student_id):
    """Удаление студента (F-03)"""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Студент успешно удален.'}), 200

@api_bp.route('/students/search', methods=['GET'], endpoint='search_students')
@login_required
def search_students(current_user):
    """Поиск студентов по имени или группе (F-11)"""
    query_param = request.args.get('q', '')
    
    if not query_param:
        return jsonify({'error': 'Укажите параметр q для поиска.'}), 400
        
    students = Student.query.join(Group).filter(
        db.or_(
            Student.name.ilike(f'%{query_param}%'),
            Group.name.ilike(f'%{query_param}%')
        )
    ).all()
    
    output = []
    for student in students:
        student_data = {
            'id': student.id,
            'name': student.name,
            'group': student.group.name,
            'email': student.email
        }
        output.append(student_data)
        
    return jsonify({
        'search_query': query_param,
        'results_count': len(output),
        'data': output
    }), 200

# ========== Маршруты для групп ==========

@api_bp.route('/groups', methods=['GET'], endpoint='get_groups')
@login_required
def get_groups(current_user):
    """Получение списка всех групп (F-04)"""
    groups = Group.query.all()
    output = []
    for group in groups:
        group_data = {
            'id': group.id,
            'name': group.name
        }
        output.append(group_data)
    return jsonify({'data': output}), 200

@api_bp.route('/groups', methods=['POST'], endpoint='add_group')
@login_required
@admin_required
def add_group(current_user):
    """Добавление новой группы (F-04)"""
    data = request.get_json()
    
    existing_group = Group.query.filter_by(name=data['name']).first()
    if existing_group:
        return jsonify({'error': 'Группа с таким названием уже существует.'}), 400
        
    new_group = Group(name=data['name'])
    db.session.add(new_group)
    db.session.commit()
    return jsonify({'message': 'Группа успешно создана.', 'id': new_group.id}), 201

# ========== Маршруты для посещаемости ==========

@api_bp.route('/attendance', methods=['POST'], endpoint='mark_attendance')
@login_required
def mark_attendance(current_user):
    """Отметка посещаемости студента (F-05)"""
    if current_user.role != 'teacher' and current_user.role != 'admin':
        return jsonify({'error': 'Только преподаватель или администратор может отмечать посещаемость.'}), 403
        
    data = request.get_json()
    
    student = Student.query.get(data['student_id'])
    if not student:
        return jsonify({'error': 'Студент не найден.'}), 400
        
    if data['status'] not in ['present', 'absent']:
        return jsonify({'error': 'Статус должен быть "present" или "absent".'}), 400
        
    existing_record = Attendance.query.filter_by(
        student_id=data['student_id'],
        date=data['date']
    ).first()
    
    if existing_record:
        existing_record.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Посещаемость обновлена.'}), 200
    else:
        new_record = Attendance(
            student_id=data['student_id'],
            date=data['date'],
            status=data['status']
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'message': 'Посещаемость отмечена.'}), 201

@api_bp.route('/attendance', methods=['GET'], endpoint='get_attendance')
@login_required
def get_attendance(current_user):
    """Получение записей о посещаемости (F-06)"""
    date_filter = request.args.get('date')
    group_filter = request.args.get('group_id')
    student_filter = request.args.get('student_id')
    
    query = Attendance.query
    
    if date_filter:
        query = query.filter(Attendance.date == date_filter)
    if student_filter:
        query = query.filter(Attendance.student_id == student_filter)
    if group_filter:
        query = query.join(Student).filter(Student.group_id == group_filter)
        
    query = query.join(Student).order_by(Attendance.date.desc(), Student.name)
    
    records = query.all()
    output = []
    for record in records:
        record_data = {
            'id': record.id,
            'student_id': record.student_id,
            'student_name': record.student.name,
            'group_name': record.student.group.name,
            'date': record.date,
            'status': record.status
        }
        output.append(record_data)
    return jsonify({'data': output}), 200

@api_bp.route('/attendance/stats', methods=['GET'], endpoint='attendance_stats')
@login_required
def get_attendance_stats(current_user):
    """Получение статистики посещаемости (F-12)"""
    student_id = request.args.get('student_id')
    group_id = request.args.get('group_id')
    
    if student_id:
        student = Student.query.get_or_404(student_id)
        total_records = Attendance.query.filter_by(student_id=student_id).count()
        present_records = Attendance.query.filter_by(student_id=student_id, status='present').count()
        absent_records = total_records - present_records
        
        attendance_percentage = (present_records / total_records * 100) if total_records > 0 else 0
        
        return jsonify({
            'student_name': student.name,
            'group': student.group.name,
            'total_lessons': total_records,
            'attended': present_records,
            'missed': absent_records,
            'attendance_percentage': round(attendance_percentage, 1)
        }), 200
        
    elif group_id:
        students = Student.query.filter_by(group_id=group_id).all()
        group = Group.query.get_or_404(group_id)
        
        stats = []
        for student in students:
            total = Attendance.query.filter_by(student_id=student.id).count()
            present = Attendance.query.filter_by(student_id=student.id, status='present').count()
            percentage = (present / total * 100) if total > 0 else 0
            
            stats.append({
                'student_name': student.name,
                'total_lessons': total,
                'attended': present,
                'missed': total - present,
                'attendance_percentage': round(percentage, 1)
            })
            
        return jsonify({
            'group_name': group.name,
            'students_stats': stats
        }), 200
    else:
        return jsonify({'error': 'Укажите student_id или group_id для получения статистики.'}), 400