from app import create_app
from app.member.member import member_bp

app = create_app()
if __name__ == "__main__":
    app.run()