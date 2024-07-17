# This is for the member blueprint
# Assigner: Ren
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from flask import Blueprint
from flask import current_app
from .models.User import User
from .models.Session import Session
from werkzeug.utils import secure_filename
from app.utils import getCursor, verify_access, validate_form, dashboard_router, validate_email, validate_phone, validate_date, validate_password, validate_varchar, validate_text, validate_time, validate_decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  


member_bp = Blueprint('member', __name__, template_folder="templates", static_folder="static", static_url_path="/member/static")

@member_bp.before_request
def before_request():
    endpoint_access = {
        "member.member_dashboard": (["member"], "home.home"),
        "member.member_profile": (["member"], "home.home"),
        "member.manage_profile": (["member"], "home.home"),
        "member.session_schedule": (["member"], "home.home"),
        "member.booking": (["member"], "home.home"),
        "member.cancel_booking": (["member"], "home.home"),
        "member.membership_details": (["member"], "home.home"),
        "member.cancel_membership": (["member"], "home.home"),
    }
    if request.endpoint in endpoint_access:
        roles, redirect_url = endpoint_access[request.endpoint]
        return verify_access(roles, redirect_url)


@member_bp.route("/member_dashboard")
def member_dashboard():
    """Display member dashboard."""
    cursor, connection = getCursor()
    member_id = session.get("id")
    query = "SELECT * FROM userrole WHERE userID = %s AND role = 'member' LIMIT 1;"
    cursor.execute(query, (member_id,))
    member = cursor.fetchone()
    if "membership_status" in session and "validity_days" in session:
        if session["membership_status"] == 0:
            flash("Your membership has expired. Please renew your membership.", "danger")
        else:
            if session.get("validity_days") < 30:
                flash(f"Your membership will expire in {session.get('validity_days')}. Please renew your membership.", "warning")
    return render_template("member_dashboard.html", member=member)

# User functions
@member_bp.route("/member_profile")
def member_profile():
    member_id = session.get("id")
    member = User.getUserById(member_id)
    return render_template(
        "member_profile.html", member=member)

@member_bp.route("/manage_profile", methods=["GET", "POST"])
def manage_profile():
    """Display and update member profile."""
    member_id = session.get("id")
    member = User.getUserById(member_id)
    member_info = {
        "title": member.title,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "position": member.position,
        "phone": member.phone,
        "email": member.email,
        "date_of_birth": member.date_of_birth,
        "address": member.address,
        "health_information": member.health_information,
        "profile_image": member.profile_image
    }

    required_fields = ["title", "first_name", "last_name", "position", "phone", "email", "date_of_birth", "address"]
    field_validators = {
        "title": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "phone": validate_phone,
        "email": validate_email,
        "date_of_birth": validate_date,
        "address": None,
    }

    if request.method == "POST":
        user = dict()
        for key, value in request.form.items():
            if value != '':
                user[key] = value
        
        if not validate_form(request.form, required_fields, field_validators): # validate form data 
            return render_template("manage_profile.html", member_info=member_info)
        if len(user) == 0:
            flash("Please edit your profile to update.", "danger")
            return render_template("manage_profile.html", member_info=member_info)

        try:
            if 'profile_image' in request.files and request.files['profile_image'].filename:
                profile_image = request.files['profile_image']
                if profile_image.filename.split('.')[-1] not in ALLOWED_EXTENSIONS:
                    flash("Uploaded file is not a valid image. Only JPG, JPEG, PNG and GIF files are allowed.", "danger")
                    return render_template("manage_profile.html", member_info=member_info)
                filename = secure_filename(profile_image.filename)
                timeStamp = datetime.now().strftime("%Y%m%d%H%M%S")
                unique_name = f"{timeStamp}_{filename}"
                img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
                profile_image.save(img_path)
                user['profile_image'] = unique_name
        except Exception as err:
            print(f"upload file error: {err} at member.manage_profile")
        result = User.updateUser(member_id, user)
        if result:
            flash("Profile is updated successfully!", "success")
            return redirect(url_for("member.member_profile"))
        else:
            flash("No change in profile.", "warning")
            return redirect(url_for("member.member_profile"))
    return render_template("manage_profile.html", member_info=member_info)


