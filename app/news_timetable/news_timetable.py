# This is for the news_timetable blueprint
# Assigner: Elaine
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint
from app.utils import getCursor, send_email, closeCursorAndConnection, verify_access
from datetime import datetime, timedelta
from flask import flash
from flask import request

news_timetable_bp = Blueprint("news_timetable", __name__, template_folder="templates", static_folder="static", static_url_path="/news_timetable/static")
# news_timetable_bp.route("/")

@news_timetable_bp.before_request
def before_request():
    endpoing_access = {
        "news_timetable.timetable_management": (["manager"], "news_timetable.timetable"),
        "news_timetable.delete_class": (["manager"], "news_timetable.timetable"),
        "news_timetable.update_class": (["manager"], "news_timetable.timetable"),
        "news_timetable.add_news": (["manager"], "news_timetable.news"),
        "news_timetable.update_news": (["manager"], "news_timetable.news"),
        "news_timetable.delete_news": (["manager"], "news_timetable.news"),
        "news_timetable.book_class": (["member"], "news_timetable.timetable"),
    }
    if request.endpoint in endpoing_access:
        roles, redirect_url = endpoing_access[request.endpoint]
        return verify_access(roles, redirect_url)

@news_timetable_bp.route("/timetable")
def timetable():
    cursor, conn = getCursor()
    cursor.execute(""" SELECT c.class_id, ci.type, ci.description, TIME_FORMAT(c.start_time, "%H:%i") AS start_time, TIME_FORMAT(c.end_time, "%H:%i") AS end_time, 
                              c.repeat_days, r.room_name, u.userID AS therapist_id, CONCAT(u.first_name, ' ', u.last_name) AS therapist_name, 
                              u.position, u.therapist_profile, u.profile_image
                       FROM class AS c
                   JOIN class_info AS ci ON c.type_id = ci.type_id
                   JOIN room AS r ON c.room_id = r.room_id
                   JOIN userrole AS u ON c.therapist_id = u.userID
                   WHERE c.repeat_days IS NOT NULL; """)
    classes_raw = cursor.fetchall()
    cursor.execute("""SELECT class_id, date, (15 - COALESCE(COUNT(*), 0)) AS remaining_slots FROM class_booking GROUP BY class_id, date""")
    remaining_slots = {f"{slot[0]}_{slot[1]}": slot[2] for slot in cursor.fetchall()}
    conn.close()
    #convert repeat_days to lists for JSON parsing
    classes = []
    for class_tuple in classes_raw:
        class_list = list(class_tuple)
        class_list[5] = list(class_tuple[5]) if class_tuple[5] else []
        classes.append(class_list)
    return render_template("timetable.html", classes=classes, therapist_id = session.get("id"), role=session.get("role"), membership_status = session.get("membership_status"), remaining_slots=remaining_slots)

