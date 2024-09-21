from datetime import datetime
from job_portal.app.app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(254), unique=True)
    password = db.Column(db.String(254), nullable=False)
    is_employer = db.Column(db.Boolean, default=False)
    sign_up_date = db.Column(db.DateTime, default=datetime.now)

    def __str__(self):
        if not self.is_employer:
            return f"{self.first_name} {self.last_name}, Job Seeker"
        return f"{self.first_name} {self.last_name}, Employer"


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uploader = db.Column(db.Integer, ForeignKey("users.id"))
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    time_posted = db.Column(db.DateTime, default=datetime.now)
    num_applicants = db.Column(db.Integer, default=0)

    poster = relationship("User", backref="posted_jobs")  # Access all jobs posted by a user

    def __str__(self):
        return f"Title: {self.title}, Description: {self.description}, Posted at: {self.time_posted}, Applications: {self.num_applicants}"


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant = db.Column(db.Integer, ForeignKey("users.id"))
    listing = db.Column(db.Integer, ForeignKey("job.id"))
    cv = db.Column(db.Text, nullable=False)
    time_applied = db.Column(db.DateTime, default=datetime.now)

    def __str__(self):
        job = Job.query.filter_by(id=self.listing).first()
        title = job.title
        return f"Title: {title}, Applied on: {self.time_applied.date()}"

    applications = relationship("User", backref="applications")  # Access all applications made by a user
    job = relationship("Job", backref="applications")  # Access all applications for a job