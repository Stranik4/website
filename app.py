import json
from flask import Flask, render_template, redirect, url_for, session, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import calendar
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mrak.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "cb02820a3e94d72c9f950ee10ef7e3f7a35b3f5b"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# //////////Создание базы данных//////////////////////////
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    second_name = db.Column(db.String, nullable=False)
    tel = db.Column(db.String, nullable=False)
    login = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    title_service = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    booking_date = db.Column(db.String, nullable=False)
    booking_time = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default="Запланировано")
    created_at = db.Column(db.String, nullable=False)
    
    service = db.relationship('Service', backref='bookings')
    user = db.relationship('User', backref='bookings')


def init_services():
    services_data = [
        # Тонировка
        {"title_service": "Атермальная плёнка (лобовое)", "price": 4000, "time": "2 час. 30 мин.", "category": "Тонировка"},
        {"title_service": "Атермальная тонировка (лобовое - хамелеон)", "price": 7000, "time": "2 час. 30 мин.", "category": "Тонировка"},
        {"title_service": "Атермальная тонировка (Боковые Стёкла - хамелеон)", "price": 3500, "time": "2 час.", "category": "Тонировка"},
        {"title_service": "Атермальная тонировка (Боковых стекл)", "price": 2500, "time": "2 час.", "category": "Тонировка"},
        {"title_service": "Тонировка задней полусферы (чёрная)", "price": 5000, "time": "4 час.", "category": "Тонировка"},
        {"title_service": "Тонировка лобового стекла (чёрная)", "price": 3000, "time": "2 час. 30 мин.", "category": "Тонировка"},
        {"title_service": "Тонировка передних стёкл (чёрная)", "price": 2000, "time": "2 час.", "category": "Тонировка"},
        {"title_service": "Тонировка фар", "price": 5000, "time": "2 час.", "category": "Тонировка"},
        
        # Полировка
        {"title_service": "Полировка авто", "price": 10000, "time": "6 час.", "category": "Полировка"},
        {"title_service": "Полировка фар", "price": 2500, "time": "2 час.", "category": "Полировка"},
        {"title_service": "Нанесение ВОСК", "price": 3000, "time": "30 мин.", "category": "Полировка"},
        {"title_service": "Нанесение керамики", "price": 5000, "time": "30 мин.", "category": "Полировка"},
        
        # Бронеплёнка
        {"title_service": "Бронеплёнка: Фары", "price": 5000, "time": "2 час.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Капот", "price": 17000, "time": "2 час.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Бампер", "price": 17000, "time": "2 час.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Полоса", "price": 4000, "time": "2 час.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Стойки вдоль лобового", "price": 4000, "time": "2 час.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Зеркала", "price": 3000, "time": "30 мин.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Пороги 4 шт.", "price": 5000, "time": "30 мин.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Зона погрузки", "price": 4000, "time": "30 мин.", "category": "Бронеплёнка"},
        {"title_service": "Бронеплёнка: Крылья", "price": 15000, "time": "30 мин.", "category": "Бронеплёнка"},
    ]
    
    if Service.query.count() == 0:
        for service_data in services_data:
            service = Service(**service_data)
            db.session.add(service)
        db.session.commit()
        print("Услуги добавлены в базу данных")

# Создание администратора
def create_admin_user():
    admin_email = "admin@mrak.ru"
    admin_user = User.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        admin_password = "admin123"
        hash_password = generate_password_hash(admin_password)
        
        admin = User(
            name="Администратор",
            second_name="Системы",
            tel="+79990000000",
            login="admin",
            email=admin_email,
            password=admin_password,
            hash=hash_password,
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print(f"Администратор создан: {admin_email} / {admin_password}")

# Генерация данных календаря
def get_calendar_data(year=None, month=None):
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    
    formatted_days = []
    for week in month_days:
        formatted_week = []
        for day in week:
            formatted_week.append(day if day != 0 else None)
        formatted_days.append(formatted_week)
    
    month_names = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }
    
    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    
    return {
        'month_name': month_names[month],
        'year': year,
        'month': month,
        'days': formatted_days,
        'day_names': day_names
    }

