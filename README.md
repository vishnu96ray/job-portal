# job-portal-backend

A modern job portal application built with FastAPI and Python, providing a comprehensive platform for job seekers and employers to connect.

## 🚀 Features

### For Job Seekers
- User registration and authentication
- Profile management with resume upload
- Job search with advanced filters
- Job application management
- Bookmark/save jobs
- Application tracking
- Email notifications

### For Employers
- Company registration and profile management
- Job posting and management
- Applicant tracking system
- Resume viewing and downloading
- Job analytics and insights
- Bulk job operations

### Admin Features
- User and company management
- Job moderation
- System analytics
- Content management
- Report generation

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **File Storage**: AWS S3 / Local Storage
- **Email Service**: SMTP / SendGrid
- **Task Queue**: Celery with Redis
- **API Documentation**: Swagger UI (Auto-generated)
- **Testing**: Pytest
- **Containerization**: Docker
- **Environment Management**: Python-dotenv

## 📋 Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis (for caching and task queue)
- AWS S3 account (optional, for file storage)

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/job-portal-api.git
cd job-portal-api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost/job_portal_db

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_BUCKET_NAME=your-s3-bucket-name
AWS_REGION=us-east-1

# Application Settings
DEBUG=True
API_V1_STR=/api/v1
PROJECT_NAME=Job Portal API
```

### 5. Database Setup
```bash
# Create database
createdb job_portal_db

# Run migrations
alembic upgrade head
```

### 6. Start the application
```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🐳 Docker Setup

### Using Docker Compose
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build image
docker build -t job-portal-api .

# Run container
docker run -p 8000:8000 --env-file .env job-portal-api
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Reset password

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `POST /api/v1/users/upload-resume` - Upload resume
- `GET /api/v1/users/{user_id}` - Get user by ID

### Jobs
- `GET /api/v1/jobs/` - List all jobs (with filters)
- `GET /api/v1/jobs/{job_id}` - Get job details
- `POST /api/v1/jobs/` - Create new job (employers only)
- `PUT /api/v1/jobs/{job_id}` - Update job
- `DELETE /api/v1/jobs/{job_id}` - Delete job
- `GET /api/v1/jobs/search` - Advanced job search

### Applications
- `POST /api/v1/applications/` - Apply for a job
- `GET /api/v1/applications/` - Get user applications
- `GET /api/v1/applications/{app_id}` - Get application details
- `PUT /api/v1/applications/{app_id}` - Update application status
- `DELETE /api/v1/applications/{app_id}` - Withdraw application

### Companies
- `GET /api/v1/companies/` - List companies
- `GET /api/v1/companies/{company_id}` - Get company details
- `POST /api/v1/companies/` - Create company profile
- `PUT /api/v1/companies/{company_id}` - Update company
- `GET /api/v1/companies/{company_id}/jobs` - Get company jobs

### Bookmarks
- `POST /api/v1/bookmarks/` - Bookmark a job
- `GET /api/v1/bookmarks/` - Get bookmarked jobs
- `DELETE /api/v1/bookmarks/{job_id}` - Remove bookmark

## 🗂️ Project Structure

```
job-portal-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── security.py        # JWT and password hashing
│   │   └── dependencies.py    # Common dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User model
│   │   ├── job.py            # Job model
│   │   ├── company.py        # Company model
│   │   ├── application.py    # Application model
│   │   └── bookmark.py       # Bookmark model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py           # User Pydantic schemas
│   │   ├── job.py            # Job schemas
│   │   ├── company.py        # Company schemas
│   │   └── application.py    # Application schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py       # Authentication routes
│   │   │   ├── users.py      # User routes
│   │   │   ├── jobs.py       # Job routes
│   │   │   ├── companies.py  # Company routes
│   │   │   ├── applications.py # Application routes
│   │   │   └── bookmarks.py  # Bookmark routes
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py           # Base CRUD operations
│   │   ├── user.py           # User CRUD
│   │   ├── job.py            # Job CRUD
│   │   └── company.py        # Company CRUD
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py           # Database base
│   │   └── session.py        # Database session
│   └── utils/
│       ├── __init__.py
│       ├── email.py          # Email utilities
│       ├── file_handler.py   # File upload utilities
│       └── helpers.py        # Helper functions
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testing

Run tests using pytest:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run tests in verbose mode
pytest -v
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in environment variables
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper database connection
- [ ] Set up SSL certificates
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Deploy with Docker
```bash
# Build production image
docker build -t job-portal-api:prod -f Dockerfile.prod .

# Run with production settings
docker run -d -p 80:8000 --env-file .env.prod job-portal-api:prod
```

### Deploy to Cloud Platforms
- **AWS**: Use ECS, EKS, or Elastic Beanstalk
- **Google Cloud**: Use Cloud Run or GKE
- **Azure**: Use Container Instances or AKS
- **Heroku**: Use container deployment

## 📊 Monitoring and Logging

### Health Check Endpoint
```bash
GET /health
```

### Logging
The application uses Python's built-in logging module. Logs are structured and include:
- Request/Response logs
- Error tracking
- Performance metrics
- Security events

### Monitoring Tools
- **Application Performance**: New Relic, DataDog
- **Error Tracking**: Sentry
- **Infrastructure**: Prometheus + Grafana
- **Uptime**: UptimeRobot, Pingdom

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `SMTP_HOST` | Email SMTP host | `localhost` |
| `SMTP_PORT` | Email SMTP port | `587` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `MAX_FILE_SIZE` | Max upload file size (MB) | `10` |

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation
- Use meaningful commit messages
- Add docstrings to functions and classes

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify database exists
psql -l | grep job_portal
```

**Permission Errors**
```bash
# Fix file permissions
chmod +x scripts/start.sh

# Check user permissions for uploads directory
ls -la uploads/
```

**Memory Issues**
- Increase Docker memory limits
- Optimize database queries
- Use database connection pooling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: Check the `/docs` endpoint
- **Issues**: Create an issue on GitHub
- **Email**: support@jobportal.com
- **Discord**: Join our Discord server

## 🔄 Changelog

### v1.0.0
- Initial release
- Basic CRUD operations
- JWT authentication
- File upload functionality
- Email notifications
- Docker support

### v1.1.0
- Advanced search filters
- Bulk operations
- Performance improvements
- Additional test coverage
- API rate limiting

---

**Happy Coding! 🚀**
