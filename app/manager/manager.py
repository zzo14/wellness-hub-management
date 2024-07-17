# This is for the manager blueprint
# Assigner: Patrick
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
from flask import Blueprint
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import getCursor, closeCursorAndConnection, send_email, parse_time, verify_access, validate_form, dashboard_router, validate_email, validate_phone, validate_date, validate_password, validate_varchar, validate_text, validate_time, validate_decimal


manager_bp = Blueprint("manager", __name__, template_folder="templates", static_folder="static", static_url_path="/manager/static")
    
@manager_bp.before_request
def before_request():
    endpoint_access = {
        "manager.manager_dashboard": (["manager"], "home.home"),
        "manager.manager_profile": (["manager"], "home.home"),
        "manager.update_manager_profile": (["manager"], "home.home"),
        "manager.track_payment": (["manager"], "home.home"),
        "manager.member_list": (["manager"], "home.home"),
        "manager.add_member": (["manager"], "home.home"),
        "manager.update_member": (["manager"], "home.home"),
        "manager.therapist_list": (["manager"], "home.home"),
        "manager.add_therapist": (["manager"], "home.home"),
        "manager.update_therapist": (["manager"], "home.home"),
        "manager.delete_user": (["manager"], "home.home"),
        "manager.recover_user": (["manager"], "home.home"),
        "manager.manage_room": (["manager"], "home.home"),
        "manager.update_room": (["manager"], "home.home"),
        "manager.delete_room": (["manager"], "home.home"),
        "manager.manage_class_type": (["manager"], "home.home"),
        "manager.update_class_type": (["manager"], "home.home"),
        "manager.delete_class_type": (["manager"], "home.home"),
        "manager.manage_therapeutic_type": (["manager"], "home.home"),
        "manager.update_therapeutic_type": (["manager"], "home.home"),
        "manager.delete_therapeutic_type": (["manager"], "home.home"),
        "manager.manage_price": (["manager"], "home.home"),
        "manager.update_price": (["manager"], "home.home"),
        "manager.delete_price": (["manager"], "home.home"),
        "manager.attendance_record": (["manager", "therapist"], "home.home"),
        "manager.mark_attendance": (["manager", "therapist"], "home.home"),
        "manager.attendance_report": (["manager"], "home.home"),
        "manager.financial_report": (["manager"], "home.home"),
        "manager.popular_class_report": (["manager"], "home.home"),
        "manager.session_schedule": (["manager"], "home.home"),
        "manager.add_session": (["manager"], "home.home"),
        "manager.edit_session": (["manager"], "home.home"),
        "manager.cancel_session": (["manager"], "home.home"),
    }
    if request.endpoint in endpoint_access:
        roles, redirect_url = endpoint_access[request.endpoint]
        return verify_access(roles, redirect_url)
    
@manager_bp.route("/dashboard")
def manager_dashboard():
    """get the manager dashboard"""
    return render_template("manager_dashboard.html", username=session.get("username"), role=session.get("role"),)

@manager_bp.route("/profile")
def manager_profile():
    """get the manager profile"""
    cursor, connection = getCursor()
    manager_id = session.get("id")
    query = "SELECT * FROM userrole WHERE userID = %s AND role = 'manager' LIMIT 1"
    cursor.execute(query, (manager_id,))
    manager = cursor.fetchone()
    return render_template("manager_profile.html", manager=manager,)

