from flask import Flask, render_template, request, jsonify, make_response, abort, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
from dotenv import dotenv_values
from datetime import datetime, timedelta
import uuid
import geoip2.database
from time import sleep


config = dotenv_values(".env")
GOOGLE_CAPCHAV3_SITEKEY = config["GOOGLE_CAPCHAV3_SITEKEY"]
GOOGLE_CAPCHAV3_SECRET = config["GOOGLE_CAPCHAV3_SECRET"]
SCHEDULE_WEEKS_FORWARD = int(config.get("SCHEDULE_WEEKS_FORWARD", 2))
DB_PATH = config["DB_PATH"]
GEOIP_DB_PATH = config["GEOIP_DB_PATH"]
ALLOWED_FROM_COUNTRY = config["ALLOWED_FROM_COUNTRY"]
ALLOW_ALL_IP = config["ALLOW_ALL_IP"]
MAX_BOOKINGS_PER_CLIENT = int(config["MAX_BOOKINGS_PER_CLIENT"])
ADMIN_PASSWORD = config["ADMIN_PASSWORD"]
APP_SECRET_KEY = config["APP_SECRET_KEY"]


app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

from models import db, Schedule, Booking
db.init_app(app)

reader = geoip2.database.Reader(GEOIP_DB_PATH)


def get_real_ip():
    return request.headers.get('X-Real-IP', request.headers.get('X-Forwarded-For', request.remote_addr))


def is_ip_from_country(ip=None, country_iso_code=ALLOWED_FROM_COUNTRY):
    if ALLOW_ALL_IP:
        return True
    if ip is None:
        ip = get_real_ip()
    if ip in ['127.0.0.1', 'localhost']:
        return True
    try:
        response = reader.country(ip)
        print(f'{ip=} {response=}')
        return response.country.iso_code == country_iso_code
    except Exception as e:
        print(f"Error determine IP: {e}")
        return False

@app.before_request
def restrict_access():
    ip = request.remote_addr
    if not is_ip_from_country(ip):
        abort(403)

# Функция для очистки старых бронирований (от вчера и ранее)
def clean_old_bookings():
    today = datetime.today().date()
    # Удаляем все бронирования, где дата меньше сегодняшней
    Booking.query.filter(Booking.booking_date < today).delete(synchronize_session=False)
    db.session.commit()

# Функция для вычисления ближайшей даты проведения занятия (>= start_date)
def get_next_occurrence(day_str, time_str, start_date):
    weekdays = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    target_weekday = weekdays.get(day_str)
    if target_weekday is None:
        return start_date  # Если день не распознан, возвращаем start_date

    target_time = datetime.strptime(time_str, "%H:%M").time()
    candidate = datetime.combine(start_date, target_time)
    days_ahead = target_weekday - start_date.weekday()
    if days_ahead < 0:
        days_ahead += 7
    next_occurrence = candidate + timedelta(days=days_ahead)
    return next_occurrence.date()


# Генерирует все сессии для занятия в диапазоне [start_date, end_date]
def get_occurrences_in_range(schedule_item, start_date, end_date):
    occurrences = []
    first_occurrence = get_next_occurrence(schedule_item.day, schedule_item.time, start_date)
    occurrence = first_occurrence
    while occurrence <= end_date:
        occurrences.append(occurrence)
        occurrence = occurrence + timedelta(days=7)
    return occurrences

