from flask import Flask, request, session, redirect, url_for, render_template, flash
import boto3
from botocore.exceptions import ClientError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import uuid
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key, Attr

# ----------------------------------------
# Load environment variables
# ----------------------------------------
load_dotenv()

# ----------------------------------------
# Flask App Initialization
# ----------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'temporary_secret_key')  # consistent fallback

# ----------------------------------------
# Application Configuration
# ----------------------------------------

# AWS Config
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION_NAME)
sns = boto3.client('sns', region_name=AWS_REGION_NAME)

# DynamoDB Table Names
USERS_TABLE_NAME = os.environ.get('USERS_TABLE_NAME', 'UsersTable')
APPOINTMENTS_TABLE_NAME = os.environ.get('APPOINTMENTS_TABLE_NAME', 'AppointmentsTable')

user_table = dynamodb.Table(USERS_TABLE_NAME)
appointment_table = dynamodb.Table(APPOINTMENTS_TABLE_NAME)

# SNS Config
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
ENABLE_SNS = os.environ.get('ENABLE_SNS', 'False').lower() == 'true'

# Email Config
ENABLE_EMAIL = os.environ.get('ENABLE_EMAIL', 'False').lower() == 'true'
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')

# ----------------------------------------
# Logging Configuration
# ----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------------------
# Helper Functions
# ----------------------------------------

def is_logged_in():
    """Check if user is logged in based on session."""
    return 'email' in session

def send_email(to_email, subject, body):
    """Send email using SMTP if enabled."""
    if not ENABLE_EMAIL:
        logger.info("[Email Skipped] Subject: {} to {}".format(subject, to_email))
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()

        logger.info("Email sent to {}".format(to_email))
    except Exception as e:
        logger.error("Failed to send email: {}".format(e))

def publish_to_sns(message, subject="HealthCare Notification"):
    """Publish a message to SNS if enabled."""
    if not ENABLE_SNS or not SNS_TOPIC_ARN:
        logger.info("[SNS Skipped] Message: {}".format(message))
        return
    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )
        logger.info("SNS published: {}".format(response['MessageId']))
    except Exception as e:
        logger.error("Failed to publish to SNS: {}".format(e))

# index route
@app.route('/')
def index():
    if is_logged_in():
        role = session.get('role', 'unknown')
        logger.info("User logged in, role: {}, redirecting to dashboard_{}".format(role, role))
        return redirect(url_for('dashboard_' + role))
    return render_template('index.html')

# register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        role = session.get('role', 'unknown')
        logger.info("User already logged in, role: {}, redirecting to dashboard_{}".format(role, role))
        return redirect(url_for('dashboard_' + role))

    if request.method == 'POST':
        required_fields = ['name', 'email', 'password', 'confirm_password', 'age', 'gender', 'role']
        for field in required_fields:
            if not request.form.get(field):
                flash('Please enter {}'.format(field), 'danger')
                return render_template('register.html')

        if request.form['password'] != request.form['confirm_password']:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        email = request.form['email'].lower()
        existing = user_table.get_item(Key={'email': email}).get('Item')
        if existing:
            flash('Email already registered', 'danger')
            return render_template('register.html')

        user_data = {
            'email': email,
            'name': request.form['name'],
            'password': generate_password_hash(request.form['password']),
            'age': request.form['age'],
            'gender': request.form['gender'],
            'role': request.form['role'].lower(),
            'created_at': datetime.utcnow().isoformat()
        }

        if user_data['role'] == 'doctor':
            specialization = request.form.get('specialization', 'Not specified')
            user_data['specialization'] = specialization

        user_table.put_item(Item=user_data)

        if ENABLE_EMAIL:
            send_email(email, 'Welcome to HealthCare App', "Hello {}, your account was created successfully.".format(user_data['name']))

        publish_to_sns("New user registered: {} ({}) as {}".format(user_data['name'], email, user_data['role']))

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        role = session.get('role', 'unknown')
        logger.info("User already logged in, role: {}, redirecting to dashboard_{}".format(role, role))
        return redirect(url_for('dashboard_' + role))

    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '').lower()

        if not email or not password or not role:
            flash('All fields are required', 'danger')
            return render_template('login.html')

        user = user_table.get_item(Key={'email': email}).get('Item')
        if user and user['role'] == role and check_password_hash(user['password'], password):
            session['email'] = email
            session['role'] = role
            session['name'] = user.get('name', '')
            logger.info("Login successful for email: {}, role: {}, redirecting to dashboard_{}".format(email, role, role))
            return redirect(url_for('dashboard_' + role))
        flash('Invalid email, password, or role', 'danger')

    return render_template('login.html')