@manager_bp.route("/profile/update_profile",  methods=['GET','POST'])
def update_manager_profile():
    """update the manager profile"""
    cursor, connection = getCursor()
    manager_id = session.get("id")
    titles = ["Mr.", "Mrs.", "Miss", "Ms.", "Mx.", "Dr.", "Prof."]
    required_fields = ["title", "first_name", "last_name", "position", "phone", "email"]
    field_validators = {
        "title": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "phone": validate_phone,
        "email": validate_email,
    }
    query = "SELECT * FROM userrole WHERE userID = %s AND role = 'manager' LIMIT 1"
    cursor.execute(query, (manager_id,))
    manager = cursor.fetchone()

    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.update_manager_profile")) 
        title = request.form.get("title")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        position = request.form.get("position")
        phone = request.form.get("phone")
        email = request.form.get("email")
        
        try:
            query = "UPDATE userrole SET title = %s, first_name = %s, last_name = %s, position = %s, phone = %s, email = %s WHERE userID = %s AND role = 'manager'"
            cursor.execute(query, (title, first_name.capitalize(), last_name.capitalize(), position.capitalize(), phone, email, manager_id,)) # update the manager profile
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Successfully updated! ", "success")
                return redirect(url_for("manager.manager_profile"))
            else:
                flash("No change in profile.", "warning")
                return redirect(url_for("manager.manager_profile"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.update_manager_profile")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return render_template("update_manager_profile.html", manager=manager, titles=titles,)


# payment transaction tracking
@manager_bp.route("/track_payment",  methods=['GET','POST'])
def track_payment():
    """track the payment transactions"""
    cursor, connection = getCursor()
    query = """SELECT p.payment_id, u.userID, u.first_name, u.last_name, t.description, f.fees_name, p.payment_date, f.price as amount
               FROM payment_transaction p
               JOIN fees f ON p.fees_id = f.fees_id
               JOIN payment_type t ON t.payment_type_id = f.payment_type_id
               JOIN userrole u ON u.userID = p.member_id
               WHERE u.role = 'member' AND u.is_active = 1
               ORDER BY payment_id;"""
    cursor.execute(query)
    transactions = cursor.fetchall()
    return render_template("manager_track_payment.html", transactions=transactions)


# member and therapist management
@manager_bp.route("/member_list", methods=['GET','POST'])
def member_list():
    """get the list of members"""
    cursor, connection = getCursor()
    titles = ["Mr.", "Mrs.", "Miss", "Ms.", "Mx.", "Dr.", "Prof."]
    query = """SELECT u.userID, u.title, u.first_name, u.last_name, u.position, u.phone, u.email, u.address, u.date_of_birth, 
                      u.profile_image, u.health_information, m.first_joined, m.membership_status, m.expiry_date, m.renewed, u.is_active, u.username
               FROM userrole u
               JOIN membership m ON u.userID = m.member_id 
               WHERE u.role = 'member';"""
    cursor.execute(query)
    members = cursor.fetchall()
    return render_template("manager_member_list.html", members=members, titles=titles)

@manager_bp.route("/add_member", methods=['GET','POST'])
def add_member():
    """add a new member"""
    cursor, connection = getCursor()
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
        "email": validate_email,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.member_list"))
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

        # hash the password by using werkzeug.security
        hashed_password = generate_password_hash(password)
        try:
            query = """INSERT INTO userrole (username, password_hash, role, date_joined, title, first_name, last_name, position, 
                                             phone, email, address, date_of_birth, profile_image, health_information) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(
                    query,
                    ( 
                        username, hashed_password, "member", datetime.now(), title, first_name.capitalize(), last_name.capitalize(), position, 
                        phone, email, address, date_of_birth, "default_profile.jpg", health_info
                    ),
                )
            member_id = cursor.lastrowid
            query = """INSERT INTO membership (member_id, membership_status, expiry_date, first_joined, renewed) VALUES (%s, %s, %s, %s, %s);"""
            cursor.execute(query, (member_id, 0, datetime.now(), datetime.now(), 0))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Successfully registered! ", "success")
                return redirect(url_for("manager.member_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.add_member")
            if "Duplicate entry" in str(e): # check if the username already exists
                flash("Username already exists, please try a different username.", "danger")
            else:
                flash("Registration failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.member_list"))

@manager_bp.route("/update_member", methods=['GET','POST'])
def update_member():
    """update the member profile"""
    cursor, connection = getCursor()
    required_fields = ["member_id", "title", "first_name", "last_name", "position", "phone", "date_of_birth", "address", "email"]
    field_validators = {
        "member_id": None,
        "title": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "phone": validate_phone,
        "date_of_birth": validate_date,
        "address": None,
        "email": validate_email,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.member_list"))
        member_id = request.form.get("member_id")
        title = request.form.get("title")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        position = request.form.get("position")
        phone = request.form.get("phone")
        email = request.form.get("email")
        date_of_birth = request.form.get("date_of_birth")
        address = request.form.get("address")
        health_info = request.form.get("health_info")        
        try:
            query = """UPDATE userrole SET title = %s, first_name = %s, last_name = %s, position = %s, 
                              phone = %s, email = %s, date_of_birth = %s, address = %s, health_information = %s
                       WHERE userID = %s"""
            cursor.execute(query, (title, first_name.capitalize(), last_name.capitalize(), position, phone, email, date_of_birth, address, health_info, member_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Successfully updated!", "success")
                return redirect(url_for("manager.member_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.update_member")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.member_list"))

@manager_bp.route("/therapist_list", methods=['GET', 'POST'])
def therapist_list():
    """get the list of therapists"""
    cursor, connection = getCursor()
    titles = ["Mr.", "Mrs.", "Miss", "Ms.", "Mx.", "Dr.", "Prof."]
    query = """SELECT * FROM userrole WHERE role = 'therapist';"""
    cursor.execute(query)
    therapists = cursor.fetchall()
    return render_template("manager_therapist_list.html", therapists=therapists, titles=titles)

@manager_bp.route("/add_therapist", methods=['GET','POST'])
def add_therapist():
    """add a new therapist"""
    cursor, connection = getCursor()
    required_fields = ["username", "password", "title", "first_name", "last_name", "position", "phone", "email", "therapist_profile"]
    field_validators = {
        "username": None,
        "password": validate_password,
        "title": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "phone": validate_phone,
        "email": validate_email,
        "therapist_profile": validate_text,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.therapist_list"))
        username = request.form.get("username")
        password = request.form.get("password")
        title = request.form.get("title")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        position = request.form.get("position")
        phone = request.form.get("phone")
        email = request.form.get("email")
        therapist_profile = request.form.get("therapist_profile")

        # hash the password by using werkzeug.security
        hashed_password = generate_password_hash(password)

        try:
            query = """INSERT INTO userrole (username, password_hash, role, date_joined, title, first_name, last_name, 
                                             position, phone, email, therapist_profile, profile_image) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(
                    query,
                    ( 
                        username, hashed_password, "therapist", datetime.now(), title, first_name.capitalize(), last_name.capitalize(), position.capitalize(), 
                        phone, email, therapist_profile, "default_profile.jpg"
                    ),
                )
            connection.commit()
            therapist_profile_id = cursor.lastrowid
            if therapist_profile_id:
                flash("Successfully registered! ", "success")
                return redirect(url_for("manager.therapist_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.add_therapist")
            if "Duplicate entry" in str(e): # check if the username already exists
                flash("Username already exists, please try another one.", "danger")
            else:
                flash("Registration failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.therapist_list"))

@manager_bp.route("/update_therapist", methods=['GET', 'POST'])
def update_therapist():
    """update the therapist profile"""
    cursor, connection = getCursor()
    required_fields = ["therapist_id", "title", "first_name", "last_name", "position", "phone", "email", "therapist_profile"]
    field_validators = {
        "therapist_id": None,
        "title": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "phone": validate_phone,
        "email": validate_email,
        "therapist_profile": validate_text,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.therapist_list"))
        therapist_id = request.form.get("therapist_id")
        title = request.form.get("title")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        position = request.form.get("position")
        phone = request.form.get("phone")
        email = request.form.get("email")
        therapist_profile = request.form.get("therapist_profile")
        
        try:
            query = """UPDATE userrole SET title = %s, first_name = %s, last_name = %s, position = %s, phone = %s, email = %s, therapist_profile = %s
                       WHERE userID = %s"""
            cursor.execute(query, (title, first_name.capitalize(), last_name.capitalize(), position.capitalize(), phone, email, therapist_profile, therapist_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Successfully updated!", "success")
                return redirect(url_for("manager.therapist_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.update_therapist")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.therapist_list"))

@manager_bp.route("/delete_user", methods=['GET','POST'])
def delete_user():
    """delete the user"""
    cursor, connection = getCursor()
    if request.method == "POST":
        # delete the user by setting the status to '0'
        user_id = request.form.get("user_id")
        user_type = request.form.get("user_type")
        url = url_for("manager.therapist_list") if user_type == "therapist" else url_for("manager.member_list") # redirect to the correct page by user type
        if user_type == "therapist":
            cursor.execute("SELECT * FROM class WHERE therapist_id = %s;", (user_id,))
            classes = cursor.fetchall()
            cursor.execute("SELECT * FROM therapeutic WHERE therapist_id = %s;", (user_id,))
            therapeutics = cursor.fetchall()

            if classes or therapeutics:
                flash("Cannot delete the therapist. There are classes or therapeutic sessions assigned to this therapist.", "danger")
                return redirect(url_for("manager.therapist_list"))
        try:
            query = "UPDATE userrole SET is_active = 0 WHERE userID = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("User is successfully deleted!", "success")
                return redirect(url)
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.delete_user")
            flash("Failed to delete. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url)

@manager_bp.route("/recover_user", methods=['GET','POST'])
def recover_user():
    """recover the user"""
    cursor, connection = getCursor()
    if request.method == "POST":
        # recover the user by setting the status to '1'
        user_id = request.form.get("user_id")
        user_type = request.form.get("user_type")
        url = url_for("manager.therapist_list") if user_type == "therapist" else url_for("manager.member_list") # redirect to the correct page by user type
        try:
            query = "UPDATE userrole SET is_active = 1 WHERE userID = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("User is successfully recovered!", "success")
                return redirect(url)
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.recover_user")
            flash("Recover failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url)


# Room Management
@manager_bp.route("/manage_room", methods=['GET','POST'])
def manage_room():
    """get the list of rooms"""
    cursor, connection = getCursor()
    query = """SELECT * FROM room;"""
    cursor.execute(query)
    rooms = cursor.fetchall()
    return render_template("manager_room.html", rooms=rooms)

@manager_bp.route("/update_room", methods=['GET', 'POST'])
def update_room():
    """update the room"""
    cursor, connection = getCursor()
    required_fields = ["room_name", "room_capacity"]
    field_validators = {
        "room_name": None,
        "room_capacity": validate_decimal,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.manage_room"))
        room_id = request.form.get("room_id")
        room_name = request.form.get("room_name")
        room_capacity = request.form.get("room_capacity")

        # check if the room name already exists
        if room_id:
            cursor.execute("SELECT * FROM room WHERE room_name = %s AND room_id != %s;", (room_name, room_id,))
        else:
            cursor.execute("SELECT * FROM room WHERE room_name = %s;", (room_name,))
        exist_room = cursor.fetchone()
        if exist_room:
            flash("Room name already exists, please try a different name.", "danger")
            return redirect(url_for("manager.manage_room"))
        
        try:    
            if room_id:
                query = """UPDATE room SET room_name = %s, capacity = %s WHERE room_id = %s"""
                cursor.execute(query, (room_name.capitalize(), room_capacity,room_id,))
                success_msg = "Room updated successfully!"
            else:
                query = """INSERT INTO room (room_name, capacity) VALUES (%s, %s);"""
                cursor.execute(query, (room_name.capitalize(), room_capacity,))
                success_msg = "Room added successfully!"
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash(success_msg, "success")
                return redirect(url_for("manager.manage_room"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.update_room")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_room"))

@manager_bp.route("/delete_room", methods=['GET', 'POST'])
def delete_room():
    """delete the room"""
    cursor, connection = getCursor()
    if request.method == "POST":
        room_id = request.form.get("room_id")

        cursor.execute("SELECT * FROM class WHERE room_id = %s;", (room_id,))
        exist_class = cursor.fetchall()
        if exist_class:
            flash("Cannot delete the room. There are classes assigned to this room.", "danger")
            return redirect(url_for("manager.manage_room"))
        cursor.execute("SELECT * FROM therapeutic WHERE room_id = %s;", (room_id,))
        exist_therapeutic = cursor.fetchall()
        if exist_therapeutic:
            flash("Cannot delete the room. There are therapeutic sessions assigned to this room.", "danger")
            return redirect(url_for("manager.manage_room"))
        try:
            query = "DELETE FROM room WHERE room_id = %s"
            cursor.execute(query, (room_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Room deleted successfully!", "success")
                return redirect(url_for("manager.manage_room"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.delete_room")
            flash("Delete failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_room"))


#Class Type Management
@manager_bp.route("/manage_class_type", methods=['GET','POST'])
def manage_class_type():
    """get the list of class types"""
    cursor, connection = getCursor()
    query = """SELECT * FROM class_info;"""
    cursor.execute(query)
    classes = cursor.fetchall()
    return render_template("manager_class_type.html", classes=classes)

@manager_bp.route("/update_class_type", methods=['GET', 'POST'])
def update_class_type():
    """update the class type"""
    cursor, connection = getCursor()
    required_fields = ["class_name", "class_description"]
    field_validators = {
        "class_name": None,
        "class_description": None,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.manage_class_type"))
        class_id = request.form.get("class_id")
        class_name = request.form.get("class_name")
        class_description = request.form.get("class_description")
    
        # check if the class name already exists
        if class_id:
            cursor.execute("SELECT * FROM class_info WHERE type = %s AND type_id != %s;", (class_name, class_id,))
        else:
            cursor.execute("SELECT * FROM class_info WHERE type = %s;", (class_name,))
        exist_class = cursor.fetchone()
        if exist_class:
            flash("Class name already exists, please try a different name.", "danger")
            return redirect(url_for("manager.manage_class_type"))
    
        try:
            if class_id:
                query = """UPDATE class_info SET type = %s, description = %s WHERE type_id = %s"""
                cursor.execute(query, (class_name.capitalize(), class_description,class_id,))
                success_msg = "Successfully update!"
            else:
                query = """INSERT INTO class_info (type, description) VALUES (%s, %s);"""
                cursor.execute(query, (class_name.capitalize(), class_description,))
                success_msg = "Class type added successfully!"
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash(success_msg, "success")
                return redirect(url_for("manager.manage_class_type"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.update_class_type")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_class_type"))

@manager_bp.route("/delete_class_type", methods=['GET', 'POST'])
def delete_class_type():
    """delete the class type"""
    cursor, connection = getCursor()
    if request.method == "POST":
        class_id = request.form.get("class_id")

        cursor.execute("SELECT * FROM class WHERE class_id = %s;", (class_id,))
        exist_class = cursor.fetchall()
        if exist_class:
            flash("Cannot delete the class type. There are classes assigned to this class type.", "danger")
            return redirect(url_for("manager.manage_class_type"))
        try:
            query = "DELETE FROM class_info WHERE type_id = %s"
            cursor.execute(query, (class_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Class type deleted successfully!", "success")
                return redirect(url_for("manager.manage_class_type"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.delete_class_type")
            flash("Delete failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_class_type"))


#Therapeutic Type Management
@manager_bp.route("/manage_therapeutic_type", methods=['GET','POST'])
def manage_therapeutic_type():
    """get the list of therapeutic types"""
    cursor, connection = getCursor()
    query = """SELECT * FROM session;"""
    cursor.execute(query)
    therapeutics = cursor.fetchall()
    return render_template("manager_therapeutic_type.html", therapeutics=therapeutics)

@manager_bp.route("/update_therapeutic_type", methods=['GET', 'POST'])
def update_therapeutic_type():
    """update the therapeutic type"""
    cursor, connection = getCursor()
    required_fields = ["therapeutic_type", "therapeutic_description"]
    field_validators = {
        "therapeutic_type": None,
        "therapeutic_description": None,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("manager.manage_therapeutic_type"))
        therapeutic_id = request.form.get("therapeutic_id")
        therapeutic_type = request.form.get("therapeutic_type")
        therapeutic_description = request.form.get("therapeutic_description")

        # check if the therapeutic type already exists
        if therapeutic_id:
            cursor.execute("SELECT * FROM session WHERE type = %s AND type_id != %s;", (therapeutic_type,therapeutic_id, ))
        else:
            cursor.execute("SELECT * FROM session WHERE type = %s;", (therapeutic_type,))
        exist_therapeutic = cursor.fetchone()
        if exist_therapeutic:
            flash("Session name already exists, please try a different name.", "danger")
            return redirect(url_for("manager.manage_therapeutic_type"))
        
        try:
            if therapeutic_id:
                query = """UPDATE session SET type = %s, description = %s WHERE type_id = %s"""
                cursor.execute(query, (therapeutic_type.capitalize(), therapeutic_description, therapeutic_id,))
                success_msg = "Session type updated successfully!"
            else:
                query = """INSERT INTO session (type, description) VALUES (%s, %s);"""
                cursor.execute(query, (therapeutic_type.capitalize(), therapeutic_description,))
                success_msg = "Session type added successfully!"
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash(success_msg, "success")
                return redirect(url_for("manager.manage_therapeutic_type"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.update_therapeutic_type")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_therapeutic_type"))

@manager_bp.route("/delete_therapeutic_type", methods=['GET', 'POST'])
def delete_therapeutic_type():
    """delete the therapeutic type"""
    cursor, connection = getCursor()
    if request.method == "POST":
        therapeutic_id = request.form.get("therapeutic_id")

        cursor.execute("SELECT * FROM therapeutic WHERE type_id = %s;", (therapeutic_id,))
        exist_therapeutic = cursor.fetchall()
        if exist_therapeutic:
            flash("Cannot delete the therapeutic type. There are therapeutic sessions assigned to this therapeutic type.", "danger")
            return redirect(url_for("manager.manage_therapeutic_type"))
        try:
            query = "DELETE FROM session WHERE type_id = %s"
            cursor.execute(query, (therapeutic_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Session type deleted successfully!", "success")
                return redirect(url_for("manager.manage_therapeutic_type"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.delete_therapeutic_type")
            flash("Delete failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_therapeutic_type"))


#Price Management
@manager_bp.route("/manage_price", methods=['GET','POST'])
def manage_price():
    """get the list of prices"""
    cursor, connection = getCursor()
    payment_types = ["subscription", "therapeutic", "other"]
    query = """SELECT f.fees_id, f.fees_name,  p.description, f.price FROM fees f
               JOIN payment_type p ON p.payment_type_id = f.payment_type_id;"""
    cursor.execute(query)
    prices = cursor.fetchall()
    return render_template("manager_price.html", prices=prices, payment_types=payment_types)

@manager_bp.route("/update_price", methods=['GET', 'POST'])
def update_price():
    """update the price"""
    cursor, connection = getCursor()
    required_fields = ["price_name", "type", "price"]
    field_validators = {
        "price_name": None,
        "type": None,
        "price": validate_decimal,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("manager.manage_price"))
        price_id = request.form.get("price_id")
        price_name = request.form.get("price_name")
        payment_type = request.form.get("type")
        price = request.form.get("price")

        # check the payment type
        if payment_type == "subscription":
            payment_type_id = 1
        elif payment_type == "therapeutic":
            payment_type_id = 2
        else:
            payment_type_id = 3
        
        # check if the price name already exists
        if price_id:
            cursor.execute("SELECT * FROM fees WHERE fees_name = %s AND fees_id != %s;", (price_name,price_id, ))
        else:
            cursor.execute("SELECT * FROM fees WHERE fees_name = %s;", (price_name,))
        exist_fees = cursor.fetchone()
        if exist_fees:
            flash("Price name already exists, please try a different name.", "danger")
            return redirect(url_for("manager.manage_price"))

        try:
            if price_id:
                query = """UPDATE fees SET fees_name = %s, payment_type_id = %s, price = %s WHERE fees_id = %s"""
                cursor.execute(query, (price_name.capitalize(), payment_type_id, price, price_id,))
                success_msg = "Price updated succesfully!"
            else:
                query = """INSERT INTO fees (fees_name, payment_type_id, price) VALUES (%s, %s, %s);"""
                cursor.execute(query, (price_name.capitalize(), payment_type_id, price,))
                success_msg = "Price added succesfully!"
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash(success_msg, "success")
                return redirect(url_for("manager.manage_price"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.update_price")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_price"))

@manager_bp.route("/delete_price", methods=['GET', 'POST'])
def delete_price():
    """delete the price"""
    cursor, connection = getCursor()
    if request.method == "POST":
        price_id = request.form.get("price_id")
        try:
            query = "DELETE FROM fees WHERE fees_id = %s"
            cursor.execute(query, (price_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Price deleted succesfully!", "success")
                return redirect(url_for("manager.manage_price"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.delete_price")
            flash("Delete failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.manage_price"))


#Record attendance at class and therapeutic sessions
@manager_bp.route("/attendance_record", methods=['GET', 'POST'])
def attendance_record():
    """record the attendance"""
    cursor, connection = getCursor()
    addon_therapeutic_query = ""
    addon_class_query = ""
    # get the attendance records for the manager or therapist
    if session.get("role") == 'therapist':
        therapist_id = session.get("id")
        addon_therapeutic_query = f"WHERE t.therapist_id = {therapist_id}"
        addon_class_query = f"WHERE c.therapist_id = {therapist_id}"
    query = f""" SELECT * FROM (
                    SELECT 'class' AS type, c.class_id AS id, i.type AS `Class/Session`, cb.date, CONCAT(TIME_FORMAT(c.start_time, "%H:%i"), ' - ', TIME_FORMAT(c.end_time, "%H:%i")) AS time,
                            CONCAT(u.first_name, ' ', u.last_name) AS therapist_name
                    FROM class c
                    JOIN class_booking cb ON cb.class_id = c.class_id
                    JOIN class_info i ON c.type_id = i.type_id
                    JOIN userrole u ON c.therapist_id = u.userID
                    {addon_class_query}
                    GROUP BY cb.class_id, cb.date, time

                    UNION ALL

                    SELECT 'therapeutic' AS type, t.therapeutic_id AS id, s.type AS `Class/Session`, t.date, CONCAT(TIME_FORMAT(t.start_time, "%H:%i"), ' - ', TIME_FORMAT(t.end_time, "%H:%i")) AS time,  
                            CONCAT(u.first_name, ' ', u.last_name) AS therapist_name
                    FROM therapeutic t 
                    JOIN therapeutic_booking tb ON t.therapeutic_id = tb.therapeutic_id
                    JOIN session s ON s.type_id = t.type_id
                    JOIN userrole u ON t.therapist_id = u.userID
                    {addon_therapeutic_query}
                    GROUP BY t.therapeutic_id, t.date, time) AS attendance_record
                    ORDER BY date ASC, time ASC;"""
    cursor.execute(query)
    records = cursor.fetchall()
    # get the attendance data for each record (therapeutic and class)
    attendance_data = {}
    for record in records:
        type = record[0]
        id = record[1]
        date = record[3]
        if type not in attendance_data:
            attendance_data[type] = {}
        key = (id, date) if type == 'class' else id # key for class is (class_id, date) and for therapeutic is therapeutic_id
        if id not in attendance_data[type]:
            attendance_data[type][key] = []
        if type == 'therapeutic':
            booking_query = """SELECT tb.therapeutic_id, tb.member_id, CONCAT(m.first_name, ' ', m.last_name) AS member_name,
                                    tar.is_attended, tb.therapeutic_booking_id 
                            FROM therapeutic_booking tb
                            LEFT JOIN therapeutic_attendance_record tar ON tb.therapeutic_booking_id = tar.therapeutic_booking_id 
                            LEFT JOIN userrole m ON tb.member_id = m.userID  
                            WHERE tb.therapeutic_id = %s"""
            cursor.execute(booking_query, (id,))
        else:
            booking_query = """SELECT cb.class_id, cb.member_id, CONCAT(m.first_name, ' ', m.last_name) AS member_name, 
                                    car.is_attended, cb.class_booking_id 
                            FROM class_booking cb
                            LEFT JOIN class_attendance_record car ON cb.class_booking_id = car.class_booking_id 
                            LEFT JOIN userrole m ON cb.member_id = m.userID  
                            WHERE cb.class_id = %s AND cb.date = %s"""
            cursor.execute(booking_query, (id, date,))
        attendance_data[type][key] = cursor.fetchall()
    return render_template("manager_attendance.html", records=records, attendance_data=attendance_data, role=session.get("role"))

@manager_bp.route("/attendance_record/mark_attendance", methods=['GET', 'POST'])
def mark_attendance():
    """mark the attendance for the class or therapeutic session"""
    cursor, connection = getCursor()
    if request.method == "POST":
        type = request.form.get('type')
        # update the attendance record
        if type == 'therapeutic':
            query = """UPDATE therapeutic_attendance_record SET is_attended = %s WHERE therapeutic_booking_id = %s"""
        else:
            query = """UPDATE class_attendance_record SET is_attended = %s WHERE class_booking_id = %s"""
        success_flag = False
        try:
            for key, value in request.form.items():
                if key.startswith('is_attended_'):
                    booking_id = key.split('_')[2]
                    is_attended = value
                    cursor.execute(query, (is_attended, booking_id,))
                    connection.commit()
                    if cursor.rowcount > 0:
                        success_flag = True
            if success_flag:
                flash("Attendance is successfully recorded!", "success")
            else:
                flash("No change in attendance record.", "warning")
            return redirect(url_for("manager.attendance_record"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.mark_attendance")
            flash("Attendance recording failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.attendance_record"))


#Report for attendance
@manager_bp.route("/attendance_report", methods=['GET', 'POST'])
def attendance_report():
    """get the attendance report for the manager"""
    cursor, connection = getCursor()
    # get the attendance report for the therapeutic and class sessions
    therapeutic_report_query = """SELECT u.userID, CONCAT(u.first_name, ' ', u.last_name) AS member_name,
                                         'Private Therapeutic' AS type, s.type AS therapeutic_type, t.date AS therapeutic_date, 
                                         CONCAT(TIME_FORMAT(t.start_time, "%H:%i"), ' - ', TIME_FORMAT(t.end_time, "%H:%i")) AS therapeutic_time,
                                         CONCAT(therapist.first_name, ' ', therapist.last_name) AS therapist_name,
                                         tar.is_attended AS therapeutic_attendance
                                  FROM userrole u
                                  JOIN therapeutic_booking tb ON u.userID = tb.member_id
                                  JOIN therapeutic_attendance_record tar ON tb.therapeutic_booking_id = tar.therapeutic_booking_id
                                  JOIN therapeutic t ON tb.therapeutic_id = t.therapeutic_id
                                  JOIN session s ON t.type_id = s.type_id
                                  JOIN userrole therapist ON t.therapist_id = therapist.userID
                                  WHERE u.role = 'member';"""
    cursor.execute(therapeutic_report_query)
    therapeutic_reports = cursor.fetchall()
    # get the attendance report for the class sessions
    class_reports_query = """SELECT u.userID, CONCAT(u.first_name, ' ', u.last_name) AS member_name, 'Group Class' AS type, 
                                    ci.type AS class_type, cb.date AS class_day, 
                                    CONCAT(TIME_FORMAT(c.start_time, "%H:%i"), ' - ', TIME_FORMAT(c.end_time, "%H:%i")) AS therapeutic_time,
                                    CONCAT(therapist.first_name, ' ', therapist.last_name) AS therapist_name,
                                    car.is_attended AS class_attendance
                             FROM userrole u
                             JOIN class_booking cb ON u.userID = cb.member_id
                             JOIN class_attendance_record car ON cb.class_booking_id = car.class_booking_id
                             JOIN class c ON cb.class_id = c.class_id
                             JOIN class_info ci ON c.type_id = ci.type_id
                             JOIN userrole therapist ON c.therapist_id = therapist.userID
                             WHERE u.role = 'member';"""
    cursor.execute(class_reports_query)
    class_reports = cursor.fetchall()
    return render_template("manager_report_attendance.html", therapeutic_reports=therapeutic_reports, class_reports=class_reports)

#Report for finanical
@manager_bp.route("/financial_report", methods=['GET', 'POST'])
def financial_report():
    """get the financial report for the manager"""
    cursor, connection = getCursor()
    query = """SELECT YEAR(ptr.payment_date) AS year, MONTH(ptr.payment_date) AS month,
                      pty.description AS payment_type, SUM(f.price) AS total_revenue
               FROM payment_transaction ptr
               JOIN fees f ON ptr.fees_id = f.fees_id
               JOIN payment_type pty ON f.payment_type_id = pty.payment_type_id
               GROUP BY YEAR(ptr.payment_date), MONTH(ptr.payment_date), pty.description
               ORDER BY Year, Month, payment_type;"""
    cursor.execute(query)
    financial_reports = cursor.fetchall()
    return render_template("manager_report_financial.html", financial_reports=financial_reports)

#Report for population of classes
@manager_bp.route("/popular_class_report", methods=['GET', 'POST'])
def popular_class_report():
    """get the popular class report for the manager"""
    cursor, connection = getCursor()
    query = """SELECT ci.type, COUNT(cb.class_id) AS booking_count
               FROM class_booking AS cb
               JOIN class AS c ON cb.class_id = c.class_id
               JOIN class_info AS ci ON c.type_id = ci.type_id
               GROUP BY ci.type
               ORDER BY booking_count DESC;"""
    cursor.execute(query)
    popular_class_reports = cursor.fetchall()
    return render_template("manager_report_popular_class.html", popular_class_reports=popular_class_reports)


#Manage session schedule
@manager_bp.route("/session_schedule",  methods=['GET', 'POST'])
def session_schedule():
    """manage the session schedule for the manager"""
    cursor, connection = getCursor()
    # update session availability based on booking
    cursor.execute('UPDATE therapeutic JOIN therapeutic_booking ON therapeutic_booking.therapeutic_id = therapeutic.therapeutic_id SET therapeutic.is_available = 0') 
    connection.commit()
    today = datetime.now().strftime('%Y-%m-%d')   

    query ="""SELECT therapeutic.therapeutic_id, date, start_time, end_time, duration, is_available, session.type, session.description, 
                        fees.fees_name, fees.price, room.room_name, therapeutic_booking.therapeutic_booking_id, 
                        therapeutic_attendance_record.is_attended, therapeutic.therapist_id, CONCAT(userrole.first_name, ' ', userrole.last_name) AS therapist_name
                FROM therapeutic 
                JOIN session ON therapeutic.type_id = session.type_id 
                JOIN fees ON therapeutic.fees_id = fees.fees_id 
                JOIN room ON therapeutic.room_id = room.room_id
                JOIN userrole ON therapeutic.therapist_id = userrole.userID 
                LEFT JOIN therapeutic_booking ON therapeutic.therapeutic_id = therapeutic_booking.therapeutic_id 
                LEFT JOIN therapeutic_attendance_record ON therapeutic_booking.therapeutic_booking_id = therapeutic_attendance_record.therapeutic_booking_id 
                WHERE therapeutic.date >= CURDATE() 
                ORDER BY therapeutic.date, therapeutic.start_time"""
    cursor.execute(query)     # fetches session details
    sessions = cursor.fetchall()
            
    cursor.execute('SELECT type_id, type FROM session')              # fetches session types
    types = cursor.fetchall()
    cursor.execute('SELECT room_id, room_name FROM room')              # fetches room details
    rooms = cursor.fetchall()
    cursor.execute("SELECT * FROM userrole WHERE role = 'therapist' AND is_active = 1")
    therapists = cursor.fetchall()

    booking_member_details = {}
    for field in sessions:
        cursor.execute('SELECT member_id FROM therapeutic_booking WHERE therapeutic_id = %s', (field[0],))
        member_id = cursor.fetchall()
        if member_id:
            cursor.execute('SELECT userID, title, first_name, last_name, position, phone, email, address, date_of_birth, health_information FROM userrole WHERE userID = %s', (member_id[0][0],))
            member_info = cursor.fetchall()
            booking_member_details[field[0]] = member_info[0]
    return render_template('manager_session_schedule.html', sessions=sessions, rooms=rooms, types=types, today=today, booking_member_details=booking_member_details, therapists=therapists)
       
@manager_bp.route("/session_schedule/add_session", methods=['GET','POST'])
def add_session():
    """add a new session"""
    cursor, connection = getCursor()
    required_fields = ["type_id", "date", "start_time", "end_time", "room_id", "price", "therapist_id"]
    field_validators = {
        "type_id": None,
        "date": validate_date,
        "start_time": validate_time,
        "end_time": validate_time,
        "room_id": None,
        "price": validate_decimal,
        "therapist_id": None,
    }
    if request.method == 'POST':
        if not validate_form(request.form, required_fields, field_validators):  # validates that required fields are filled for adding sessions
            return redirect(url_for("manager.session_schedule"))          
        type_id = request.form.get("type_id")
        date = request.form.get("date")
        booking_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        room_id = request.form.get("room_id")
        price = request.form.get("price")
        start_time = parse_time(start_time)
        end_time = parse_time(end_time)
        duration = int((end_time-start_time).total_seconds()/60)
        therapist_id = request.form.get("therapist_id")

        if end_time <= start_time:              # checks if end time is before start time
            flash("End time cannot be before start time!", "danger")
            return redirect(url_for("manager.session_schedule"))
        
        cursor.execute('SELECT * FROM class WHERE therapist_id = %s AND repeat_days LIKE %s AND (start_time BETWEEN %s AND %s OR end_time BETWEEN %s AND %s)', 
                        (therapist_id, f"%{booking_date.strftime('%A')}%", start_time, end_time, start_time, end_time))
        existing_class = cursor.fetchall()
        if existing_class:
            flash("The selected therapist have been scheduled an existing class at this time. Please check the schedule and try again.", "danger")
            return redirect(url_for("manager.session_schedule"))

        cursor.execute('SELECT type FROM session WHERE type_id = %s', (type_id,))   
        session_name = cursor.fetchone()[0]
        fees_name = f"{session_name} - {therapist_id} - {booking_date.strftime('%d-%m-%Y')}"

        cursor.execute('SELECT * FROM therapeutic WHERE date = %s AND room_id = %s AND (start_time = %s OR end_time = %s)', 
                        (date, room_id, start_time, end_time))            # checking if added room is booked at the same time with other therapists or self
        existing_room = cursor.fetchall()
        if existing_room:
            flash("The room is already booked at the selected time. Please choose a different time or room.", "danger")
            return redirect(url_for("manager.session_schedule"))
        

        cursor.execute('SELECT * FROM therapeutic WHERE date = %s AND therapist_id = %s AND (start_time BETWEEN %s AND %s OR end_time BETWEEN %s AND %s)', 
                        (date, therapist_id, start_time, end_time, start_time, end_time))          # checking if added session overlaps with therapist's existing sessions
        existing_sessions = cursor.fetchall()
        if existing_sessions:
            flash("Session overlaps with an existing session. Please check the schedule and try again.", "danger")
            return redirect(url_for("manager.session_schedule"))
        
        try:
            cursor.execute('INSERT INTO fees (fees_name, payment_type_id, price) VALUES (%s, %s, %s)', (fees_name, 2, price))           # adds new fee details into fees table
            # retrieve the generated fee_id
            fees_id = cursor.lastrowid
            cursor.execute('INSERT INTO therapeutic (date, start_time, end_time, duration, type_id, room_id, fees_id, therapist_id, is_available) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                        (date, start_time, end_time, duration, type_id, room_id, fees_id, therapist_id, 1))           # adds new session into therapeutic table
            connection.commit()
            flash ("Session is added successfully!", "success")             # success message
            return redirect(url_for("manager.session_schedule"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.add_session")
            flash("Session failed to be added. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.session_schedule"))

@manager_bp.route("/session_schedule/edit_session/<int:therapeutic_id>", methods=['GET', 'POST'])
def edit_session(therapeutic_id):
    """edit the session"""
    cursor, connection = getCursor()
    required_fields = ["type_id", "date", "start_time", "end_time", "room_id", "price", "therapist_id"]
    field_validators = {
        "type_id": None,
        "date": validate_date,
        "start_time": validate_time,
        "end_time": validate_time,
        "room_id": None,
        "price": validate_decimal,
        "therapist_id": None,
    }
    if request.method == 'POST': 
        if not validate_form(request.form, required_fields, field_validators):  # validates that required fields are filled for editing sessions
            return redirect(url_for("manager.session_schedule"))
        type_id = request.form.get("type_id")
        date = request.form.get("date")
        booking_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        room_id = request.form.get("room_id")
        price = request.form.get("price")
        start_time =parse_time(start_time)
        end_time = parse_time(end_time)
        duration = int((end_time-start_time).total_seconds()/60)
        therapist_id = request.form.get("therapist_id")

        if end_time <= start_time:              # checks if end time is before start time
            flash("End time cannot be before start time!", "danger")
            return redirect(url_for("manager.session_schedule"))
        
        cursor.execute("""SELECT * FROM class 
                          WHERE therapist_id = %s 
                          AND repeat_days LIKE %s 
                          AND ((start_time > %s AND start_time < %s) OR (end_time > %s AND end_time < %s))""",
                        (therapist_id, f"%{booking_date.strftime('%A')}%", start_time, end_time, start_time, end_time))
        existing_class = cursor.fetchall()
        if existing_class:
            flash("The selected therapist have been scheduled an existing class at this time. Please check the schedule and try again.", "danger")
            return redirect(url_for("manager.session_schedule"))
        
        cursor.execute('SELECT * FROM therapeutic WHERE therapeutic_id != %s AND therapist_id = %s AND date = %s AND ((start_time > %s AND start_time < %s) OR (end_time > %s AND end_time < %s))', 
                        (therapeutic_id, therapist_id, date, start_time, end_time, start_time, end_time))              # checking if edited session overlaps with therapist's existing sessions
        existing_sessions = cursor.fetchall()
        if existing_sessions:
            flash("Session overlaps with an existing session. Please check the schedule and try again.", "danger")
            return redirect(url_for("manager.session_schedule"))
        
        cursor.execute('SELECT * FROM therapeutic WHERE therapeutic_id != %s AND date = %s AND room_id = %s AND (start_time = %s OR end_time = %s)', 
                        (therapeutic_id, date, room_id, start_time, end_time))  # checking if the room is booked at the selected time with other therapists or self
        existing_room = cursor.fetchall()
        if existing_room:
            flash("The room is already booked at the selected time. Please choose a different time or room.", "danger")
            return redirect(url_for("manager.session_schedule"))
        
        try:
            cursor.execute('UPDATE fees SET price = %s WHERE fees_id = (SELECT fees_id FROM therapeutic WHERE therapeutic_id = %s)', ( price, therapeutic_id))                  # updates fee details in fees table
            cursor.execute('UPDATE therapeutic SET date = %s, start_time = %s, end_time = %s, duration = %s, type_id = %s, room_id = %s, therapist_id = %s WHERE therapeutic_id = %s', 
                        (date, start_time, end_time, duration, type_id, room_id, therapist_id, therapeutic_id))                # updates session into therapeutic table
            connection.commit()
            if cursor.rowcount > 0:
                flash("Session is updated successfully!", "success")               # success message
                return redirect(url_for("manager.session_schedule"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at manager.edit_session")
            flash("Session failed to be updated. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("manager.session_schedule"))

@manager_bp.route("/session_schedule/cancel_session/<therapeutic_id>", methods=['GET', 'POST'])
def cancel_session(therapeutic_id):
    """cancel the session"""
    cursor, connection = getCursor()
    cursor.execute("""SELECT userrole.email 
                      FROM therapeutic_booking 
                      INNER JOIN userrole ON therapeutic_booking.member_id = userrole.userID 
                      WHERE therapeutic_booking.therapeutic_id = %s""", 
                      (therapeutic_id,))     # fetches email of member booked in for session
    member_emails = cursor.fetchall()

    cursor.execute("""SELECT p.payment_id
						  FROM payment_transaction p
						  JOIN therapeutic_booking t ON t.payment_id = p.payment_id
						  WHERE t.therapeutic_id = %s""", (therapeutic_id,))
    payment_trans = cursor.fetchone()
    
    cursor.execute('SELECT fees_id FROM therapeutic WHERE therapeutic_id = %s', (therapeutic_id,))              # fetches fees_id for deletion
    fees_id = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM therapeutic WHERE fees_id = %s', (fees_id,))
    existing_sessions = cursor.fetchall()
    try:
        cursor.execute('DELETE FROM therapeutic WHERE therapeutic_id = %s', (therapeutic_id,))                # deletes session in therapeutic table
        if len(existing_sessions) == 1:
            cursor.execute('DELETE FROM fees WHERE fees_id = %s', (fees_id,))                                     # uses fees_id to delete fee
        if payment_trans:
            paymentId = payment_trans[0]
            cursor.execute('DELETE FROM payment_transaction WHERE payment_id = %s', (paymentId,))
        connection.commit()
    
        for email in member_emails:                 # to send cancellation email 
            recipient = email[0]
            subject = 'Session Cancelled'
            msg = 'Dear Member,\n\nWe regret to inform you that the session you booked has been cancelled. Please reschedule your session with a therapist. \n\nSincerely,\nHigh Country Health and Wellness Hub'
            send_email(recipient, subject, msg)         # send email
        flash("Session is now cancelled! Cancellation emails have been sent to members who booked this session.", "success")               # success message
        return redirect(url_for("manager.session_schedule"))
    except Exception as e:
        connection.rollback()
        print(f"Error: {e} at manager.cancel_session")
        flash("Session failed to be cancelled. Please try again.", "danger")
    finally:
        closeCursorAndConnection()
    return redirect(url_for("manager.session_schedule"))