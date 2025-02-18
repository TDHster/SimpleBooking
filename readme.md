# 🏋️ Studio Booking System

## About the Project
Studio Booking System is a powerful and intuitive web application designed for fitness studios, yoga centers, and other venues that offer scheduled group classes. It allows visitors to seamlessly book spots in the studio for upcoming sessions, making scheduling easier for both clients and administrators.

## Key Features 🚀
✅ **Modern UI & UX** – Responsive and user-friendly interface built with Bootstrap 5 for smooth navigation.  
✅ **Admin Panel** – Manage schedules, add/edit sessions, and track bookings effortlessly.  
✅ **Secure Authentication** – Password protection with brute-force prevention (15-second delay on failed login attempts).  
✅ **IP-based Access Restrictions** – Limit access by country or city to enhance security and prevent unauthorized usage.  
✅ **User Data in Cookies** – Returning users can book faster thanks to auto-filled details stored in cookies.  
✅ **GDPR Ready** – Implements privacy-compliant warnings, user consent prompts, and secure data handling.  
✅ **Booking Confirmation** – Users receive real-time confirmation for their bookings.  
✅ **Dynamic Schedule** – Manage class availability, maximum slots, and duration with ease.  
✅ **Session Editing & Deletion** – Modify or remove entries with built-in confirmation dialogs.  
✅ **Role-based Access Control** – Secure admin panel with restricted access.  

## Tech Stack 💻
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Backend:** Flask (Python)
- **Database:** SQLite / PostgreSQL (configurable)
- **Authentication:** Flask-Login, session-based auth

## How to Install & Run 🚀
```bash
# Clone the repository
git clone https://github.com/yourusername/studio-booking.git
cd studio-booking

edit .env file, use .env-example

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the system at:
http://localhost:5000
```
