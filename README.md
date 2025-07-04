# 🏥 MedTrack — Cloud-Enabled Healthcare Management System

**MedTrack** is a robust healthcare management platform built with **Flask (Python)** and integrated with **AWS DynamoDB** and **AWS SNS**. It enables **patients** to book and manage appointments with **doctors**, while doctors can efficiently handle their schedules. With role-based login, email notifications, and a responsive Bootstrap UI, MedTrack provides a seamless experience for both patients and healthcare providers.

---

## 📌 Key Features

- ✅ **User Registration & Role Selection**  
  Users can register as either **Doctor** or **Patient**, and access functionalities based on their role.

- ✅ **Secure Login System**  
  Role-based login with password hashing using **Werkzeug** for secure access.

- ✅ **Appointment Booking**  
  Patients can browse doctors and book appointments by selecting date and time.

- ✅ **Doctor Appointment Management**  
  Doctors can view, accept, or complete appointments from their dashboard.

- ✅ **Appointment Search**  
  Users can search appointments by name or date using intuitive filters.

- ✅ **Email Notifications**  
  Users receive emails for appointment confirmations, cancellations, and updates via **SMTP (Gmail)**.

- ✅ **AWS DynamoDB Integration**  
  User and appointment data are stored securely in AWS NoSQL database.

- ✅ **Optional AWS SNS Integration**  
  Supports cloud-based notifications for scalable messaging.

- ✅ **Responsive & Accessible UI**  
  Built with **Bootstrap 5**, supporting dark mode and mobile-first design.

- ✅ **Custom Error Handling**  
  Includes custom 404 error page for better user experience.

---

## 🌐 Live Demo *(Optional)*

> Add your hosted demo link here  
> Example: `https://medtrack.yourdomain.com`

---

## 🚀 Full Feature Summary

| Feature               | Description                                    |
|----------------------|------------------------------------------------|
| 👥 Roles              | Patient, Doctor *(Admin - future scope)*      |
| 🔐 Auth               | Secure login with hashed passwords             |
| 📅 Booking            | Patients book and view appointments            |
| 🩺 Doctor Tools       | Manage appointments and status updates         |
| 🔍 Search             | By doctor name, patient name, or date          |
| 📧 Notifications      | SMTP-based email notifications                 |
| ☁️ Cloud Integration  | AWS DynamoDB and optional SNS                  |
| 🎨 UI                 | Bootstrap 5 with dark mode & accessibility     |
| 🧪 Testing            | Functional test coverage for all key features  |
| 💻 Deployment         | AWS EC2, Render, Heroku, or any VPS host       |

---

## 📁 Project Structure — MedTrack

```bash
MedTrack/
├── app.py                       # Main Flask app logic
├── requirements.txt             # Python packages
├── .env                         # Environment variables

├── templates/                   # Jinja2 HTML templates
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


## 🗃️ DynamoDB Schema

### 📌 Users Table (`Users`)

| Attribute | Type | Description                 |
|-----------|------|-----------------------------|
| `email`   | HASH | Unique user identifier      |
| `name`    | String | Full name                  |
| `role`    | String | `doctor` or `patient`      |
| `...`     | ...  | Additional user information |

---

### 📌 Appointments Table (`Appointments`)

| Attribute         | Type   | Description                          |
|------------------|--------|--------------------------------------|
| `appointment_id` | HASH   | Unique appointment ID                |
| `patient`        | String | Patient’s name                       |
| `doctor`         | String | Doctor’s name                        |
| `date`           | String | Format: `YYYY-MM-DD`                 |
| `time`           | String | Format: `HH:MM`                      |
| `status`         | String | `pending`, `confirmed`, `completed` |

---

## ✉️ Email Notifications

Emails are automatically sent for:

- ✅ **Appointment Confirmations**
- ❌ **Appointment Cancellations/Updates**
- 🔔 *(Optional)* **Admin Notifications**

**Powered by** `smtplib` with Gmail SMTP  
➡️ Use **App Passwords** for secure Gmail access.

---

## ✅ Functional Testing Coverage

| Test Module                   | Status |
|------------------------------|--------|
| Home Page Navigation         | ✔️     |
| Doctor/Patient Registration  | ✔️     |
| Login & Role-based Redirect  | ✔️     |
| Patient Dashboard            | ✔️     |
| Doctor Dashboard             | ✔️     |
| Book Appointment             | ✔️     |
| Search Appointments          | ✔️     |
| DynamoDB Data Handling       | ✔️     |
| Email Notification System    | ✔️     |
| Custom Error Pages           | ✔️     |

## ⚙️ Installation & Running

### 🔁 Clone the Repository

```bash
git clone https://github.com/yourusername/MedTrack.git
cd MedTrack

## 📦 Install Dependencies

Create and activate a virtual environment, then install the required packages:

```bash
python -m venv venv
source venv/bin/activate      # On macOS/Linux
# OR
venv\Scripts\activate         # On Windows

pip install -r requirements.txt

## ⚙️ Configure Environment & Run App

Set up your `.env` file with the necessary environment variables, then run the Flask app using:

```bash
flask run

## ☁️ Deployment Note 
  - 🌍 Host on platforms like:
  - [AWS EC2](https://aws.amazon.com/ec2/)

---

## 👨‍💻 Author

**Developed by:** [@SAGAR](https://github.com/sagar25k)  
📧 **Contact:** `sagarkanithi@example.com`
