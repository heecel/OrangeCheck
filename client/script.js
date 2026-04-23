// ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
const API_URL = 'http://127.0.0.1:5000';
let authToken = localStorage.getItem('token') || null;
let currentUser = null;

// ========== DOM-ЭЛЕМЕНТЫ ==========
const loginScreen = document.getElementById('login-screen');
const mainScreen = document.getElementById('main-screen');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const userInfo = document.getElementById('user-info');

// ========== ИНИЦИАЛИЗАЦИЯ ==========
if (authToken) {
    // Если токен уже сохранён — пробуем войти
    checkAuth();
} else {
    showLoginScreen();
}

// ========== ФУНКЦИИ НАВИГАЦИИ ==========
function showLoginScreen() {
    loginScreen.classList.add('active');
    mainScreen.classList.remove('active');
}

function showMainScreen() {
    loginScreen.classList.remove('active');
    mainScreen.classList.add('active');
}

// ========== АВТОРИЗАЦИЯ ==========
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Успешный вход
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('token', authToken);
            
            userInfo.textContent = `${currentUser.login} (${currentUser.role})`;
            showMainScreen();
            navigateTo('dashboard');
            loadDashboardData();
        } else {
            // Ошибка входа
            loginError.textContent = data.error || 'Неверный логин или пароль';
            loginError.classList.remove('hidden');
        }
    } catch (error) {
        loginError.textContent = 'Ошибка соединения с сервером';
        loginError.classList.remove('hidden');
    }
});

// Проверка токена при загрузке
async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/api/students`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            // Токен действителен
            showMainScreen();
            navigateTo('dashboard');
            loadDashboardData();
        } else {
            // Токен недействителен
            localStorage.removeItem('token');
            authToken = null;
            showLoginScreen();
        }
    } catch (error) {
        showLoginScreen();
    }
}

// Выход
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    authToken = null;
    currentUser = null;
    showLoginScreen();
});

// ========== НАВИГАЦИЯ ПО СТРАНИЦАМ ==========
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = link.dataset.page;
        navigateTo(page);
    });
});

function navigateTo(page) {
    // Обновляем активную ссылку в меню
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');
    
    // Показываем нужную страницу
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${page}`)?.classList.add('active');
    
    // Загружаем данные для страницы
    switch(page) {
        case 'dashboard': loadDashboardData(); break;
        case 'students': loadStudents(); break;
        case 'groups': loadGroups(); break;
        case 'attendance': initAttendancePage(); break;
        case 'reports': initReportsPage(); break;
    }
}

// ========== ЗАГРУЗКА ДАННЫХ ДЛЯ ПАНЕЛИ УПРАВЛЕНИЯ ==========
async function loadDashboardData() {
    try {
        const [studentsRes, groupsRes, attendanceRes] = await Promise.all([
            fetch(`${API_URL}/api/students`, { headers: authHeader() }),
            fetch(`${API_URL}/api/groups`, { headers: authHeader() }),
            fetch(`${API_URL}/api/attendance`, { headers: authHeader() })
        ]);
        
        const students = await studentsRes.json();
        const groups = await groupsRes.json();
        const attendance = await attendanceRes.json();
        
        document.getElementById('total-students').textContent = students.data?.length || 0;
        document.getElementById('total-groups').textContent = groups.data?.length || 0;
        document.getElementById('total-records').textContent = attendance.data?.length || 0;
    } catch (error) {
        console.error('Ошибка загрузки данных панели управления:', error);
    }
}

