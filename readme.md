# 🏋️ Studio Booking System

## About the Project
Studio Booking System is a powerful and intuitive web application designed for fitness studios, yoga centers, and other venues that offer scheduled group classes. It allows visitors to seamlessly book spots in the studio for upcoming sessions, making scheduling easier for both clients and administrators.

### User view
<img width="593" alt="Снимок экрана 2025-02-18 в 14 52 38" src="https://github.com/user-attachments/assets/bd50ca81-5bc3-420a-8ff2-eefd4796dc6f" />
<hr>

### Admin view

<img width="605" alt="Снимок экрана 2025-02-18 в 14 52 54" src="https://github.com/user-attachments/assets/ccdcf23c-a792-4627-badc-7338ef2bb1dd" />

<img width="791" alt="Снимок экрана 2025-02-18 в 14 53 13" src="https://github.com/user-attachments/assets/974cd06c-7175-4820-a015-1cc2c3b0f2a2" />
<hr>

## Key Features 🚀
✅ **Modern UI & UX** – Responsive and user-friendly interface built with Bootstrap 5 for smooth navigation.  
✅ **Admin Panel** – Manage schedules, add/edit sessions, and track bookings effortlessly.  
✅ **Check bot** – Via Google capcha v3, no disturbing user.  
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

Need to get Google Capcha v3 key on google develop and store it to .env file.

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
http://localhost:5001
```
