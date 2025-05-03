Anna Web App
A production-ready web app for Tanzanian users, offering microservices for ROSCA management (Mchezo Manager) and mobile money float balancing (MultiSyncBalance).
Setup

Clone the repository: git clone <repo-url>
Install dependencies: pip install -r requirements.txt
Set environment variables:
SECRET_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER


Run migrations: python manage.py migrate
Collect static files: python manage.py collectstatic
Start server: python manage.py runserver

Deployment

Use Gunicorn/Nginx for production.
Serve static files via CDN.
Enable HTTPS.

Features

Modular microservices: Mchezo Manager, MultiSyncBalance.
Responsive UI with dark/light mode, Swahili/English.
WhatsApp integration for notifications.
Secure: OTP auth, encrypted SQLite.
Accessible: Audio prompts, ARIA labels.

