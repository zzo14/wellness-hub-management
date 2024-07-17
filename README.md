# High Country Health and Wellness Hub Management System 

Welcome to the High Country Health and Wellness Hub Management System. This Flask-based web application is designed to streamline the management of member details, class schedules, therapeutic session bookings, and much more for a wellness club situated on a high-country farm in Canterbury. The system is built with security, usability, and comprehensive management in mind, catering to members, therapists, and managers with tailored access and functionalities.

## Showcase
Check out our live demo here: [live demo](http://groupwow.pythonanywhere.com/)

## Requirements
 - Python 3.12
 - Flask
 - MySQL
 - Javascript
 - Other dependencies listed in requirements.txt

## Features
 - **User Authentication**: Robust authentication system for Members, Therapists, and Managers with password hashing and salting.
 - **Dynamic Role-Based Access Control**: Tailored access to functionalities based on user roles to enhance security and user experience.
 - **Scheduling System**: Allows booking and management of health and wellness classes and therapeutic sessions.
 - **Interactive Timetables**: Therapists and managers can manage their schedules, and members can book classes or sessions.
 - **Comprehensive Reporting**: Includes financial reports, attendance tracking, and subscription management for comprehensive oversight.
 - **Responsive Web Design**: Ensures that the application is accessible on a variety of devices, enhancing user interaction.

## Installation and Setup
 - Clone the repository: `git clone https://github.com/LUMasterOfAppliedComputing2024S1/COMP639S1_Group_W.git`
 - Install the required packages: `pip install -r requirements.txt`
 - Set up the database using the provided MySQL scripts.
 - Change `dbuser` and `dbpass` in `app/connect.py` to your MySQL username and password.
 - Run the application: `flask run`

## Login Information
The application includes a login system with separate dashboards for three user roles: Member, Therapist, and Manager.

### Member
 - Username: john_doe
 - Password: 123456Zzz!
 - Access: Manage profile, book classes and sessions, manage bookings, manage membership details, and view news.

### Therapist
 - Username: jane_doe
 - Password: 123456Zzz!
 - Access: Manage profile, manage own session schedules, view bookings, record attendance, and view news.

### Manager
 - Username: admin
 - Password: 123456Zzz!
 - Access: Full control over user profiles, financial transactions, class and session schedules, comprehensive reporting, and other management.

## Acknowledgements
Thanks to the team members who contributed to this project:
 - Menglin Chen
 - Letitia Sie
 - Loo See Yin
 - Ren Wang
 - Patrick Zou