// ========== РАБОТА СО СТУДЕНТАМИ ==========
async function loadStudents(searchQuery = '') {
    const tbody = document.getElementById('students-tbody');
    tbody.innerHTML = '<tr><td colspan="5">Загрузка...</td></tr>';
    
    try {
        let url = `${API_URL}/api/students`;
        if (searchQuery) {
            url = `${API_URL}/api/students/search?q=${encodeURIComponent(searchQuery)}`;
        }
        
        const response = await fetch(url, { headers: authHeader() });
        const data = await response.json();
        const students = data.data || [];
        
        if (students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">Нет данных</td></tr>';
            return;
        }
        
        tbody.innerHTML = students.map(s => `
            <tr>
                <td>${s.id}</td>
                <td>${s.name}</td>
                <td>${s.group}</td>
                <td>${s.email}</td>
                <td>
                    <button class="btn btn-secondary" onclick="editStudent(${s.id})" style="padding:5px 10px; font-size:0.85rem;">✏️</button>
                    <button class="btn btn-logout" onclick="deleteStudent(${s.id})" style="padding:5px 10px; font-size:0.85rem;">🗑️</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="5">Ошибка загрузки</td></tr>';
    }
}

// Поиск студентов (ввод в поле поиска)
document.getElementById('student-search')?.addEventListener('input', (e) => {
    loadStudents(e.target.value);
});

// Кнопка "Добавить студента"
document.getElementById('add-student-btn')?.addEventListener('click', () => {
    openStudentModal();
});

// Модальное окно студента
const studentModal = document.getElementById('student-modal');
const studentForm = document.getElementById('student-form');

function openStudentModal(student = null) {
    document.getElementById('student-id').value = student?.id || '';
    document.getElementById('student-name').value = student?.name || '';
    document.getElementById('student-email').value = student?.email || '';
    document.getElementById('student-modal-title').textContent = student ? 'Редактировать студента' : 'Добавить студента';
    
    // Загружаем список групп в выпадающий список
    loadGroupsForSelect();
    
    studentModal.classList.remove('hidden');
}

// Закрытие модального окна
document.querySelector('.modal-close')?.addEventListener('click', () => {
    studentModal.classList.add('hidden');
});
document.querySelector('.modal-close-btn')?.addEventListener('click', () => {
    studentModal.classList.add('hidden');
});

// Сохранение студента (добавление или редактирование)
studentForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('student-id').value;
    const name = document.getElementById('student-name').value;
    const groupId = document.getElementById('student-group').value;
    const email = document.getElementById('student-email').value;
    
    const body = { name, group_id: parseInt(groupId), email };
    
    try {
        let response;
        if (id) {
            // Редактирование существующего
            response = await fetch(`${API_URL}/api/students/${id}`, {
                method: 'PUT',
                headers: { ...authHeader(), 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        } else {
            // Добавление нового
            response = await fetch(`${API_URL}/api/students`, {
                method: 'POST',
                headers: { ...authHeader(), 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        }
        
        if (response.ok) {
            studentModal.classList.add('hidden');
            loadStudents();
        } else {
            const err = await response.json();
            alert('Ошибка: ' + (err.error || 'Не удалось сохранить'));
        }
    } catch (error) {
        alert('Ошибка соединения с сервером');
    }
});

// Редактирование студента
async function editStudent(id) {
    try {
        const response = await fetch(`${API_URL}/api/students`, {
            headers: authHeader()
        });
        const data = await response.json();
        const student = data.data?.find(s => s.id === id);
        if (student) {
            openStudentModal(student);
        }
    } catch (error) {
        alert('Ошибка загрузки данных студента');
    }
}

// Удаление студента
async function deleteStudent(id) {
    if (!confirm('Вы уверены, что хотите удалить этого студента?')) return;
    
    try {
        const response = await fetch(`${API_URL}/api/students/${id}`, {
            method: 'DELETE',
            headers: authHeader()
        });
        
        if (response.ok) {
            loadStudents();
        } else {
            alert('Ошибка при удалении');
        }
    } catch (error) {
        alert('Ошибка соединения с сервером');
    }
}

// ========== РАБОТА С ГРУППАМИ ==========
async function loadGroups() {
    const container = document.getElementById('groups-list');
    
    try {
        const response = await fetch(`${API_URL}/api/groups`, {
            headers: authHeader()
        });
        const data = await response.json();
        const groups = data.data || [];
        
        if (groups.length === 0) {
            container.innerHTML = '<p>Группы не найдены</p>';
            return;
        }
        
        container.innerHTML = groups.map(g => `
            <div class="group-card">👥 ${g.name}</div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p>Ошибка загрузки</p>';
    }
}

async function loadGroupsForSelect() {
    try {
        const response = await fetch(`${API_URL}/api/groups`, {
            headers: authHeader()
        });
        const data = await response.json();
        const groups = data.data || [];
        
        const selects = ['student-group', 'att-group', 'view-group', 'report-group'];
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (!select) return;
            
            const currentValue = select.value;
            select.innerHTML = '<option value="">-- Выберите группу --</option>';
            groups.forEach(g => {
                select.innerHTML += `<option value="${g.id}">${g.name}</option>`;
            });
            select.value = currentValue;
        });
    } catch (error) {
        console.error('Ошибка загрузки групп:', error);
    }
}

