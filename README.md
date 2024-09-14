# Job Portal Flask API

This is a RESTful API built with Flask and SQLAlchemy for a job portal system.
It allows users to register as job seekers or employers, post jobs, and apply to jobs.
It integrates with PostgreSQL for data persistence.

## Features
* User Management:
  * Register as a Job Seeker or Employer
  * Login with email and password authentication
  * Passwords hashed for security using werkzeug.security
* Job Listings:
  * Employers can post jobs
  * Job seekers can view all job listings
  * Employers can view applicants for a job
* Applications:
  * Job seekers can apply for jobs