# logout route
@app.route('/logout')
def logout():
    session.clear()
    logger.info("User logged out, redirecting to login")
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# dashboard route
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        logger.info("User not logged in, redirecting to login")
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))

    role = session.get('role', 'unknown')
    logger.info("Dashboard accessed, role: {}".format(role))
    if role == 'doctor':
        return redirect(url_for('dashboard_doctor'))
    elif role == 'patient':
        return redirect(url_for('dashboard_patient'))
    else:
        logger.warning("Invalid role: {}, clearing session and redirecting to login".format(role))
        session.clear()
        flash('Invalid role. Please log in again.', 'danger')
        return redirect(url_for('login'))

# dashboard/doctor route
@app.route('/dashboard/doctor')
def dashboard_doctor():
    if not is_logged_in() or session.get('role') != 'doctor':
        logger.info("Unauthorized access to dashboard_doctor, redirecting to login")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    email = session['email']

    try:
        try:
            response = appointment_table.query(
                IndexName='DoctorEmailIndex',
                KeyConditionExpression=Key('doctor_email').eq(email)
            )
            appointments = response.get('Items', [])
        except Exception as e:
            logger.warning("DoctorEmailIndex fallback scan: {}".format(e))
            scan_response = appointment_table.scan(
                FilterExpression=Attr('doctor_email').eq(email)
            )
            appointments = scan_response.get('Items', [])

        pending_appointments = [a for a in appointments if a.get('status') == 'pending']
        completed_appointments = [a for a in appointments if a.get('status') == 'completed']

        return render_template(
            'dashboard_doctor.html',
            pending_appointments=pending_appointments,
            completed_appointments=completed_appointments,
            all_appointments=appointments,
            pending_count=len(pending_appointments),
            completed_count=len(completed_appointments),
            total_count=len(appointments)
        )
    except Exception as e:
        logger.error("Doctor dashboard error: {}".format(e))
        flash('Something went wrong. Please try again later.', 'danger')
        return redirect(url_for('login'))

