# This is for the therapist blueprint
# Assigner: Tish
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
import re
from flask import Blueprint
from app.utils import getCursor, closeCursorAndConnection, allowed_file, save_image, parse_time, send_email, verify_access, validate_form, dashboard_router, validate_email, validate_phone, validate_date, validate_password, validate_varchar, validate_text, validate_time, validate_decimal
from datetime import datetime, timedelta


therapist_bp = Blueprint("therapist", __name__, template_folder="templates", static_folder="static", static_url_path="/therapist/static")

@therapist_bp.before_request
def before_request():
    endpoint_access = {
        "therapist_bp.therapist_dashboard": (["therapist"], "home.home"),
        "therapist_bp.therapist_profile": (["therapist"], "home.home"),
        "therapist_bp.update_therapist_profile": (["therapist"], "home.home"),
        "therapist_bp.session_schedule": (["therapist"], "home.home"),
        "therapist_bp.add_session": (["therapist"], "home.home"),
        "therapist_bp.edit_session": (["therapist"], "home.home"),
        "therapist_bp.cancel_session": (["therapist"], "home.home"),
        "therapist_bp.session_attendance": (["therapist, manager"], "home.home"),
    }
    if request.endpoint in endpoint_access:
        roles, redirect_url = endpoint_access[request.endpoint]
        return verify_access(roles, redirect_url)
           
@therapist_bp.route("/")
def therapist_dashboard():                         
    cursor, connection = getCursor()
    today = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')  # show sessions for the next 7 days
    cursor.execute("""SELECT DISTINCT date, session.type 
                      FROM therapeutic 
                      JOIN session ON therapeutic.type_id = session.type_id 
                      WHERE therapist_id = %s AND date BETWEEN %s AND %s ORDER BY date""", 
                      (session.get("id"), today, end_date))
    upcoming = cursor.fetchall()
    return render_template("therapistdashboard.html", username=session.get("username"), upcoming=upcoming)           # displays therapist home page
    
@therapist_bp.route("/profile")
def therapist_profile():
    # We need all the account info for the therapist so we can display it on the profile page
    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM userrole WHERE userID = %s', (session.get("id"),))
    therapist = cursor.fetchone()
    return render_template('therapistprofile.html', therapist=therapist)                
        
@therapist_bp.route("/profile/update", methods=['GET','POST'])
def update_therapist_profile():
    cursor, connection = getCursor()
    required_fields = ['title', 'first_name', 'last_name', 'position', 'phone', 'email', 'therapist_profile']
    field_validators = {
        'title': None,
        'first_name': validate_varchar,
        'last_name': validate_varchar,
        'position': validate_varchar,
        'phone': validate_phone,
        'email': validate_email,
        'therapist_profile': validate_text
    }

    if request.method == 'POST':                           
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("therapist.update_therapist_profile"))        # validates that required fields are filled for updating therapist profile
        title = request.form['title']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        position = request.form['position']
        phone = request.form['phone']
        email = request.form['email']
        therapist_profile = request.form['therapist_profile']

        update_flag = False

        try:     
            if 'profile_image' in request.files and request.files['profile_image'].filename:                  # check if a file is uploaded
                profile_image = request.files['profile_image']
                if not allowed_file(profile_image):
                    flash ('Uploaded file is not a valid image. Only JPG, JPEG, PNG and GIF files are allowed.', 'danger')
                else:
                    image_path = save_image(profile_image)
                    cursor.execute('UPDATE userrole SET profile_image = %s WHERE userID = %s', (image_path, session.get("id"),))             # updates profile image
                    if cursor.rowcount > 0:
                        update_flag = True
            cursor.execute("""UPDATE userrole SET title = %s, first_name = %s, last_name = %s, position = %s, phone = %s, email = %s, therapist_profile = %s WHERE userID = %s""", 
                            (title, first_name.capitalize(), last_name.capitalize(), position.capitalize(), phone, email, therapist_profile.capitalize(), session.get("id")))           # update therapist details
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                update_flag = True
            
            if update_flag:
                flash('Profile is updated successfully!', 'success')   # success message
                return redirect(url_for('therapist.therapist_profile'))
            else:
                flash("No change in profile.", "warning")           # warning message
                return redirect(url_for('therapist.therapist_profile'))
        except Exception as e:
            print(f"Error: {e} at update_therapist_profile")
            flash('Failed to update profile. Please try again.', 'danger')
            return redirect(url_for('therapist.update_therapist_profile'))
        finally:
            closeCursorAndConnection()
    cursor.execute('SELECT title, first_name, last_name, position, phone, email, therapist_profile, profile_image FROM userrole WHERE userID = %s', (session.get("id"),))               # fetches therapist details
    therapist = cursor.fetchone()
    return render_template('updatetherapist.html', therapist=therapist)

