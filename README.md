📋 MedTrack - Healthcare Management System
MedTrack is a Cloud-Enabled Healthcare Management System built using Flask, AWS DynamoDB, and SNS. It allows patients to book appointments with doctors, manage profiles, view appointment history, and enables doctors to manage their schedules effectively.


📌 Features
✅ User Registration (Doctors & Patients)

✅ Secure Login System (Role-based: Patient / Doctor)

✅ Book Appointments with Doctors

✅ Doctors Manage Appointments

✅ Search Appointments (by name or date)

✅ Email Notifications (to users/admin using SMTP)

✅ AWS DynamoDB Integration (User & Appointment data)

✅ Responsive UI using Bootstrap

✅ Error Handling with Custom 404 Page

## 🌐 Live Demo (Optional)
*(If hosted, add your URL here)*

---

## 🚀 Features

- User roles: **Patient**, **Doctor**, **Admin**
- User registration & authentication
- **Book appointments** with doctors
- **Doctor dashboards** to manage patient appointments
- Email notifications for bookings and confirmations
- AWS DynamoDB for database
- AWS SNS for notifications (optional)
- Dark mode, accessibility, responsive UI
- **Deployed on AWS EC2**

---

## 📦 Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML5, Bootstrap 5, Jinja2
- **Database:** AWS DynamoDB
- **Notifications:** AWS SNS (optional)
- **Deployment:** AWS EC2

---

## 📁 Project Structure

🛠️ Technologies Used
Technology	Purpose
Python (Flask)	Backend Web Application
AWS DynamoDB	NoSQL Database for persistence
AWS SNS	Email/Notification System
Bootstrap 5	Responsive Frontend Framework
Jinja2	HTML Templating Engine
dotenv	Environment Configuration
Werkzeug	Password Hashing
SMTP (Gmail)	Sending email notifications

MedTrack/
├── app.py
├── requirements.txt
├── .env
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard_patient.html
│   ├── dashboard_doctor.html
│   ├── book_appointment.html
│   ├── view_appointment_patient.html
│   ├── view_appointment_doctor.html
│   ├── search_results.html
│   ├── profile.html
│   └── 404.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── scripts.js
└── README.md


SECRET_KEY=<your_secret_key_here>
EMAIL_USER=<your_email_address>
EMAIL_PASS=<your_email_password_or_app_password>
AWS_ACCESS_KEY_ID=<your_aws_access_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_key>
AWS_REGION=<your_aws_region>
DYNAMODB_USERS_TABLE=Users
DYNAMODB_APPOINTMENTS_TABLE=Appointments
SNS_TOPIC_ARN=<your_topic_arn>  # optional


🗃️ DynamoDB Tables Structure
MedTrack_Users
Attribute	Type
email	HASH
name	String
role	String (patient or doctor)
...	...

MedTrack_Appointments
Attribute	Type
appointment_id	HASH
patient	String
doctor	String
date	String (YYYY-MM-DD)
time	String (HH:MM)
status	String (pending, confirmed, completed)

📧 Email Notification
Users receive emails for:

Appointment confirmations

Cancellations

Admin notifications

Configured using smtplib and Gmail SMTP.

✅ Functional Testing Covered
Home Page Navigation ✔️

Doctor/Patient Registration ✔️

Secure Login ✔️

Patient Dashboard ✔️

Doctor Dashboard ✔️

Book Appointment ✔️

Appointment Search ✔️

DynamoDB Updates ✔️

Email Notifications ✔️

Error Pages ✔️

📦 Deployment (Optional)
For production deployment, use gunicorn or uWSGI behind Nginx/Apache or deploy on platforms like AWS EC2, Heroku, etc.

👨‍💻 Author
Developed by: @SAGAR

📧 Contact: Sagar@example.com

