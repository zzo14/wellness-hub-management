from flask import Flask
from datetime import timedelta
import os


def create_app():
    app = Flask(__name__)

    # this is where you import the blueprints
    from app.home import home_view
    from app.auth import auth
    from app.member import member
    from app.therapist import therapist
    from app.manager import manager
    from app.news_timetable import news_timetable

    app.secret_key = "key"
    app.permanent_session_lifetime = timedelta(hours=24)
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/image/profile_image")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # this is where you register the blueprints
    app.register_blueprint(home_view.home_bp)
    app.register_blueprint(auth.auth_bp, url_prefix="/auth")
    app.register_blueprint(member.member_bp, url_prefix="/member")
    app.register_blueprint(therapist.therapist_bp, url_prefix="/therapist")
    app.register_blueprint(manager.manager_bp, url_prefix="/manager")
    app.register_blueprint(news_timetable.news_timetable_bp, url_prefix="/news_timetable")

    return app
