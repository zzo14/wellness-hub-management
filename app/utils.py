from flask import Flask
from flask import session
from flask import url_for
from flask import current_app
from flask import flash
from flask import redirect
import mysql.connector
import app.connect as connect
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re

dbconn = None
connection = None
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(
        user=connect.dbuser,
        password=connect.dbpass,
        host=connect.dbhost,
        database=connect.dbname,
        autocommit=False,
    )
    dbconn = connection.cursor()
    return dbconn, connection

def closeCursorAndConnection():
    dbconn.close()
    connection.close()

def allowed_file(file):
    # check if the file is image
    result = True
    if type(file) == list:
        for f in file:
            result = ( "." in f.filename and f.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)
            if not result:
                break
    else:
        result = ( "." in file.filename and file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)
    return result

def save_image(file):
    # save the image to the static folder
    filename = secure_filename(file.filename)
    timeStamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_name = f"{timeStamp}_{filename}"
    img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file.save(img_path)
    return unique_name

def handle_user_data(role_list):
    # separate the active and inactive user data
    active_roles = []
    inactive_roles = []
    for user in role_list:
        if user[-1] == 1:
            active_roles.append(user)
        else:
            inactive_roles.append(user)
    return active_roles, inactive_roles

def parse_time(time_str):
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            pass
    raise ValueError("No valid date format found")

# get the day order
day_order = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7
}
def sort_day_order(class_report):
    for i, report in enumerate(class_report):
        sorted_days = sorted(list(report[4]), key=lambda x: day_order[x])
        new_record = report[:4] + (sorted_days,) + report[5:]
        class_report[i] = new_record
    return class_report

def send_email(recipient, subject, msg):                 # send email function (fake)
    print(f"Email sent to: {recipient}")
    print(f"Subject: {subject}")
    print(f"Message: {msg}")

def dashboard_router(role):
    if role == "member":
        return redirect(url_for("member.member_dashboard"))
    elif role == "therapist":
        return redirect(url_for("therapist.therapist_dashboard"))
    elif role == "manager":
        return redirect(url_for("manager.manager_dashboard"))

def verify_access(required_roles, redirect_page):
    # helper function to verify user accrss based on role
    if "loggedin" not in session:
        flash("Please login to access this page.", "danger")
        return redirect(url_for(redirect_page))
    if session.get("role") not in required_roles:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for(redirect_page))
    return None
    
def validate_form(form_data, required_fields, field_validations=None):
    for field in required_fields:
        if not form_data.get(field):
            flash(f"{field} is required, please fill in all required fields.", "danger")
            return False
    if field_validations:
        for field, validation in field_validations.items():
            if validation is not None and not validation(form_data.get(field)):
                if field == "email":
                    flash("Please enter a valid email address.", "danger")
                elif field == "phone":
                    flash("Please enter a valid phone number.", "danger")
                elif field == "date":
                    flash("Please enter a valid date in the format YYYY-MM-DD.", "danger")
                elif field == "time":
                    flash("Please enter a valid time in the format HH:MM:SS.", "danger")
                elif field == "password":
                    flash("Password must contain at least 8 characters, one uppercase letter, one lowercase letter and one number.", "danger")
                elif field == "first_name" or field == "last_name":
                    flash("Name must contain only alphabetic characters.", "danger")
                else:
                    flash(f"{field} is invalid", "danger")
                return False
    return True

def validate_email(email):
    if email:
        if re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return True
    return False

def validate_phone(phone):
    if phone:
        if phone.isdigit() and len(phone) == 10:
            return True
    return False

def validate_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_password(password):
    if password:
        if len(password) >= 8 and re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and re.search(r"\d", password):
                return True
    return False

def validate_varchar(text):
    if text:
        if re.match(r'[A-Za-z]+', text):
            return True
    return False

def validate_text(text):
    if text:
        if re.match(r'[A-Za-z0-9\s]+', text):
            return True
    return False

def validate_time(time):
    try:
        parse_time(time)
        return True
    except ValueError:
        return False
    
def validate_decimal(decimal):
    if decimal:
        if re.match(r'[0-9]+(\.[0-9]+)?', decimal):
            return True
    return False