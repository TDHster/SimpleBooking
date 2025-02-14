#create_db.py

from app import app, db
from models import Schedule

schedule_data = [
    ("Monday", "07:00", "Morning Bliss", 60),
    ("Monday", "16:45", "Aerial Yoga", 75),
    ("Monday", "18:00", "Aerial Stretching", 90),
    ("Monday", "19:30", "Evening Serenity", 60),
    
    ("Tuesday", "07:00", "Morning Bliss", 60),
    ("Tuesday", "16:45", "Aerial Yoga", 75),
    ("Tuesday", "18:00", "Evening Serenity", 60),
    ("Tuesday", "19:30", "Aerial Stretching", 90),

    ("Wednesday", "07:00", "Morning Bliss", 60),
    ("Wednesday", "16:45", "Aerial Dance", 75),
    ("Wednesday", "18:00", "Aerial Yoga", 75),
    ("Wednesday", "19:30", "Aerial Stretching", 90),

    ("Thursday", "07:00", "Morning Bliss", 60),
    ("Thursday", "16:45", "Kids", 45),
    ("Thursday", "18:00", "Aerial Yoga", 75),
    ("Thursday", "19:30", "Aerial Stretching", 90),

    ("Friday", "07:00", "Morning Bliss", 60),
    ("Friday", "16:45", "Kids", 45),
    ("Friday", "18:00", "Aerial Stretching", 90),
    ("Friday", "19:30", "Evening Serenity", 60),

    ("Saturday", "10:00", "Morning Bliss", 60),
    ("Saturday", "11:30", "Aerial Yoga", 75),
    ("Saturday", "13:00", "Aerial Stretching", 90),
]

with app.app_context():
    db.create_all()
    # Очистка таблицы расписания (если нужно)
    db.session.query(Schedule).delete()

    for day, time, title, duration in schedule_data:
        # Можно задавать max_slots индивидуально, здесь для всех ставим 5
        schedule = Schedule(day=day, time=time, title=title, duration=duration, max_slots=5)
        db.session.add(schedule)

    db.session.commit()
    print("Тестовые данные обновлены!")