# dashboard/patient route
@app.route('/dashboard/patient')
def dashboard_patient():
    if not is_logged_in() or session.get('role') != 'patient':
        logger.info("Unauthorized access to dashboard_patient, redirecting to login")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    email = session['email']

    try:
        response = appointment_table.scan(
            FilterExpression=Attr('patient_email').eq(email)
        )
        appointments = response.get('Items', [])

        pending_appointments = sum(1 for appt in appointments if appt['status'] == 'pending')
        completed_appointments = sum(1 for appt in appointments if appt['status'] == 'completed')
        total_appointments = len(appointments)

        doctor_response = user_table.scan(
            FilterExpression=Attr('role').eq('doctor')
        )
        doctors = doctor_response.get('Items', [])

        return render_template(
            'dashboard_patient.html',
            appointments=appointments,
            doctors=doctors,
            pending_appointments=pending_appointments,
            completed_appointments=completed_appointments,
            total_appointments=total_appointments
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.error("DynamoDB table {} not found.".format(APPOINTMENTS_TABLE_NAME))
            flash("Error: The appointments table does not exist. Please contact support.", 'danger')
        else:
            logger.error("DynamoDB error: {}".format(e))
            flash('An error occurred while loading your dashboard. Please try again later.', 'danger')
        return redirect(url_for('login'))
    except Exception as e:
        logger.error("Unexpected error in dashboard_patient: {}".format(str(e)))
        flash('An error occurred while loading your dashboard. Please try again later.', 'danger')
        return redirect(url_for('dashboard_patient'))  # Retry the same page instead of login

# Book Appointment Route
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if not is_logged_in() or session.get('role') != 'patient':
        logger.info("Unauthorized access to book_appointment, redirecting to login")
        flash('Only patients can book appointments.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_email = request.form.get('doctor_email')
        symptoms = request.form.get('symptoms')
        appointment_date = request.form.get('appointment_date') or datetime.now().isoformat()
        appointment_time = request.form.get('appointment_time')  # New field
        patient_email = session.get('email')

        if not doctor_email or not symptoms or not appointment_date or not appointment_time:
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('book_appointment'))

        try:
            doctor = user_table.get_item(Key={'email': doctor_email}).get('Item')
            patient = user_table.get_item(Key={'email': patient_email}).get('Item')

            if not doctor or doctor.get('role') != 'doctor':
                flash('Invalid doctor selected.', 'danger')
                return redirect(url_for('book_appointment'))

            if not patient:
                flash('Patient data not found.', 'danger')
                return redirect(url_for('book_appointment'))

            doctor_name = doctor.get('name', 'Doctor')
            patient_name = patient.get('name', 'Patient')

            from datetime import datetime
            appointment_datetime = datetime.strptime("{0} {1}".format(appointment_date, appointment_time), '%Y-%m-%d %H:%M').isoformat()

            appointment_id = str(uuid.uuid4())
            appointment_item = {
                'appointment_id': appointment_id,
                'doctor_email': doctor_email,
                'doctor_name': doctor_name,
                'patient_email': patient_email,
                'patient_name': patient_name,
                'symptoms': symptoms,
                'status': 'pending',
                'appointment_date': appointment_datetime,
                'created_at': datetime.now().isoformat()
            }

            appointment_table.put_item(Item=appointment_item)

            if ENABLE_EMAIL:
                send_email(
                    doctor_email,
                    "New Appointment Notification",
                    "Dear Dr. {0},\n\nA new appointment has been booked by {1}.\n\nSymptoms: {2}\nDate & Time: {3}".format(doctor_name, patient_name, symptoms, appointment_datetime)
                )
                send_email(
                    patient_email,
                    "Appointment Confirmation",
                    "Dear {0},\n\nYour appointment with Dr. {1} has been successfully booked on {2}.".format(patient_name, doctor_name, appointment_datetime)
                )

            if ENABLE_SNS and SNS_TOPIC_ARN:
                try:
                    sns.publish(
                        TopicArn=SNS_TOPIC_ARN,
                        Message="New appointment booked by {0} with Dr. {1} for {2}".format(patient_name, doctor_name, appointment_datetime),
                        Subject="New Appointment - MedTrack"
                    )
                except Exception as sns_err:
                    logger.warning("SNS publish failed: {}".format(sns_err))

            logger.info("Appointment booked successfully for patient: {}, redirecting to dashboard_patient".format(patient_email))
            flash('Appointment booked successfully.', 'success')
            return redirect(url_for('dashboard_patient'))  # Direct redirect to patient dashboard
        except Exception as e:
            logger.error("Appointment booking failed: {}".format(e))
            flash('An error occurred while booking the appointment.', 'danger')
            return redirect(url_for('book_appointment'))

    try:
        response = user_table.scan(
            FilterExpression="#r = :doc",
            ExpressionAttributeNames={"#r": "role"},
            ExpressionAttributeValues={":doc": "doctor"}
        )
        doctors = response.get('Items', [])
    except Exception as e:
        logger.error("Doctor fetch failed: {}".format(e))
        doctors = []

    return render_template('book_appointment.html', doctors=doctors)

# view_appointment route
# Doctor View
@app.route('/appointment/view/doctor/<appointment_id>', methods=['GET', 'POST'])
def view_appointment_doctor(appointment_id):
    if not is_logged_in() or session.get('role') != 'doctor':
        logger.info("Unauthorized access to view_appointment_doctor, redirecting to login")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    try:
        response = appointment_table.get_item(Key={'appointment_id': appointment_id})
        appointment = response.get('Item')

        if not appointment or appointment['doctor_email'] != session['email']:
            flash('Access denied or appointment not found.', 'danger')
            return redirect(url_for('dashboard_doctor'))

        if request.method == 'POST':
            diagnosis = request.form.get('diagnosis', '').strip()
            treatment_plan = request.form.get('treatment_plan', '').strip()
            prescription = request.form.get('prescription', '').strip()

            if not diagnosis or not treatment_plan:
                flash('Diagnosis and treatment plan are required.', 'danger')
                return render_template('view_appointment_doctor.html', appointment=appointment)

            appointment_table.update_item(
                Key={'appointment_id': appointment_id},
                UpdateExpression="SET diagnosis = :d, treatment_plan = :tp, prescription = :p, #s = :status, updated_at = :now",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':d': diagnosis,
                    ':tp': treatment_plan,
                    ':p': prescription,
                    ':status': 'completed',
                    ':now': datetime.utcnow().isoformat()
                }
            )

            if ENABLE_EMAIL:
                try:
                    patient_email = appointment.get('patient_email')
                    patient_name = appointment.get('patient_name', 'Patient')
                    doctor_name = appointment.get('doctor_name', 'Doctor')
                    message = """Dear {0},

Your appointment with Dr. {1} has been completed.

Diagnosis: {2}
Treatment Plan: {3}

Thank you for using MedTrack.""".format(patient_name, doctor_name, diagnosis, treatment_plan)
                    send_email(patient_email, "Your Appointment Diagnosis", message)
                except Exception as e:
                    logger.warning("Email error: {}".format(e))

            flash('Diagnosis submitted successfully.', 'success')
            return redirect(url_for('dashboard_doctor'))

        return render_template('view_appointment_doctor.html', appointment=appointment)
    except Exception as e:
        logger.error("[view_appointment_doctor] Error: {}".format(e))
        flash('Something went wrong.', 'danger')
        return redirect(url_for('dashboard_doctor'))

