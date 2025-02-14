#models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)        # Например, "Monday"
    time = db.Column(db.String(10), nullable=False)         # Формат "HH:MM"
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)        # Длительность в минутах
    max_slots = db.Column(db.Integer, nullable=False, default=5)  # Максимальное количество участников

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)       # Дата проведения занятия
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    client_id = db.Column(db.String(50), nullable=False)

    schedule = db.relationship('Schedule', backref=db.backref('bookings', lazy=True))
