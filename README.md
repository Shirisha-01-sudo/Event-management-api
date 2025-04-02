# Event Management API

A scalable and feature-rich API for managing events and attendees built with FastAPI and SQLite.

## Features

- Complete event lifecycle management (create, update, list, delete)
- Attendee registration and check-in functionality
- Event status management
- CSV upload for bulk attendee registration
- JWT authentication for secure access
- Asynchronous database operations
- Comprehensive error handling
- Pagination and filtering support

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **SQLite**: Lightweight database
- **JWT**: JSON Web Tokens for authentication
- **Uvicorn**: ASGI server
- **Pandas**: For CSV processing

## Project Structure

```
event-management-api/
├── .env                     # Environment variables
├── .venv/                   # Virtual environment
├── app/                     # Application package
│   ├── api/                 # API routes
│   │   ├── routers/         # Router modules
│   │   └── api.py           # API router aggregation
│   ├── core/                # Core application config
│   ├── db/                  # Database setup
│   ├── middleware/          # Middleware components
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   └── main.py              # Application entry point
├── requirements.txt         # Dependencies
├── server.py                # Server startup script
└── README.md                # Documentation
```

## Setup and Installation

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/event-management-api.git
   cd event-management-api
   ```

2. **Create and activate a virtual environment**:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   create a `.env` file in root with your settings given in env.example

5. **Run the application**:
   ```
   python server.py
   ```

   The API will be available at `http://localhost:8000`

6. **Access the documentation**:
   Visit `http://localhost:8000/docs` for the Swagger UI documentation

## API Endpoints

### Events

- `POST /events`: Create a new event
- `GET /events`: List events with optional filters
- `GET /events/{event_id}`: Get event details
- `PUT /events/{event_id}`: Update an event
- `DELETE /events/{event_id}`: Delete an event

### Attendees

- `POST /attendees`: Register a new attendee
- `GET /attendees/event/{event_id}`: List attendees for an event
- `GET /attendees/{attendee_id}`: Get attendee details
- `PUT /attendees/{attendee_id}`: Update an attendee
- `DELETE /attendees/{attendee_id}`: Delete an attendee
- `POST /attendees/{attendee_id}/check-in`: Check in an attendee
- `POST /attendees/event/{event_id}/check-in-bulk`: Bulk check-in attendees
- `POST /attendees/event/{event_id}/upload-csv`: Upload CSV for bulk registration
- `POST /attendees/event/{event_id}/bulk-create`: Bulk create attendees

### Users & Authentication

- `POST /users`: Register a new user
- `POST /users/login`: Login to get access token
- `GET /users/me`: Get current user details
- `PUT /users/me`: Update current user

## Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. Register a user: `POST /users`
2. Login to get token: `POST /users/login`
3. Include the token in requests: `Authorization: Bearer YOUR_TOKEN`

## License

[MIT License](LICENSE)

## Contact

For questions or support, please open an issue in the repository.