# Patient View
@app.route('/appointment/view/patient/<appointment_id>')
def view_appointment_patient(appointment_id):
    if not is_logged_in() or session.get('role') != 'patient':
        logger.info("Unauthorized access to view_appointment_patient, redirecting to login")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    try:
        response = appointment_table.get_item(Key={'appointment_id': appointment_id})
        appointment = response.get('Item')

        if not appointment or appointment['patient_email'] != session['email']:
            flash('Access denied or appointment not found.', 'danger')
            return redirect(url_for('dashboard_patient'))

        return render_template('view_appointment_patient.html', appointment=appointment)
    except Exception as e:
        logger.error("[view_appointment_patient] Error: {}".format(e))
        flash('Something went wrong.', 'danger')
        return redirect(url_for('dashboard_patient'))

# search_appointments route
@app.route('/search_appointments', methods=['GET', 'POST'])
def search_appointments():
    if not is_logged_in():
        logger.info("Unauthorized access to search_appointments, redirecting to login")
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()

        if not search_term:
            flash('Please enter a search term.', 'warning')
            return redirect(url_for('dashboard'))

        try:
            user_email = session['email']
            role = session['role']
            appointments = []

            if role == 'doctor':
                response = appointment_table.scan(
                    FilterExpression="#doctor_email = :email AND contains(#patient_name, :term)",
                    ExpressionAttributeNames={
                        "#doctor_email": "doctor_email",
                        "#patient_name": "patient_name"
                    },
                    ExpressionAttributeValues={
                        ":email": user_email,
                        ":term": search_term
                    }
                )
            else:
                response = appointment_table.scan(
                    FilterExpression="#patient_email = :email AND (contains(#doctor_name, :term) OR contains(#status, :term))",
                    ExpressionAttributeNames={
                        "#patient_email": "patient_email",
                        "#doctor_name": "doctor_name",
                        "#status": "status"
                    },
                    ExpressionAttributeValues={
                        ":email": user_email,
                        ":term": search_term
                    }
                )

            appointments = response.get('Items', [])

            if not appointments:
                flash("No appointments matched your search.", 'info')

            return render_template('search_results.html', appointments=appointments, search_term=search_term)
        except Exception as e:
            logger.error("Search failed: {}".format(e))
            flash('An error occurred while searching. Please try again.', 'danger')
            return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))

# profile route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        logger.info("Unauthorized access to profile, redirecting to login")
        flash('Please login first', 'danger')
        return redirect(url_for('login'))

    email = session.get('email')
    user = user_table.get_item(Key={'email': email}).get('Item')

    if not user:
        logger.warning("User not found for email: {}, clearing session".format(email))
        flash('User not found', 'danger')
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username', user.get('username'))
        email_form = request.form.get('email', user.get('email'))
        contact = request.form.get('contact', user.get('contact'))

        update_expression = "SET #username = :username, email = :email, contact = :contact"
        expr_values = {
            ':username': username,
            ':email': email_form,
            ':contact': contact
        }
        expr_names = {
            '#username': 'username'
        }

        if user['role'] == 'doctor':
            specialty = request.form.get('specialty', user.get('specialty', ''))
            qualifications = request.form.get('qualifications', user.get('qualifications', ''))
            update_expression += ", specialty = :specialty, qualifications = :qualifications"
            expr_values[':specialty'] = specialty
            expr_values[':qualifications'] = qualifications

        try:
            user_table.update_item(
                Key={'email': email},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expr_values,
                ExpressionAttributeNames=expr_names
            )
            session['name'] = username
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            logger.error("Profile update failed: {}".format(e))
            flash('Failed to update profile. Please try again later.', 'danger')

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

# health route
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error("500 Internal Server Error: {}".format(error))
    return render_template("500.html"), 500

# run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)