# Therapist functions
@member_bp.route("/therapist_list")
def therapist_list():
    """Display list of therapists and their sessions."""
    loggedin = session.get("loggedin")
    therapists = User.getUsersByRole('therapist')
    sessions = {}
    for therapist in therapists: 
        sessions[therapist.userID] = User.getSessionsByTherapist(therapist.userID) # get sessions by therapist
    return render_template("therapist_list.html", therapists=therapists, sessions=sessions, loggedin=loggedin)


# Session functions
@member_bp.route("/session_schedule", defaults={'therapistId': None})
@member_bp.route("/session_schedule/<therapistId>")
def session_schedule(therapistId):
    """Display session schedule for a therapist. If therapistId is None, display all sessions."""
    if therapistId:
        therapist = User.getUserById(therapistId) # get therapist by id
    else:
        therapist = None # if no therapist id, set therapist to None
    sessions = Session.getSessionsByTherapistId(therapistId)
    membership_status = session.get("membership_status")
    return render_template("session_schedule.html", sessions=sessions, therapist=therapist, membership_status=membership_status)

@member_bp.route("/session_book/<therapeutic_id>", methods=['GET', 'POST'])
def session_book(therapeutic_id):
    """Book a session by therapeutic id."""
    therapy = Session.getSessionByTherapeuticId(therapeutic_id)
    if request.method == "POST":
        therapist_id = request.form.get('therapist_id')
        booking_succeeded = Session.bookSessionById(session['id'], therapeutic_id, therapy.fees_id, therapy.price)
        if booking_succeeded:
            flash("Booking successful! Session fees have been paid!", "success")
        else:
            flash("Booking failed. Please try again.", "danger")
        if therapist_id:
            return redirect(url_for('member.session_schedule', therapistId=therapist_id))
        return redirect(url_for('member.session_schedule'))  # Redirect to session schedule page after booking

    return render_template("session_schedule.html", sessions=[therapy]) 


# Booking management functions
@member_bp.route('/booking', methods=['GET'])
def booking():
    """Display all bookings for the current user."""
    try:
        member_id = session.get('id')
        bookings = Session.getAllBookingsbyID(member_id)
        return render_template('booking.html', bookings=bookings, date=datetime.now().date())
    except Exception as e:
        print('Error fetching bookings:', e)
        flash('Error fetching bookings', 'error')
        return redirect(url_for('member.member_dashboard'))
    
@member_bp.route('/booking/cancel', methods=['POST'])
def cancel_booking():
    """Cancel a booking."""
    bookingId = request.form.get('bookingId')
    bookingType = request.form.get('bookingType')
    therapeuticId = request.form.get('therapeuticId')

    try:
        if bookingType == 'class':
            Session.cancelClassBooking(bookingId)
            msg = 'Class Booking cancelled successfully!'
        elif bookingType == 'therapeutic':
            Session.cancelTherapeuticBooking(bookingId, therapeuticId)
            msg = 'Session Booking cancelled successfully! Payment refunded!'
        else:
            raise ValueError('Invalid booking type') # Raise an error if booking type is invalid
        flash(msg, 'success')
    except Exception as e:
        print('Error canceling booking:', e)
        flash('Error canceling booking', 'error')

    return redirect(url_for('member.booking'))

# Membership functions
@member_bp.route("/membership", methods=['GET'])
def membership_details():
    """Display membership details."""
    member_id = session.get("id") 
    validity_days = session.get("validity_days")
    membership_detail = User.getMembershipDetailById(member_id)
    membership_payments = User.getMembershipPaymentsById(member_id)
    return render_template("membership_details.html",
        membership_detail=membership_detail,
        membership_payments=membership_payments,
        validity_days=validity_days)

@member_bp.route("/cancel_membership", methods=['GET', 'POST'])
def cancel_membership():
    """Cancel membership."""
    member_id = session.get("id")
    if request.method == "POST":
        cancel_successed = User.cancelMembership(member_id)
        refund_successed = User.refundMembershipPayment(member_id)
        if cancel_successed and refund_successed:
            session["membership_status"] = 0
            session["validity_days"] = 0 #new_expiry_date is expiry_data, and type is datetime.datetime
            flash("Membership cancelled successfully! Membership fees have been refunded.", "success")
            return redirect(url_for("member.membership_details"))
        else:
            flash("Error cancelling membership", "danger")
    return redirect(url_for("member.membership_details"))