@news_timetable_bp.route("/book_class", methods=["GET", "POST"])
def book_class():
    cursor, conn = getCursor()
    if request.method == "POST":
        try:
            class_id = request.form.get("class_id")
            member_id = session.get("id")
            date = request.form.get("class_date")
            cursor.execute("SELECT * FROM class_booking WHERE class_id = %s AND date = %s AND member_id = %s", (class_id, date, member_id))
            booking_duplicate_check  = cursor.fetchone()
            if booking_duplicate_check:
                flash("You already booked this class, please do not book again!", "danger")
                return redirect(url_for("news_timetable.timetable"))
            query = """INSERT INTO class_booking (member_id, class_id, date) VALUES (%s, %s, %s);"""
            cursor.execute(query, (member_id, class_id, date))
            new_booking_id = cursor.lastrowid
            query = """INSERT INTO class_attendance_record (class_booking_id, member_id, is_attended) VALUES (%s, %s, %s);"""
            cursor.execute(query, (new_booking_id, member_id, 1))
            conn.commit()
            affected_rows = cursor.rowcount
            if affected_rows > 0:
                flash("Class booked successfully!", "success")
                return redirect(url_for("news_timetable.timetable"))
        except Exception as e:
            conn.rollback()
            print(f"Error: {e} at news_timetable.book_class")
            flash("Booking failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection()
    return redirect(url_for("news_timetable.timetable"))


@news_timetable_bp.route("/timetable_management", methods=["GET", "POST"])
def timetable_management():
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    cursor, conn = getCursor()
    cursor.execute("SELECT userID, CONCAT(first_name, ' ', last_name) AS therapist_name FROM userrole WHERE role='therapist' AND is_active = 1;") # fetches therapist
    therapists = cursor.fetchall()
    cursor.execute("SELECT room_id, room_name FROM room") # fetches room details
    rooms = cursor.fetchall()
    cursor.execute("SELECT ci.type_id, ci.type FROM class_info ci LEFT JOIN class c ON ci.type_id = c.type_id WHERE c.class_id IS NULL;") # fetches class details
    class_info = cursor.fetchall()
    query = """SELECT c.class_id, ci.*, TIME_FORMAT(c.start_time, "%H:%i") AS start_time, TIME_FORMAT(c.end_time, "%H:%i") AS end_time, 
                      c.repeat_days, r.room_id, r.room_name, u.userID AS therapist_id, CONCAT(u.first_name, ' ', u.last_name) AS therapist_name
               FROM class AS c
               JOIN class_info AS ci ON c.type_id = ci.type_id
               JOIN room AS r ON c.room_id = r.room_id
               JOIN userrole AS u ON c.therapist_id = u.userID
               WHERE c.repeat_days IS NOT NULL;"""
    cursor.execute(query)
    classes_raw = cursor.fetchall()
    conn.close()
    classes = []
    for class_tuple in classes_raw:
        class_list = list(class_tuple)
        class_list[6] = list(class_tuple[6]) if class_tuple[6] else []
        classes.append(class_list)
    return render_template("timetable_management.html", classes=classes, therapists=therapists, rooms=rooms, class_info=class_info, role=session.get("role"), weekdays=weekdays)

@news_timetable_bp.route("/update_class", methods=["GET", "POST"])
def update_class():
    cursor, conn = getCursor()
    try:
        class_id = request.form.get("class_id")
        class_type_id = request.form.get("class_type_id")
        class_name = request.form.get("class_name")
        description = request.form.get("class_description")
        start_time = request.form.get("start_time")
        end_time = (datetime.strptime(start_time, "%H:%M") + timedelta(hours=1)).strftime("%H:%M")
        selected_days = request.form.getlist("repeat_days")
        repeat_days = ",".join(selected_days)
        day_numbers = {day: i+2 for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])}
        room = request.form.get("room")
        therapist = request.form.get("therapist")
        
        if selected_days == []:
            flash("Failed updated! Please select at least one day for the class.", "danger")
            return redirect(url_for("news_timetable.timetable_management"))
        elif not class_name or not description or not start_time or not room or not therapist:
            flash("Failed updated! Please fill in all fields.", "danger")
            return redirect(url_for("news_timetable.timetable_management"))

        # check if class conflicts with existing classes
        repeat_days_conditions = " OR ".join([f"repeat_days LIKE '%{day}%'" for day in selected_days])
        if class_id:
            cursor.execute(f"""SELECT * FROM class WHERE ({repeat_days_conditions}) AND start_time = %s AND (room_id = %s OR therapist_id = %s) AND class_id != %s;""", (start_time, room, therapist, class_id))
        else:
            cursor.execute(f"""SELECT * FROM class WHERE ({repeat_days_conditions}) AND start_time = %s AND (room_id = %s OR therapist_id = %s);""", (start_time, room, therapist))
        existing_class = cursor.fetchall()
        if existing_class:
            flash("This class conflicts with another classes. Please try again.", "danger")
            return redirect(url_for("news_timetable.timetable_management"))
        
        # check if class conficts with therapist's existing therapy sessions
        date_conditions = ','.join(str(day_numbers[day]) for day in selected_days)
        cursor.execute(f"""SELECT therapeutic_id, date
                           FROM therapeutic 
                           WHERE therapist_id = %s 
                           AND DAYOFWEEK(date) IN ({date_conditions})
                           AND ((start_time > %s AND start_time < %s) OR (end_time > %s AND end_time < %s))""", 
                           (therapist, start_time, end_time, start_time, end_time,))
        existing_session = cursor.fetchall()
        if existing_session:
            flash("This class conflicts with therapist's existing therapy sessions. Please try again.", "danger")
            return redirect(url_for("news_timetable.timetable_management"))
        
        # check class is already added or not
        if class_type_id:
            cursor.execute("SELECT * FROM class_info WHERE UPPER(type) = UPPER(%s) AND type_id != %s", (class_name, class_type_id))
        else:
            cursor.execute("SELECT * FROM class_info WHERE UPPER(type) = UPPER(%s)", (class_name,))
        exist_class = cursor.fetchall()
        if exist_class:
            flash("Class already exists, please do not add again!", "danger")
            return redirect(url_for("news_timetable.timetable_management"))
        # update class
        if class_id:
            query = """UPDATE class_info SET type = %s, description = %s WHERE type_id = %s;"""
            cursor.execute(query, (class_name, description, class_type_id))
            query = """UPDATE class SET repeat_days = %s, start_time = %s, end_time = %s, room_id = %s, therapist_id = %s WHERE class_id = %s;"""
            cursor.execute(query, (repeat_days, start_time, end_time, room, therapist, class_id))
            success_message = "Class updated successfully!"
        # add new class
        else:
            query = """INSERT INTO class_info (type, description) VALUES (%s, %s);"""
            cursor.execute(query, (class_name, description))
            new_class_id = cursor.lastrowid
            query = """INSERT INTO class (type_id, repeat_days, start_time, end_time, duration, room_id, therapist_id) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(query, (new_class_id, repeat_days, start_time, end_time, 60, room, therapist))
            success_message = "Class added successfully!"
        conn.commit()
        flash(success_message, "success")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e} at news_timetable.update_class")
        flash("Class addition failed. Please try again.", "danger")
    finally:
        closeCursorAndConnection()
    return redirect(url_for("news_timetable.timetable_management"))
            
@news_timetable_bp.route("/delete_class", methods=["GET", "POST"])
def delete_class():
    cursor, conn = getCursor()
    class_id = request.form.get("class_id")
    class_type_id = request.form.get("class_type_id")
    cursor.execute("SELECT u.email FROM class_booking cb INNER JOIN userrole u ON cb.member_id = u.userID WHERE cb.class_id = %s", (class_id,))
    member_emails = cursor.fetchall()
    try:
        cursor.execute("DELETE FROM class WHERE class_id = %s;", (class_id,))
        cursor.execute("DELETE FROM class_info WHERE type_id = %s;", (class_type_id,))
        conn.commit()
        flash("Class deleted successfully! Cancellation emails have been sent to members who booked this class.", "success")
        for email in member_emails:                 # to send cancellation email 
            recipient = email[0]
            subject = 'Class Cancelled'
            msg = 'Dear Member,\n\nWe regret to inform you that the class you booked has been cancelled. Sorry for any inconvenience. \n\nSincerely,\nHigh Country Health and Wellness Hub'
            send_email(recipient, subject, msg)         # send email
    except Exception as e:
        conn.rollback()
        print(f"Error: {e} at news_timetable.delete_class")
        flash("Class deletion failed. Please try again.", "danger")
    finally:
        closeCursorAndConnection()
    return redirect(url_for("news_timetable.timetable_management"))

@news_timetable_bp.route("/news")
def news():
    db_cursor, db_connection = getCursor()
    try:
        query = """
        SELECT news.title, news.content, news.publish_time, userrole.first_name, userrole.last_name, news.news_id
        FROM news
        JOIN userrole ON news.manager_Id = userrole.userID
        ORDER BY news.publish_time DESC
        """
        db_cursor.execute(query)  
        news_items = db_cursor.fetchall()
    finally:
        db_cursor.close()
        db_connection.close()
    return render_template("news.html", news_items=news_items, role=session.get("role"))

@news_timetable_bp.route("/add_news", methods=["GET", "POST"])
def add_news():
    # This route processes the form submission for adding a new news item.
    db_cursor, db_connection = getCursor()
    title = request.form['title']
    content = request.form['content']
    manager_id = session.get('id')  # Assuming manager's user_id is stored in session
    
    if not manager_id:
        flash('You must be logged in to add news.', 'danger')
        return redirect(url_for('news_timetable.news'))
    try:
        query = """
        INSERT INTO news (title, content, publish_time, manager_Id)
        VALUES (%s, %s, %s, %s)
        """
        db_cursor.execute(query, (title, content, datetime.now(), manager_id))
        db_connection.commit()
        flash('News item added successfully.', 'success')
    except Exception as e:
        db_connection.rollback()
        print(f"Error: {e} at news_timetable.add_news")
        flash('An error occurred while adding the news item. Please try again.', 'danger')
    finally:
        db_cursor.close()
        db_connection.close()
    return redirect(url_for('news_timetable.news'))

@news_timetable_bp.route("/update_news",  methods=["GET", "POST"])
def update_news():
    # This route processes the form submission for updating a news item.
    db_cursor, db_connection = getCursor()
    news_id = request.form['news_id']
    title = request.form['title']
    content = request.form['content']
    manager_id = session.get('id')  # Assuming manager's user_id is stored in session
    print(news_id, manager_id)

    if not manager_id:
        flash('You must be logged in to update news.', 'danger')
        return redirect(url_for('news_timetable.news'))
    try:
        query = """UPDATE news SET title = %s, content = %s WHERE news_id = %s"""
        db_cursor.execute(query, (title, content, news_id))
        db_connection.commit()
        if db_cursor.rowcount > 0:
            flash('News updated successfully.', 'success')
        else:
            flash('Updated failed, please try again.', 'danger')
    except Exception as e:
        db_connection.rollback()
        print(f"Error: {e} at news_timetable.update_news")
        flash('An error occurred while updating the news item. Please try again.', 'danger')
    finally:
        db_cursor.close()
        db_connection.close()
    return redirect(url_for('news_timetable.news'))

@news_timetable_bp.route("/delete_news",  methods=["GET", "POST"])
def delete_news():
    # This route processes the form submission for deleting a news item.
    db_cursor, db_connection = getCursor()
    news_id = request.form['news_id']
    manager_id = session.get('id')  # Assuming manager's user_id is stored in session
    print(news_id, manager_id)

    if not manager_id:
        flash('You must be logged in to delete news.', 'danger')
        return redirect(url_for('news_timetable.news'))
    try:
        query = """DELETE FROM news WHERE news_id = %s"""
        db_cursor.execute(query, (news_id,))
        db_connection.commit()
        if db_cursor.rowcount > 0:
            flash('News deleted successfully.', 'success')
        else:
            flash('Deletion failed, please try again.', 'danger')
    except Exception as e:
        db_connection.rollback()
        print(f"Error: {e} at news_timetable.delete_news")
        flash('An error occurred while deleting the news item. Please try again.', 'danger')
    finally:
        db_cursor.close()
        db_connection.close()
    return redirect(url_for('news_timetable.news'))