@app.route('/')
def index():
    clean_old_bookings()  # Очистка старых бронирований
    client_id = request.cookies.get("client_id")
    if not client_id:
        client_id = str(uuid.uuid4())
    
    today = datetime.today().date()
    end_date = today + timedelta(days=SCHEDULE_WEEKS_FORWARD * 7)
    
    schedule_items = Schedule.query.all()
    formatted_schedule = []
    
    # Для каждого шаблонного занятия генерируем все его сессии в заданном периоде
    for session in schedule_items:
        occurrences = get_occurrences_in_range(session, today, end_date)
        for occ in occurrences:
            total_slots = session.max_slots
            bookings = Booking.query.filter_by(schedule_id=session.id, booking_date=occ).all()
            booked_count = len(bookings)
            free_count = total_slots - booked_count

            slots = []
            booking_id = None
            for booking in bookings:
                if booking.client_id == client_id:
                    slots.append("You")
                    booking_id = booking.id
                else:
                    slots.append("Booked")
            slots += ["Free"] * free_count

            formatted_schedule.append({
                'id': session.id,
                'day': session.day,
                'time': session.time,
                'title': session.title,
                'duration': session.duration,
                'slots': slots,
                'booking_id': booking_id,
                'occurrence_date': occ.strftime("%Y-%m-%d")
            })
    
    # Сортируем по дате проведения и времени
    formatted_schedule.sort(key=lambda x: (x["occurrence_date"], x["time"]))
    
    response = make_response(render_template('index-notablegdpr.html', schedule=formatted_schedule, recaptcha_sitekey=GOOGLE_CAPCHAV3_SITEKEY))
    response.set_cookie("client_id", client_id, max_age=365*24*60*60)
    return response

@app.route('/schedule', methods=['GET'])
def get_schedule():
    clean_old_bookings()  # Очистка старых бронирований
    today = datetime.today().date()
    end_date = today + timedelta(days=SCHEDULE_WEEKS_FORWARD * 7)
    schedule_items = Schedule.query.all()
    schedule_data = []
    for session in schedule_items:
        occurrences = get_occurrences_in_range(session, today, end_date)
        for occ in occurrences:
            booked_slots = Booking.query.filter_by(schedule_id=session.id, booking_date=occ).count()
            free_slots = session.max_slots - booked_slots
            slots_status = ["Booked"] * booked_slots + ["Free"] * free_slots

            schedule_data.append({
                "day": session.day,
                "time": session.time,
                "title": session.title,
                "duration": session.duration,
                "slots": slots_status,
                "occurrence_date": occ.strftime("%Y-%m-%d")
            })
    # Можно отсортировать данные по дате и времени
    schedule_data.sort(key=lambda x: (x["occurrence_date"], x["time"]))
    return jsonify(schedule_data)

def verify_recaptcha(token):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        'secret': GOOGLE_CAPCHAV3_SECRET,
        'response': token
    }
    response = requests.post(url, data=data).json()
    score = response.get("score", 0)
    print(f'{score=}')
    return response.get("success", False), score

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    recaptcha_token = data.get('recaptcha_token', '')

    success, score = verify_recaptcha(recaptcha_token)
    if not success or score < 0.5:
        return jsonify({"status": "error", "message": "I suppose you are not a human."}), 403

    name = data.get("name")
    phone = data.get("phone")
    schedule_id = data.get("schedule_id")
    booking_date_str = data.get("booking_date")
    client_id = data.get("client_id")
    
    if not booking_date_str:
        return jsonify({"status": "error", "message": "Booking date is required"}), 400
    try:
        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid booking date format"}), 400

    # session_obj = Schedule.query.get(schedule_id)
    session_obj = db.session.get(Schedule, schedule_id)
    if not session_obj:
        return jsonify({"status": "error", "message": "Schedule not found"}), 404

    # Ограничение бронирований для одного клиента (будущие бронирования)
    today = datetime.today().date()
    client_bookings = Booking.query.filter(
        Booking.client_id == client_id,
        Booking.booking_date >= today
    ).count()
    if client_bookings >= MAX_BOOKINGS_PER_CLIENT:
        return jsonify({
            "status": "error", 
            "message": "You have reached the maximum number of bookings allowed."
        }), 400

    new_booking = Booking(
        schedule_id=schedule_id,
        booking_date=booking_date,
        client_name=name,
        client_phone=phone,
        client_id=client_id
    )
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({"status": "success"})

