# This is for the authentication blueprint
# Assigner: Patrick
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from flask import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.utils import getCursor, allowed_file, save_image, closeCursorAndConnection, validate_form, dashboard_router, validate_email, validate_phone, validate_date, validate_password, validate_varchar, validate_text

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static", static_url_path="/auth/static")

@auth_bp.before_request
def before_request():
    if "loggedin" in session and request.endpoint in ["auth.login", "auth.register"]:
        return dashboard_router(session.get("role"))
    elif "loggedin" not in session and request.endpoint in ["auth.change_password"]:
        flash("Please login to access this page.", "danger")
        return redirect(url_for("home.home"))

# Login, Register and Logout
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    cursor, connection = getCursor()
    if request.method == "POST":
        if not validate_form(request.form, ["username", "password"]):
            return redirect(url_for("auth.login"))
        username = request.form.get("username")
        password = request.form.get("password")
        query = ("SELECT * FROM userrole u LEFT JOIN membership m ON u.userID = m.member_id WHERE username = %s and is_active = 1 LIMIT 1")
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            session.permanent = True
            session["loggedin"] = True
            session["id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]
            if user[3] == "member":
                session["membership_status"] = user[18]
                session["validity_days"] = (user[19]-datetime.now().date()).days #user[19] is expiry_data, and type is datetime.date
            flash("Welcome back! ", "success")
            return before_request()
        else:
            flash("Invalid username or password, please try again.", "danger")
            return redirect(url_for("auth.login"))
    closeCursorAndConnection()
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    cursor, connection = getCursor()
    titles = ["Mr.", "Ms.", "Miss", "Mrs.", "Dr.", "Prof."]
    required_fields = ["username", "password", "title", "first_name", "last_name", "position", "phone", "date_of_birth", "address", "email"]
    field_validators = {
        "username": None,
        "password": validate_password,
        "title": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "phone": validate_phone,
        "date_of_birth": validate_date,
        "address": None,
        "email": validate_email
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("auth.register"))
        
        username = request.form.get("username")
        password = request.form.get("password")
        title = request.form.get("title")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        position = request.form.get("position")
        phone = request.form.get("phone")
        date_of_birth = request.form.get("date_of_birth")
        address = request.form.get("address")
        email = request.form.get("email")
        health_info = request.form.get("health_info")
        profile_img = request.files.get("profile_image")

        if profile_img.filename != "": # check if the file is empty
            if not allowed_file(profile_img):
                flash("Uploaded file is not a valid image. Only JPG, JPEG, PNG and GIF files are allowed.", "danger")
                return redirect(url_for("auth.register"))
            else:
                profile_img = save_image(profile_img)
        else:
            profile_img = "default_profile.jpg"
            # hash the password by using werkzeug.security
        hashed_password = generate_password_hash(password)

        try:
            query = """INSERT INTO userrole (username, password_hash, role, date_joined, title, first_name, last_name, 
                                            position, phone, email, address, date_of_birth, profile_image, health_information) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query,
                    ( 
                        username, hashed_password, "member", datetime.now(), title, first_name.capitalize(), last_name.capitalize(), 
                        position.capitalize(), phone, email, address, date_of_birth, profile_img, health_info
                    ),
                )
            connection.commit()
            new_id = cursor.lastrowid
            if new_id:
                session["id"] = new_id
                session["username"] = username
                flash("Successfully registered! ", "success")
                return redirect(url_for("auth.membership_payment"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at auth.register")
            if "Duplicate entry" in str(e):
                flash("Username already exists, please try a different username.", "danger")
            else:
                flash("Register failed. Please try again.", "danger")
            return redirect(url_for("auth.register"))
        finally:
            closeCursorAndConnection()
    return render_template("register.html", titles=titles)

@auth_bp.route("/logout")
def logout():
    # Remove session data, this will log the user out
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("password", None)
    session.pop("role", None)
    session.pop("membership_status", None)
    session.pop("validity_days", None)
    # Redirect to login page
    return redirect(url_for("home.home"))


@auth_bp.route("/change_password", methods=["GET", "POST"])
def change_password():
    cursor, connection = getCursor()
    id = session.get("id")
    role = session.get("role")
    cursor.execute("SELECT password_hash FROM userrole WHERE userID = %s", (id,))
    password = cursor.fetchone()[0]
    required_fields = ["current_password", "new_password", "confirm_password"]
    field_validators = {
        "current_password": None,
        "new_password": validate_password,
        "confirm_password": validate_password
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("auth.change_password"))
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not (current_password and new_password and confirm_password):
            flash("Please fill out the form!", "danger")
            return redirect(url_for("auth.change_password"))
        # check if the entered current password is correct
        if not check_password_hash(password, current_password):
            flash("Current Password is wrong! Please try again.", "danger")
            return redirect(url_for("auth.change_password"))
        if new_password != confirm_password:
            flash("New password do not match, please try again!", "danger")
            return redirect(url_for("auth.change_password"))
        hashed_new_password = generate_password_hash(new_password)

        try:
            query = "UPDATE userrole SET password_hash=%s WHERE userID=%s"
            cursor.execute( query, ( hashed_new_password, id,))
            connection.commit()
            affected_rows = cursor.rowcount
            if affected_rows > 0:
                flash("Password changed successfully! ", "success")
                if role == "member":
                    return redirect(url_for("member.member_profile"))
                elif role == "therapist":
                    return redirect(url_for("therapist.therapist_profile"))
                elif role == "manager":
                    return redirect(url_for("manager.manager_profile"))
            else:
                flash("Change password failed. Please try again.", "danger")
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at auth.change_password")
            flash("Change password failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return render_template( "change_password.html", username=session["username"], role=session["role"])


@auth_bp.route("/membership_payment", methods=['GET', 'POST'])
def membership_payment():
    cursor, connection = getCursor()
    query = "SELECT * FROM fees WHERE fees_name LIKE '%membership%';"
    cursor.execute(query)
    plans = cursor.fetchall()
    plans_dict = {plan[0]: plan for plan in plans}
    member_id = session.get("id")
    role = session.get("role")
    today = datetime.now().date()

    if request.method == "POST":
        plan = request.form.get('plan')
        numberOfMonths = int(request.form.get('numberOfMonths', 12))
        amount = (plans_dict[int(plan)][3] if int(plan) in plans_dict else 0) * (numberOfMonths if numberOfMonths < 12 else 1)
        
        try:
            cursor.execute("SELECT * FROM userrole u LEFT JOIN membership m ON u.userID = m.member_id WHERE userid = %s and is_active = 1 LIMIT 1", (member_id,))
            member = cursor.fetchone()

            query = "SELECT expiry_date FROM membership WHERE member_id = %s;"
            cursor.execute(query, (member_id,))
            result = cursor.fetchone()
            current_expiry_date = result[0] if result else None
            new_expiry_date = current_expiry_date if current_expiry_date and current_expiry_date > today else today
            new_expiry_date += relativedelta(months=+numberOfMonths)
            renewed = 1 if current_expiry_date else 0
        
            query = "INSERT INTO payment_transaction (member_id, fees_id, payment_date, amount) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (member_id, plan, datetime.now(), amount,))
            payment_id = cursor.lastrowid

            query = """INSERT INTO membership (member_id, membership_status, expiry_date, first_joined, renewed, payment_id) VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    membership_status=VALUES(membership_status),
                    expiry_date=VALUES(expiry_date),
                    renewed=VALUES(renewed),
                    payment_id=VALUES(payment_id);"""
            cursor.execute(query, (member_id, 1, new_expiry_date, datetime.now(), renewed, payment_id))
            connection.commit()

            if session.get("loggedin"):
                session["membership_status"] = 1
                session["validity_days"] = (new_expiry_date - datetime.now().date()).days #new_expiry_date is expiry_data, and type is datetime.datetime
                flash("Payment successful! Welcome back!", "success")
                return redirect(url_for("member.membership_details"))
            else:
                # set the session variable for auto login after payment
                session["loggedin"] = True
                session["id"] = member[0]
                session["username"] = member[1]
                session["role"] = member[3]
                if member[3] == "member":
                    session["membership_status"] = 1
                    session["validity_days"] = (new_expiry_date - datetime.now().date()).days #new_expiry_date is expiry_data, and type is datetime.datetime
                flash("Payment successful! Welcome on board!", "success")
                return redirect(url_for("member.member_dashboard"))
        except Exception as e:
            connection.rollback()
            flash(f"Error: {e}. Payment failed. Please try again.", "danger")
            return redirect(url_for("auth.membership_payment"))
        finally:
            closeCursorAndConnection()
    return render_template("membership_payment.html", plans=plans, role=role)