# Форматирование даты в русский формат
def format_selected_date(date_str):
    """Форматирование выбранной даты в русский формат"""
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month_names = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        
        day_names = ["Понедельник", "Вторник", "Среда", "Четверг", 
                    "Пятница", "Суббота", "Воскресенье"]
        
        day_name = day_names[date_obj.weekday()]
        month_name = month_names[date_obj.month]
        
        return f"{day_name}, {date_obj.day} {month_name}"
    except:
        return date_str

# временя услуги в минуты
def get_service_duration_minutes(service_time):
    import re
    
    # Ищем числа перед словами "час" и "мин"
    hours_match = re.search(r'(\d+)\s*час', service_time)
    minutes_match = re.search(r'(\d+)\s*мин', service_time)
    
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    
    return hours * 60 + minutes

# Получение заблокированных временных слотов
def get_blocked_times(booking_date, service_duration_minutes):
    bookings = Booking.query.filter(
        Booking.booking_date == booking_date,
        Booking.status.in_(["Запланировано", "Подтверждено"])
    ).all()
    
    blocked_times = []
    
    for booking in bookings:
        service = Service.query.get(booking.service_id)
        if service:
            service_minutes = get_service_duration_minutes(service.time)
            start_time = datetime.strptime(booking.booking_time, '%H:%M')
            end_time = start_time + timedelta(minutes=service_minutes)
            
            # Блокировка каждого 30-минутного слота в течение услуги
            current_time = start_time
            while current_time < end_time:
                time_str = current_time.strftime('%H:%M')
                blocked_times.append(time_str)
                current_time += timedelta(minutes=30)
    
    return blocked_times

# Получение доступных времен с учетом продолжительности услуги
def get_available_times_with_duration(selected_date, service_duration_minutes, booked_times):
    all_times = [
        "09:00", "09:30", "10:00", "10:30",
        "11:00", "11:30", "12:00", "12:30",
        "13:00", "13:30", "14:00", "14:30",
        "15:00", "15:30", "16:00", "16:30",
        "17:00", "17:30", "18:00", "18:30"
    ]
    
    duration_blocked_times = get_blocked_times(selected_date, service_duration_minutes)
    all_blocked_times = set(booked_times + duration_blocked_times)
    
    available_times = []
    
    for time_slot in all_times:
        if time_slot not in all_blocked_times:
            start_time = datetime.strptime(time_slot, '%H:%M')
            end_time = start_time + timedelta(minutes=service_duration_minutes)
            
            # Проверка, что услуга заканчивается до конца рабочего дня
            if end_time <= datetime.strptime('19:00', '%H:%M'):
                available_times.append(time_slot)
    
    return available_times

# Проверка, является ли дата прошедшей
def is_date_in_past(date_str):
    """Проверяет, является ли дата прошедшей"""
    if not date_str:
        return True
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        return date_obj < datetime.now().date()
    except:
        return True

# Проверка, является ли время прошедшим для сегодняшнего дня
def is_time_in_past_for_today(time_str):
    """Проверяет, является ли время прошедшим для сегодняшнего дня"""
    if not time_str:
        return True
    
    try:
        today = datetime.now().date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        current_time = datetime.now().time()
        return time_obj < current_time
    except:
        return True


# ////////// Декоратор для проверки администратора //////////
def admin_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Для доступа к админ-панели необходимо авторизоваться", "error")
            return redirect(url_for('profil'))
        
        user = User.query.get(session["user_id"])
        if not user or not user.is_admin:
            flash("У вас нет прав доступа к админ-панели", "error")
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    
    return decorated_function


# ////////// Основные маршруты //////////
# Главная страница
@app.route("/")
def index():
    services = Service.query.all()
    if not services:
        flash("Услуги временно недоступны", "error")
    return render_template("index.html", services=services)