@therapist_bp.route("/sessionschedule")
def session_schedule():
    cursor, connection = getCursor()
    cursor.execute('UPDATE therapeutic JOIN therapeutic_booking ON therapeutic_booking.therapeutic_id = therapeutic.therapeutic_id SET therapeutic.is_available = 0')       # update session availability based on room capacity
    connection.commit()
    today = datetime.now().strftime('%Y-%m-%d')   

    cursor.execute("""SELECT therapeutic.therapeutic_id, date, start_time, end_time, duration, is_available, session.type, session.description, 
                             fees.fees_name, fees.price, room.room_name, therapeutic_booking.therapeutic_booking_id, therapeutic_attendance_record.is_attended 
                      FROM therapeutic 
                      JOIN session ON therapeutic.type_id = session.type_id 
                      JOIN fees ON therapeutic.fees_id = fees.fees_id 
                      JOIN room ON therapeutic.room_id = room.room_id 
                      LEFT JOIN therapeutic_booking ON therapeutic.therapeutic_id = therapeutic_booking.therapeutic_id 
                      LEFT JOIN therapeutic_attendance_record ON therapeutic_booking.therapeutic_booking_id = therapeutic_attendance_record.therapeutic_booking_id 
                      WHERE therapeutic.therapist_id = %s AND therapeutic.date >= %s ORDER BY therapeutic.date""", 
                      (session.get("id"), today))      # fetches session details
    sessions = cursor.fetchall()
            
    cursor.execute('SELECT type_id, type FROM session')              # fetches session types
    types = cursor.fetchall()
    cursor.execute('SELECT room_id, room_name FROM room')              # fetches room details
    rooms = cursor.fetchall()

    booking_member_details = {}
    for field in sessions:
        cursor.execute('SELECT member_id FROM therapeutic_booking WHERE therapeutic_id = %s', (field[0],))
        member_id = cursor.fetchone()
        if member_id:
            cursor.execute("""SELECT userID, title, first_name, last_name, position, 
                                     phone, email, address, date_of_birth, health_information 
                              FROM userrole 
                              WHERE userID = %s""", (member_id[0],))
            booking_member_details[field[0]] = cursor.fetchone()
    return render_template('sessionschedule.html', sessions=sessions, rooms=rooms, types=types, today=today, booking_member_details=booking_member_details)

