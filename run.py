from app import create_app, db

job_portal_app = create_app()

if __name__ == "__main__":
    job_portal_app.run(debug=True)