# Страница деталей услуги и запись на нее
@app.route("/service/<int:service_id>", methods=["GET", "POST"])
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    selected_date = request.args.get('selected_date', '')
    
    # Проверка, является ли пользователь администратором
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user and user.is_admin:
            flash("Администраторы не могут записываться на услуги", "error")
            return redirect(url_for('admin_panel'))

    # Получение месяца и года для календаря
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    # Если месяц и год не указаны, используем текущие
    now = datetime.now()
    if not month or not year:
        month = now.month
        year = now.year
    
    service_duration_minutes = get_service_duration_minutes(service.time)
    
    # Обработка POST запроса - создание записи
    if request.method == "POST":
        if "user_id" not in session:
            flash("Для записи на услугу необходимо авторизоваться", "error")
            return redirect(url_for('profil'))

        # Проверка, что пользователь не администратор
        user = User.query.get(session["user_id"])
        if user and user.is_admin:
            flash("Администраторы не могут записываться на услуги", "error")
            return redirect(url_for('admin_panel'))    
        
        booking_date = request.form.get("booking_date")
        booking_time = request.form.get("booking_time")
        
        if not booking_date or not booking_time:
            flash("Пожалуйста, выберите дату и время", "error")
            return redirect(url_for('service_detail', service_id=service.id, selected_date=selected_date, month=month, year=year))
        
        # ПРОВЕРКА: НЕЛЬЗЯ ЗАПИСЫВАТЬСЯ НА ПРОШЕДШУЮ ДАТУ
        selected_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        current_date = datetime.now().date()
        
        # Если дата в прошлом
        if selected_date_obj < current_date:
            flash("Нельзя записаться на прошедшую дату", "error")
            return redirect(url_for('service_detail', service_id=service.id, selected_date=selected_date, month=month, year=year))
        
        # Если дата сегодня, проверяем время
        if selected_date_obj == current_date:
            selected_time = datetime.strptime(booking_time, '%H:%M').time()
            current_time = datetime.now().time()
            if selected_time <= current_time:
                flash("Нельзя записаться на прошедшее время", "error")
                return redirect(url_for('service_detail', service_id=service.id, selected_date=selected_date, month=month, year=year))
        
        # Проверка на занятость времени
        existing_booking = Booking.query.filter(
            Booking.booking_date == booking_date,
            Booking.booking_time == booking_time,
            Booking.status.in_(["Запланировано", "Подтверждено"])
        ).first()
        
        if existing_booking:
            flash("Это время уже занято. Пожалуйста, выберите другое время.", "error")
            return redirect(url_for('service_detail', service_id=service.id, selected_date=selected_date, month=month, year=year))
        
        # Проверка на пересечение с другими записями
        blocked_times = get_blocked_times(booking_date, service_duration_minutes)
        if booking_time in blocked_times:
            flash("Это время пересекается с другой записью. Пожалуйста, выберите другое время.", "error")
            return redirect(url_for('service_detail', service_id=service.id, selected_date=selected_date, month=month, year=year))
        
        # Создание новой записи
        booking = Booking(
            user_id=session["user_id"],
            service_id=service.id,
            booking_date=booking_date,
            booking_time=booking_time,
            created_at=datetime.now().strftime("%d.%m.%Y %H:%M")
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Расчет времени окончания услуги
        start_time = datetime.strptime(booking_time, '%H:%M')
        end_time = start_time + timedelta(minutes=service_duration_minutes)
        end_time_str = end_time.strftime('%H:%M')
        
        flash(f"Вы успешно записались на услугу '{service.title_service}'! Время: {booking_time}-{end_time_str}", "success")
        return redirect(url_for('profil'))
    
    # Обработка GET запроса - отображение страницы
    calendar_data = get_calendar_data(year, month)
    formatted_date = format_selected_date(selected_date)
    booked_times = []
    
    # Получение занятых времен для выбранной даты
    if selected_date:
        bookings = Booking.query.filter(
            Booking.booking_date == selected_date,
            Booking.status.in_(["Запланировано", "Подтверждено"])
        ).all()
        booked_times = [booking.booking_time for booking in bookings]
    
    # Получение доступных времен
    available_times = []
    if selected_date:
        # Проверяем, не прошедшая ли дата
        if not is_date_in_past(selected_date):
            available_times = get_available_times_with_duration(selected_date, service_duration_minutes, booked_times)
            
            # Если дата сегодня, убираем прошедшее время
            if datetime.strptime(selected_date, '%Y-%m-%d').date() == datetime.now().date():
                available_times = [time for time in available_times if not is_time_in_past_for_today(time)]
    
    # Расчет следующего и предыдущего месяца для навигации
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year = year + 1
    
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year = year - 1
    
    return render_template(
        "service_detail.html",
        service=service,
        calendar_data=calendar_data,
        available_times=available_times,
        selected_date=selected_date,
        formatted_date=formatted_date,
        booked_times=booked_times,
        service_duration_minutes=service_duration_minutes,
        next_month=next_month,
        next_year=next_year,
        prev_month=prev_month,
        prev_year=prev_year,
        is_date_in_past=is_date_in_past,
        is_time_in_past_for_today=is_time_in_past_for_today
    )

# Отмена записи пользователем
@app.route("/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):
    if "user_id" in session:
        booking = Booking.query.filter_by(id=booking_id, user_id=session["user_id"]).first()
        if booking:
            db.session.delete(booking)
            db.session.commit()
            flash("Запись успешно отменена", "success")
    return redirect(url_for('profil'))

# Удаление записи из истории
@app.route("/delete_from_history/<int:booking_id>")
def delete_from_history(booking_id):
    if "user_id" in session:
        booking = Booking.query.filter_by(id=booking_id, user_id=session["user_id"]).first()
        if booking and booking.status in ["Выполнено", "Отменено"]:
            db.session.delete(booking)
            db.session.commit()
            flash("Запись удалена из истории", "success")
    return redirect(url_for('profil'))

# Очистка всей истории записей
@app.route("/clear_history", methods=["POST"])
def clear_history():
    if "user_id" in session:
        # Удаляем все записи пользователя со статусом "Выполнено" или "Отменено"
        history_bookings = Booking.query.filter_by(user_id=session["user_id"]).filter(
            Booking.status.in_(["Выполнено", "Отменено"])
        ).all()
        
        count = 0
        for booking in history_bookings:
            db.session.delete(booking)
            count += 1
        
        db.session.commit()
        flash(f"Удалено записей из истории: {count}", "success")
    
    return redirect(url_for('profil'))

# ////////// Админские маршруты //////////
# Главная страница админ-панели
@app.route("/admin")
@admin_required
def admin_panel():
    total_services = Service.query.count()
    total_bookings = Booking.query.count()
    
    recent_bookings = db.session.query(Booking, Service, User)\
        .join(Service, Booking.service_id == Service.id)\
        .join(User, Booking.user_id == User.id)\
        .order_by(Booking.created_at.desc())\
        .limit(10)\
        .all()
    
    popular_services = get_popular_services(limit=5)

    return render_template("admin_panel.html",total_services=total_services,total_bookings=total_bookings,recent_bookings=recent_bookings, popular_services=popular_services)

# Управление услугами
@app.route("/admin/services")
@admin_required
def admin_services():
    services = Service.query.all()
    return render_template("admin_services.html", services=services)

# Добавление новой услуги
@app.route("/admin/service/add", methods=["GET", "POST"])
@admin_required
def admin_add_service():
    if request.method == "POST":
        title_service = request.form.get("title_service")
        price = request.form.get("price")
        time = request.form.get("time")
        category = request.form.get("category")
        
        if not all([title_service, price, time, category]):
            flash("Все поля обязательны для заполнения", "error")
            return redirect(url_for('admin_add_service'))
        
        try:
            price = int(price)
        except ValueError:
            flash("Цена должна быть числом", "error")
            return redirect(url_for('admin_add_service'))
        
        # Создание новой услуги
        service = Service(
            title_service=title_service,
            price=price,
            time=time,
            category=category
        )
        
        db.session.add(service)
        db.session.commit()
        flash("Услуга успешно добавлена", "success")
        return redirect(url_for('admin_services'))
    
    return render_template("admin_add_service.html")

# Редактирование услуги
@app.route("/admin/service/edit/<int:service_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    if request.method == "POST":
        service.title_service = request.form.get("title_service")
        service.price = int(request.form.get("price"))
        service.time = request.form.get("time")
        service.category = request.form.get("category")
        
        db.session.commit()
        flash("Услуга успешно обновлена", "success")
        return redirect(url_for('admin_services'))
    
    return render_template("admin_edit_service.html", service=service)

# Удаление услуги
@app.route("/admin/service/delete/<int:service_id>")
@admin_required
def admin_delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    bookings_count = Booking.query.filter_by(service_id=service_id).count()
    
    # Проверка на наличие связанных записей
    if bookings_count > 0:
        flash("Нельзя удалить услугу, так как есть связанные записи", "error")
        return redirect(url_for('admin_services'))
    
    db.session.delete(service)
    db.session.commit()
    flash("Услуга успешно удалена", "success")
    return redirect(url_for('admin_services'))

# Просмотр всех записей
@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    bookings = db.session.query(Booking, Service, User)\
        .join(Service, Booking.service_id == Service.id)\
        .join(User, Booking.user_id == User.id)\
        .order_by(Booking.created_at.desc())\
        .all()
    
    return render_template("admin_bookings.html", bookings=bookings)

# Статус записи
@app.route("/admin/booking/update_status/<int:booking_id>", methods=["POST"])
@admin_required
def admin_update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get("status")
    
    if new_status in ["Запланировано", "Подтверждено", "Выполнено", "Отменено"]:
        booking.status = new_status
        db.session.commit()
        flash("Статус записи обновлен", "success")
    
    return redirect(url_for('admin_bookings'))

# Удаление записи администратором
@app.route("/admin/booking/delete/<int:booking_id>")
@admin_required
def admin_delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Запись успешно удалена", "success")
    return redirect(url_for('admin_bookings'))


# /////////// Вход и регистрация///////////////////////
@app.route("/profil", methods=["GET", "POST"])
def profil():
    user_bookings = []
    user_history = []
    user_info = []
    email = request.form.get("email")
    password = request.form.get("password")
    
    # Проверка авторизации
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.hash, password):
        session["user_id"] = user.id
        session["is_admin"] = user.is_admin
        flash("Успешный вход!", "success")
        
        if user.is_admin:
            return redirect(url_for('admin_panel'))
    elif email and password:  # Только если форма отправлена
        flash("Неверный логин или пароль", "error")
    
    # Отображение данных пользователя, если авторизован
    if "user_id" in session:
        db_user = User.query.get(session["user_id"])
        user_info = [db_user.name, db_user.email]

        if db_user.is_admin:
            return render_template('profil.html', 
                                 bookings=[], 
                                 history_bookings=[], 
                                 user_info=user_info,
                                 is_admin=True)

        # Получаем все записи пользователя
        all_bookings = db.session.query(Booking, Service)\
            .join(Service, Booking.service_id == Service.id)\
            .filter(Booking.user_id == session["user_id"])\
            .order_by(Booking.booking_date.desc())\
            .all()
        
        # Разделяем на текущие и исторические записи
        for booking, service in all_bookings:
            if booking.status in ["Выполнено", "Отменено"]:
                user_history.append((booking, service))
            else:
                user_bookings.append((booking, service))
        
        return render_template('profil.html', bookings=user_bookings, history_bookings=user_history,user_info=user_info)
    else:
        return render_template('profil.html', bookings=[], history_bookings=[], user_info=[])

# Регистрация нового пользователя
@app.route("/registr", methods=["GET", "POST"])
def registr():
    email = request.form.get("email")
    login = request.form.get("login")
    password = request.form.get("password")
    name = request.form.get("name")
    second_name = request.form.get("second_name")
    tel = request.form.get("tel")
    
    if name == None:
        flash("Введите имя", "error")
    elif not name.isalpha():
        flash("Имя должно состоять из букв", "error")
    elif len(name) < 4:
        flash("Имя должно содержать не менее 4 символов", "error")
    elif len(password) < 4:
        flash("Пароль должен содержать не менее 4 символов", "error")
    else:
        hash_pasword = generate_password_hash(password)
        check_user = User.query.filter_by(email=email).first()
        
        if check_user:
            flash("такой пользователь уже существует", "error")
        else:
            # Создание нового пользователя
            user = User(
                name=name,
                second_name=second_name,
                tel=tel,
                login=login,
                email=email,
                password=password,
                hash=hash_pasword
            )
            
            db.session.add(user)
            db.session.commit()
            session["is_admin"] = user.is_admin
            return redirect(url_for("profil"))
    
    return render_template("registr.html")

def get_popular_services(limit=5):
    """Получение самых популярных услуг по количеству записей"""
    popular = db.session.query(
        Service,
        db.func.count(Booking.id).label('booking_count')
    ).join(Booking, Service.id == Booking.service_id)\
     .filter(Booking.status.in_(["Выполнено", "Подтверждено", "Запланировано"]))\
     .group_by(Service.id)\
     .order_by(db.desc('booking_count'))\
     .limit(limit)\
     .all()
    
    return popular

@app.route("/logout")
def logout():
    if "user_id" in session:
        session.clear()
    return redirect(url_for("profil"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        init_services()
        create_admin_user()
    app.run(host='127.0.0.1', port=8000, debug=True)