@therapist_bp.route("/addsession", methods=['GET','POST'])
def add_session():
    cursor, connection = getCursor()
    required_fields = ['type_id', 'date', 'start_time', 'end_time', 'room_id', 'price']
    field_validators = {
        'type_id': None,
        'date': validate_date,
        'start_time': validate_time,
        'end_time': validate_time,
        'room_id': None,
        'price': None
    }
    if request.method == 'POST':                                    
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("therapist.session_schedule"))     # validates that required fields are filled for adding sessions
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
        therapist_id = session.get("id")

        if end_time <= start_time:              # checks if end time is before start time
            flash("End time cannot be before start time!", "danger")
            return redirect(url_for("therapist.session_schedule"))
        
        cursor.execute("""SELECT * FROM class 
                          WHERE therapist_id = %s 
                          AND repeat_days LIKE %s 
                          AND (
                            (start_time < %s AND end_time > %s)  -- existing class overlaps with new class
                          OR 
                            (start_time < %s AND end_time > %s )) -- existing class overlaps with new class""",  
                          (therapist_id, f"%{booking_date.strftime('%A')}%", start_time, start_time, end_time, end_time))
        existing_class = cursor.fetchall()
        if existing_class:
            flash("You've been scheduled an existing class at this time. Please check the schedule and try again.", "danger")
            return redirect(url_for("therapist.session_schedule"))

        cursor.execute('SELECT type FROM session WHERE type_id = %s', (type_id,))   
        session_name = cursor.fetchone()[0]
        fees_name = f"{session_name} - {therapist_id} - {booking_date.strftime('%d-%m-%Y')}"

        cursor.execute('SELECT * FROM therapeutic WHERE date = %s AND room_id = %s AND (start_time = %s OR end_time = %s)', (date, room_id, start_time, end_time))            # checking if added room is booked at the same time with other therapists or self
        existing_room = cursor.fetchall()
        if existing_room:
            flash("The room is already booked at the selected time. Please choose a different time or room.", "danger")
            return redirect(url_for("therapist.session_schedule"))

        cursor.execute("""SELECT * FROM therapeutic 
                          WHERE date = %s 
                          AND therapist_id = %s 
                          AND ((start_time > %s AND start_time < %s) OR (end_time > %s AND end_time < %s))""",
                         (date, session.get("id"), start_time, end_time, start_time, end_time))          # checking if added session overlaps with therapist's existing sessions
        existing_sessions = cursor.fetchall()
        if existing_sessions:
            flash("Session overlaps with an existing session. Please check the schedule and try again.", "danger")
            return redirect(url_for("therapist.session_schedule"))
        try:
            cursor.execute('INSERT INTO fees (fees_name, payment_type_id, price) VALUES (%s, %s, %s)', (fees_name, 2, price))           # adds new fee details into fees table
            fees_id = cursor.lastrowid # retrieve the generated fee_id
            cursor.execute("""INSERT INTO therapeutic (date, start_time, end_time, duration, type_id, room_id, fees_id, therapist_id, is_available) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                            (date, start_time, end_time, duration, type_id, room_id, fees_id, session.get("id"), 1))           # adds new session into therapeutic table
            connection.commit()

            flash ("Session is added successfully!", "success")             # success message
            return redirect(url_for("therapist.session_schedule"))
        except Exception as e:
            print(f"Error: {e} at add_session")
            flash ("Failed to add a new session. Please try again.", "danger")             # danger message
            return redirect(url_for("therapist.session_schedule"))
        finally:
            closeCursorAndConnection()
    return render_template('sessionschedule.html')


@therapist_bp.route("/editsession/<therapeutic_id>", methods=['GET', 'POST'])
def edit_session(therapeutic_id):
    cursor, connection = getCursor()
    required_fields = ['type_id', 'date', 'start_time', 'end_time', 'room_id', 'price']
    field_validators = {
        'type_id': None,
        'date': validate_date,
        'start_time': validate_time,
        'end_time': validate_time,
        'room_id': None,
        'price': validate_decimal
    }
    if request.method == 'POST':
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("therapist.update_therapist_profile"))          # validates that required fields are filled for adding sessions
        type_id = request.form.get("type_id")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        room_id = request.form.get("room_id")
        price = request.form.get("price")
        start_time =parse_time(start_time)
        end_time = parse_time(end_time)
        duration = int((end_time-start_time).total_seconds()/60)
        
        cursor.execute("""SELECT * FROM therapeutic WHERE therapeutic_id != %s AND therapist_id = %s AND  date = %s AND ((start_time > %s AND start_time < %s) OR (end_time > %s AND end_time < %s))""", (therapeutic_id, session.get("id"), date, start_time, end_time, start_time, end_time))              # checking if edited session overlaps with therapist's existing sessions
        existing_sessions = cursor.fetchall()
        if existing_sessions:
            flash("Session overlaps with an existing session. Please check the schedule and try again.", "danger")
            return redirect(url_for("therapist.session_schedule"))
        
        cursor.execute('SELECT * FROM therapeutic WHERE therapeutic_id != %s AND date = %s AND room_id = %s AND (start_time = %s OR end_time = %s)', (therapeutic_id, date, room_id, start_time, end_time))  # checking if the room is booked at the selected time with other therapists or self
        existing_room = cursor.fetchall()
        if existing_room:
            flash("The room is already booked at the selected time. Please choose a different time or room.", "danger")
            return redirect(url_for("therapist.session_schedule"))
        try:
            cursor.execute('UPDATE fees SET price = %s WHERE fees_id = (SELECT fees_id FROM therapeutic WHERE therapeutic_id = %s)', ( price, therapeutic_id))                  # updates fee details in fees table
            cursor.execute('UPDATE therapeutic SET date = %s, start_time = %s, end_time = %s, duration = %s, type_id = %s, room_id = %s WHERE therapeutic_id = %s', (date, start_time, end_time, duration, type_id, room_id, therapeutic_id))                # updates session into therapeutic table
            connection.commit()
            flash("Session is updated successfully!", "success")               # success message
            return redirect(url_for("therapist.session_schedule"))
        except Exception as e:
            print(f"Error: {e} at edit_session")
            flash("Failed to update session. Please try again.", "danger")               # danger message
            return redirect(url_for("therapist.session_schedule"))
        finally:
            closeCursorAndConnection()
    return render_template('sessionschedule.html', therapeutic_id=therapeutic_id)

@therapist_bp.route("/cancelsession/<therapeutic_id>", methods=['GET', 'POST'])
def cancel_session(therapeutic_id):
    cursor, connection = getCursor()
    cursor.execute('SELECT userrole.email FROM therapeutic_booking INNER JOIN userrole ON therapeutic_booking.member_id = userrole.userID WHERE therapeutic_booking.therapeutic_id = %s', (therapeutic_id,))     # fetches email of member booked in for session
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
            payment_id = payment_trans[0]
            cursor.execute('DELETE FROM payment_transaction WHERE payment_id = %s', (payment_id,))
        connection.commit()
        for email in member_emails:                 # to send cancellation email 
            recipient = email[0]
            subject = 'Session Cancelled'
            msg = 'Dear Member,\n\nWe regret to inform you that the session you booked has been cancelled. Please reschedule your session with a therapist. \n\nSincerely,\nHigh Country Health and Wellness Hub'
            send_email(recipient, subject, msg)         # send email
        flash("Session is now cancelled! Cancellation emails have been sent to members who booked this session.", "success")               # success message
    except Exception as e:
        print(f"Error: {e} at cancel_session")
        flash("Failed to cancel session. Please try again.", "danger")               # danger message
    finally:
        closeCursorAndConnection()
    return redirect(url_for("therapist.session_schedule", therapeutic_id=therapeutic_id, fees_id=fees_id))     
    
@therapist_bp.route("/attendance/<therapeutic_id>", methods=['GET','POST'])
def session_attendance(therapeutic_id):
    if request.method == 'POST':
        therapeutic_booking_id = request.form.get('therapeutic_booking_id')
        member_id = request.form.get('member_id')
        is_attended = request.form.get('is_attended')
        cursor, connection = getCursor()
        if is_attended is None:                          
            flash("Please record the attendance!", "danger")               # if no attendance input
        else:
            cursor.execute("SELECT therapeutic_booking_id FROM therapeutic_attendance_record WHERE therapeutic_booking_id = %s AND member_id = %s", (therapeutic_booking_id, member_id))          # check if there are existing records
            existing_record = cursor.fetchone()
            
            try:
                if existing_record:
                    cursor.execute("UPDATE therapeutic_attendance_record SET is_attended = %s WHERE therapeutic_booking_id = %s", (is_attended, existing_record[0]))            # updates attendance database
                else:  
                    cursor.execute("INSERT INTO therapeutic_attendance_record (therapeutic_booking_id, member_id, is_attended) VALUES (%s, %s, %s)", (therapeutic_booking_id, member_id, is_attended))           # inserts new attendance in database
                connection.commit()
                flash("Attendance is recorded successfully!", "success")            # success message
            except Exception as e:
                print(f"Error: {e} at session_attendance")
                flash("Failed to record attendance. Please try again.", "danger")
            finally:
                closeCursorAndConnection()
        if session.get("role") == "therapist":
            return redirect(url_for("therapist.session_schedule", therapeutic_id=therapeutic_id))
        elif session.get("role") == "manager":
            return redirect(url_for("manager.session_schedule"))

# @therapist_bp.route("/classattendance")
# def class_attendance():
#     if 'loggedin' in session and session['role'] == 'therapist':             # check if therapist is loggedin 
#         cursor, connection = getCursor()
#         cursor.execute("SELECT class.class_id, class.start_time, class.end_time, class.duration, REPLACE(REPLACE(class.repeat_days, '{', ''), '}', '') AS repeat_days, class_info.type, room.room_name, CONCAT(t.first_name, ' ', t.last_name) AS therapist_name FROM class JOIN class_info ON class.type_id = class_info.type_id JOIN room ON class.room_id = room.room_id JOIN userrole t ON class.therapist_id = t.userID")        # fetches class details
#         class_data = cursor.fetchall()

#         attendance_data = {}
#         for classes in class_data:
#             class_id = classes[0]            
#             cursor.execute("SELECT class_booking.class_id, class_booking.member_id, CONCAT(m.first_name, ' ', m.last_name) AS member_name, class_attendance_record.is_attended, class_booking.class_booking_id FROM class_booking LEFT JOIN class_attendance_record ON class_booking.class_booking_id = class_attendance_record.class_booking_id LEFT JOIN userrole m ON class_booking.member_id = m.userID  WHERE class_booking.class_id = %s", (class_id,))     # fetches attandance data for class
#             attendance_data[class_id] = cursor.fetchall()
#         return render_template("classattendance.html", class_data=class_data, attendance_data=attendance_data)
#     else:
#         flash("Illegal Access!", "danger")             # danger message
#         return redirect(url_for('home.home'))             # redirect to homepage if therapist is not loggedin 
    
# @therapist_bp.route("/classattendance/<class_id>", methods=['GET','POST'])
# def mark_attendance(class_id):
#     if 'loggedin' in session and session['role'] == 'therapist':            # check if therapist is loggedin 
#         if request.method == 'POST':
#             class_booking_id = request.form.get('class_booking_id')
#             member_id = request.form.get('member_id')
#             is_attended = request.form.get('is_attended')
#             cursor, connection = getCursor()
#             if is_attended is None:
#                 flash("Please record the attendance!", "danger")                # if no attendance input
#             else:
#                 cursor.execute("SELECT class_booking_id FROM class_attendance_record WHERE class_booking_id = %s AND member_id = %s", (class_booking_id, member_id))           # check if there are existing records
#                 existing_record = cursor.fetchone()
                
#                 if existing_record:
#                     cursor.execute("UPDATE class_attendance_record SET is_attended = %s WHERE class_booking_id = %s", (is_attended, existing_record[0]))             # updates attendance database
#                 else:  
#                     cursor.execute("INSERT INTO class_attendance_record (class_booking_id, member_id, is_attended) VALUES (%s, %s, %s)", (class_booking_id, member_id, is_attended))         # inserts new attendance in database
#                 connection.commit()
#                 flash("Attendance is recorded successfully!", "success")            # success message
#             return redirect(url_for("therapist.class_attendance", class_id=class_id))
#     else:
#         flash("Illegal Access!", "danger")             # danger message
#         return redirect(url_for('home.home'))             # redirect to homepage if therapist is not loggedin 
