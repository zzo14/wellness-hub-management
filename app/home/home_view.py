# This is for the home blueprint
# Assigner: Mavis
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint
from flask import request
from app.utils import getCursor, closeCursorAndConnection, dashboard_router

home_bp = Blueprint("home", __name__, template_folder="templates", static_folder="static", static_url_path="/home/static")


# Home page
@home_bp.route("/")
def home():
    if "loggedin" in session:
        return dashboard_router(session.get("role"))
    classes = []
    remaining_slots = {}
    cursor, conn = getCursor()
    query = """ SELECT c.class_id, ci.type, ci.description, TIME_FORMAT(c.start_time, "%H:%i") AS start_time, TIME_FORMAT(c.end_time, "%H:%i") AS end_time, 
                        c.repeat_days, r.room_name, u.userID AS therapist_id, CONCAT(u.first_name, ' ', u.last_name) AS therapist_name, u.position, u.therapist_profile, u.profile_image
                    FROM class AS c
                    JOIN class_info AS ci ON c.type_id = ci.type_id
                    JOIN room AS r ON c.room_id = r.room_id
                    JOIN userrole AS u ON c.therapist_id = u.userID
                    WHERE c.repeat_days IS NOT NULL; """
    cursor.execute(query)
    classes_raw = cursor.fetchall()
    query = """SELECT class_id, date, (15 - COALESCE(COUNT(*), 0)) AS remaining_slots FROM class_booking GROUP BY class_id, date"""
    cursor.execute(query)
    remaining_slots = {f"{slot[0]}_{slot[1]}": slot[2] for slot in cursor.fetchall()}
    classes = []
    for class_tuple in classes_raw:
        class_list = list(class_tuple)
        class_list[5] = list(class_tuple[5]) if class_tuple[5] else []
        classes.append(class_list)

    class_query = """ SELECT * FROM class_info; """
    cursor.execute(class_query)
    class_info = cursor.fetchall()

    therapist_query = """ SELECT role, first_name, last_name, therapist_profile, profile_image FROM userrole WHERE role = 'therapist' AND is_active = 1; """
    cursor.execute(therapist_query)
    therapists = cursor.fetchall()

    session_query = """ SELECT * FROM session; """
    cursor.execute(session_query)
    sessions = cursor.fetchall()

    return render_template("home.html", classes=classes, remaining_slots=remaining_slots, class_info=class_info, therapists = therapists, sessions = sessions)

@home_bp.route("/price")
def price():
    cursor, connection = getCursor()
    cursor.execute("SELECT * FROM fees")
    prices = cursor.fetchall()
    membership_fees, session_fees = [], []
    for price in prices:
        if price[2] == 1:
            membership_fees.append(price)
        else:
            if '-' in price[1]:
                price = (price[0], price[1].split('-')[0], price[2], price[3])
            session_fees.append(price)
    closeCursorAndConnection()
    return render_template("price.html", membership_fees=membership_fees, session_fees=session_fees)
