Anna Web App

A production-ready web app for Tanzanian users, offering microservices for ROSCA management (Mchezo Manager) and mobile money float balancing (MultiSyncBalance).

Setup





Clone the repository: git clone <repo-url>



Install dependencies: pip install -r requirements.txt



Create and apply migrations: python manage.py makemigrations && python manage.py migrate



Create a superuser: python manage.py createsuperuser



Collect static files: python manage.py collectstatic --noinput



Start the development server: python manage.py runserver

Notes





OTPs are printed to the console for local development (see core/models.py).



Email notifications use the console backend (EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend').



Add welcome_sw.mp3 to core/static/audio/ for the welcome audio prompt.



For production, secure SECRET_KEY, configure a proper email backend, and enable HTTPS.

Features





Modular microservices: Mchezo Manager (admin/member roles), MultiSyncBalance (self-admin).



Responsive UI with dark/light mode, Swahili/English localization.



Email notifications for group invites, payments, and issue reports.



Secure: OTP authentication, CSRF protection, form/model validation.



Accessible: ARIA labels, keyboard navigation, mobile-first design (320px+).



Offline mode support with localStorage sync.



PDF/CSV exports for reports.