@app.route('/unbook', methods=['POST'])
def unbook():
    data = request.json
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({'status': 'error', 'message': 'Booking ID is required'}), 400

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'status': 'error', 'message': 'Booking not found'}), 404

    db.session.delete(booking)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Booking canceled'})



@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            sleep(15)
            error = "Invalid password"
            return render_template("admin_login.html", error=error)
    return render_template("admin_login.html")


@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    today = datetime.today().date()
    end_date = today + timedelta(days=SCHEDULE_WEEKS_FORWARD * 7)
    schedule_items = Schedule.query.all()
    admin_sessions = []  # список сессий для админа
    for s_item in schedule_items:
        occurrences = get_occurrences_in_range(s_item, today, end_date)
        for occ in occurrences:
            bookings = Booking.query.filter_by(schedule_id=s_item.id, booking_date=occ).all()
            booking_details = [f"{b.client_name} ({b.client_phone})" for b in bookings]
            admin_sessions.append({
                'booking_date': occ,  # объект даты
                'time': s_item.time,
                'title': s_item.title,
                'duration': s_item.duration,
                'bookings': booking_details
            })
    # Сортируем по дате и времени занятия
    admin_sessions.sort(key=lambda x: (x['booking_date'], x['time']))
    
    # Группируем по booking_date
    grouped_sessions = {}
    for s in admin_sessions:
        date_str = s['booking_date'].strftime("%Y-%m-%d")
        if date_str not in grouped_sessions:
            grouped_sessions[date_str] = {
                'date_obj': s['booking_date'],
                'sessions': []
            }
        grouped_sessions[date_str]['sessions'].append(s)
    
    # Преобразуем в список, отсортированный по дате
    grouped_sessions_list = sorted(grouped_sessions.items(), key=lambda x: x[0])
    
    return render_template("admin.html", grouped_sessions=grouped_sessions_list)



@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.route('/admin-schedule')
def admin_schedule():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    schedule_items = Schedule.query.all()
    day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
    # Сортируем по дню недели (согласно day_order) и затем по времени
    schedule_items.sort(key=lambda item: (day_order.get(item.day, 99), item.time))
    return render_template("admin_schedule.html", schedule_items=schedule_items)


@app.route('/admin-schedule/add', methods=['POST'])
def admin_schedule_add():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    day = request.form.get("day")
    time = request.form.get("time")
    title = request.form.get("title")
    duration = request.form.get("duration")
    max_slots = request.form.get("max_slots", 5)
    # Простой контроль (можно добавить дополнительные проверки)
    if not (day and time and title and duration):
        return "Missing fields", 400
    new_schedule = Schedule(day=day, time=time, title=title, duration=int(duration), max_slots=int(max_slots))
    db.session.add(new_schedule)
    db.session.commit()
    return redirect(url_for("admin_schedule"))

@app.route('/admin-schedule/edit/<int:schedule_id>', methods=['POST'])
def admin_schedule_edit(schedule_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    schedule_obj = db.session.get(Schedule, schedule_id)
    if not schedule_obj:
        return "Schedule not found", 404
    schedule_obj.day = request.form.get("day")
    schedule_obj.time = request.form.get("time")
    schedule_obj.title = request.form.get("title")
    schedule_obj.duration = int(request.form.get("duration"))
    schedule_obj.max_slots = int(request.form.get("max_slots", schedule_obj.max_slots))
    db.session.commit()
    return redirect(url_for("admin_schedule"))

@app.route('/admin-schedule/delete/<int:schedule_id>', methods=['POST'])
def admin_schedule_delete(schedule_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    schedule_obj = db.session.get(Schedule, schedule_id)
    if not schedule_obj:
        return "Schedule not found", 404
    db.session.delete(schedule_obj)
    db.session.commit()
    return redirect(url_for("admin_schedule"))



@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
    
# if __name__ == '__main__':
#     from waitress import serve  # pip install waitress
#     serve(app, host="0.0.0.0", port=5001)