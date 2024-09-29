from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import User, Job, Application
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import check_required_fields, allowed_file, jwt_redis_blocklist
from datetime import timedelta
from cloud_storage import upload_to_gcs, dowload_from_gcs
import re, os


def register_routes(app, db):
    # Route to register onto the site
    @app.route("/register", methods=["POST"])
    def register():
        # Check if all fields have been provided
        required_fields = ["first name", "last name", "email", "password", "is_employer"]
        is_valid, missing_fields = check_required_fields(required_fields)

        if not is_valid:
            return jsonify({"error": "Missing fields", "Missing fields": missing_fields}), 400

        data = request.get_json()
        first_name = data.get("first name")
        last_name = data.get("last name")
        email = data.get("email")
        is_employer = data.get("is_employer")
        password = data.get("password")

        # Validate data input and type
        if not all(
            [
                isinstance(first_name, str),
                isinstance(last_name, str),
                isinstance(email, str),
                isinstance(is_employer, bool),
                isinstance(password, str),
            ]
        ):
            return jsonify({"error": "Invalid data. Check data types and format"}), 422

        if not re.match(r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$", email):
            return jsonify({"error": "Invalid email"})
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()]).{8,}$", password
        ):
            return jsonify(
                {"error": "Password must be at least 8 characters and contain an uppercase, lowercase and special character"}
                ), 422
        password = generate_password_hash(password)

        # Create a new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_employer=is_employer,
        )
        try:
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"message": "User registered successfully"}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # Login
    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if password:
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                # track which users are logged in
                expires = timedelta(hours=24)
                access_token = create_access_token(
                    identity=user.id)
                return jsonify({"message": "Login successful","access token":access_token})

        return jsonify({"error": "Invalid email or password"}), 401

    # Create or view job listings
    @app.route("/jobs", methods=["GET", "POST"])
    @jwt_required()
    def jobs():
        if request.method == "GET":
            # Get all job listings
            jobs = Job.query.all()

            if not jobs:
                return jsonify({"message": "No job listings available."}), 200

            jobs_list = []
            for job in jobs:
                jobs_list.append(str(job))
            return jsonify({"Job Listings": jobs_list}), 200

        if request.method == "POST":

            user_id = get_jwt_identity()
            print(user_id)

            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found."}), 404

            if not user.is_employer:
                return jsonify({"error": "Only employers can post jobs"}), 403

            try:
                data = request.get_json()
                required_fields = ["title", "description"]
                is_valid, missing_fields = check_required_fields(required_fields)
                if not is_valid:
                    return jsonify(
                        {"error": "Missing fields","Missing fields": missing_fields}), 400

                new_job = Job(
                    uploader=user.id,
                    title=data.get("title"),
                    description=data.get("description"),
                )
                db.session.add(new_job)
                db.session.commit()
                return jsonify({"message": "Job posted successfully"}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

    # View a specific listing
    @app.route("/jobs/<int:id>")
    def get_job(id):
        job = Job.query.get(id)

        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify({"Job listing": str(job)})

    # Apply for a job
    @app.route("/jobs/<int:id>/apply", methods=["POST"])
    @jwt_required()
    def apply(id):

        user_id = get_jwt_identity()
        applicant = User.query.get(user_id)

        if applicant.is_employer:
            return jsonify({"error": "Only job seekers can apply for jobs"}), 403

        job = Job.query.get(id)

        cv = request.files.get("CV")
        if not cv:
            return jsonify({"error": "CV not uploaded"}), 400

        if not allowed_file(cv.filename):
            return jsonify({"error": "Unsupported file type."}), 415

        try:
            destination_file_name = cv.filename
            bucket_name = os.getenv('BUCKET_NAME')
            print (bucket_name)
            cv_url = upload_to_gcs(cv, destination_file_name, bucket_name)

            new_application = Application(
                applicant=applicant.id, listing=job.id, cv=cv_url)
            
            db.session.add(new_application)
            job.num_applicants += 1
            db.session.commit()
            return jsonify({"message": "Application submitted"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # Job seeker applications
    @app.route("/applications")
    @jwt_required()
    def applications():

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found."})

        if user.is_employer:
            return({"error": "Only job seekers can apply for jobs."}), 403

        applications = []
        for application in user.applications:
            applications.append(str(application))

        return jsonify({"Applications": applications}), 200

    @app.route("/logout")
    @jwt_required()
    def logout():
        jti = get_jwt().get("jti")
        jwt_redis_blocklist.set(jti, "", ex=timedelta(hours=24))
        return jsonify(message="User logged out, Access token revoked"), 200