// Кнопка "Добавить группу"
document.getElementById('add-group-btn')?.addEventListener('click', async () => {
    const name = prompt('Введите название новой группы (например, ИС-23):');
    if (!name) return;
    
    try {
        const response = await fetch(`${API_URL}/api/groups`, {
            method: 'POST',
            headers: { ...authHeader(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        
        if (response.ok) {
            loadGroups();
            loadGroupsForSelect();
        } else {
            const err = await response.json();
            alert('Ошибка: ' + (err.error || 'Не удалось создать группу'));
        }
    } catch (error) {
        alert('Ошибка соединения с сервером');
    }
});

// ========== РАБОТА С ПОСЕЩАЕМОСТЬЮ ==========
async function initAttendancePage() {
    await loadGroupsForSelect();
    document.getElementById('att-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('view-date').value = new Date().toISOString().split('T')[0];
}

// Загрузка студентов для отметки
document.getElementById('load-students-btn')?.addEventListener('click', async () => {
    const groupId = document.getElementById('att-group').value;
    const date = document.getElementById('att-date').value;
    
    if (!groupId || !date) {
        alert('Выберите группу и дату');
        return;
    }
    
    try {
        // Получаем студентов группы
        const response = await fetch(`${API_URL}/api/students/search?q=${document.getElementById('att-group').selectedOptions[0].text}`, {
            headers: authHeader()
        });
        const data = await response.json();
        const students = data.data || [];
        
        const tbody = document.getElementById('attendance-tbody');
        
        if (students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2">Студенты не найдены в этой группе</td></tr>';
        } else {
            tbody.innerHTML = students.map(s => `
                <tr>
                    <td>${s.name}</td>
                    <td>
                        <select class="attendance-status" data-student-id="${s.id}">
                            <option value="present">✅ Присутствует</option>
                            <option value="absent">❌ Отсутствует</option>
                        </select>
                    </td>
                </tr>
            `).join('');
        }
        
        document.getElementById('attendance-marking-area').classList.remove('hidden');
    } catch (error) {
        alert('Ошибка загрузки студентов');
    }
});

// Отметить всех присутствующими
document.getElementById('mark-all-present')?.addEventListener('click', () => {
    document.querySelectorAll('.attendance-status').forEach(select => {
        select.value = 'present';
    });
});

// Сохранить посещаемость
document.getElementById('save-attendance')?.addEventListener('click', async () => {
    const date = document.getElementById('att-date').value;
    const statuses = document.querySelectorAll('.attendance-status');
    
    const messageDiv = document.getElementById('attendance-message');
    
    try {
        for (const select of statuses) {
            const studentId = select.dataset.studentId;
            const status = select.value;
            
            await fetch(`${API_URL}/api/attendance`, {
                method: 'POST',
                headers: { ...authHeader(), 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: parseInt(studentId),
                    date: date,
                    status: status
                })
            });
        }
        
        messageDiv.textContent = '✅ Посещаемость успешно сохранена!';
        messageDiv.className = 'message success';
        messageDiv.classList.remove('hidden');
    } catch (error) {
        messageDiv.textContent = '❌ Ошибка при сохранении';
        messageDiv.className = 'message error';
        messageDiv.classList.remove('hidden');
    }
});

// Просмотр посещаемости
document.getElementById('view-attendance-btn')?.addEventListener('click', async () => {
    const date = document.getElementById('view-date').value;
    const groupId = document.getElementById('view-group').value;
    
    try {
        let url = `${API_URL}/api/attendance?date=${date}`;
        if (groupId) url += `&group_id=${groupId}`;
        
        const response = await fetch(url, { headers: authHeader() });
        const data = await response.json();
        const records = data.data || [];
        
        const tbody = document.getElementById('attendance-view-tbody');
        
        if (records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">Записи не найдены</td></tr>';
            return;
        }
        
        tbody.innerHTML = records.map(r => `
            <tr>
                <td>${r.student_name}</td>
                <td>${r.group_name}</td>
                <td>${r.date}</td>
                <td class="${r.status === 'present' ? 'status-present' : 'status-absent'}">
                    ${r.status === 'present' ? '✅ Присутствует' : '❌ Отсутствует'}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        alert('Ошибка загрузки данных');
    }
});

// ========== РАБОТА С ОТЧЁТАМИ ==========
async function initReportsPage() {
    await loadGroupsForSelect();
}

document.getElementById('generate-report-btn')?.addEventListener('click', async () => {
    const groupId = document.getElementById('report-group').value;
    
    if (!groupId) {
        alert('Выберите группу');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/attendance/stats?group_id=${groupId}`, {
            headers: authHeader()
        });
        const data = await response.json();
        
        document.getElementById('report-title').textContent = `Отчёт по группе: ${data.group_name}`;
        
        const tbody = document.getElementById('report-tbody');
        const stats = data.students_stats || [];
        
        tbody.innerHTML = stats.map(s => `
            <tr>
                <td>${s.student_name}</td>
                <td>${s.total_lessons}</td>
                <td>${s.attended}</td>
                <td>${s.missed}</td>
                <td>
                    <span class="${s.attendance_percentage >= 70 ? 'status-present' : 'status-absent'}">
                        ${s.attendance_percentage}%
                    </span>
                </td>
            </tr>
        `).join('');
        
        document.getElementById('report-area').classList.remove('hidden');
    } catch (error) {
        alert('Ошибка формирования отчёта');
    }
});

// Экспорт отчёта в CSV
document.getElementById('export-report-btn')?.addEventListener('click', () => {
    const rows = document.querySelectorAll('#report-table tr');
    let csv = 'Студент,Всего занятий,Посетил,Пропустил,% посещаемости\n';
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('th, td');
        const rowData = Array.from(cols).map(c => c.textContent.trim()).join(',');
        csv += rowData + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'отчёт_посещаемости.csv';
    link.click();
});

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
function authHeader() {
    return { 'Authorization': `Bearer ${authToken}` };
}