# When2Meet Frontend

This is the React Native frontend for When2Meet mobile app, built with TypeScript

-- 

## Tech Stack
- [React Native](https://reactnative.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [React Navigation](https://reactnavigation.org/)
- [Axios](https://axios-http.com/)
- [Google Sign-In](https://github.com/react-native-google-signin/google-signin)
- [AsyncStorage](https://react-native-async-storage.github.io/async-storage/)

## Initial Setup
1. **Clone the Repository**
```bash
git clone https://github.com/DamienFooxx/When2Meet-Orbital.git
cd When2Meet-Orbital
```

2. **Install Dependencies**
```bash
npm install
```

3. **Set Up Environment Variables**
Create a `.env` file in the root of the frontend folder or configure your `config.js` to define your backend base URL:
```ts
// utils/config.js
export const BASE_URL = 'http://<YOUR_BACKEND_IP>:8000';
```

4. **Start the Metro Bundler**
```bash
npx react-native start
```

5. **Run on iOS**
```bash
npx react-native run-ios
```

# When2Meet Backend

A Django-based backend for the When2Meet clone application, providing REST APIs for event scheduling and time slot management.

## Table of Contents
- [Initial Setup](#initial-setup)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Events](#events)
  - [Time Slots](#time-slots)
- [Frontend Integration](#frontend-integration)
- [Development Tools](#development-tools)
- [Troubleshooting](#troubleshooting)

## Initial Setup

1. **Clone the Repository**
```bash
git clone https://github.com/DamienFooxx/When2Meet-Orbital.git
cd When2Meet-Orbital
```

2. **Create and Activate Virtual Environment**
```bash
# For macOS/Linux
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply Database Migrations**
```bash
cd when2meet_backend
python manage.py migrate
```

5. **Create a Superuser (Admin Account)**
```bash
python manage.py createsuperuser
```

6. **Run the Development Server**
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`

## API Documentation

### Authentication

All authenticated endpoints require the header: `Authorization: Token your-auth-token`

#### Register
- **Endpoint**: `POST /api/auth/registration/`
- **Body**:
```json
{
  "email": "user@example.com",
  "password1": "your_password",
  "password2": "your_password"
}
```

#### Login
- **Endpoint**: `POST /api/auth/login/`
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```
- **Response**:
```json
{
  "key": "your-auth-token"
}
```

#### Logout
- **Endpoint**: `POST /api/auth/logout/`
- **Requires**: Authentication

### Events

#### List/Create Events
- **Endpoint**: `GET/POST /api/events/`
- **Requires**: Authentication
- **POST Body**:
```json
{
  "title": "Team Meeting",
  "description": "Weekly sync",
  "start_date": "2024-05-10T09:00:00Z",
  "end_date": "2024-05-10T10:00:00Z"
}
```

#### Get/Update/Delete Event
- **Endpoint**: `GET/PUT/DELETE /api/events/{id}/`
- **Requires**: Authentication

#### Join Event
- **Endpoint**: `POST /api/events/{id}/join/`
- **Requires**: Authentication

#### Leave Event
- **Endpoint**: `POST /api/events/{id}/leave/`
- **Requires**: Authentication

### Time Slots

#### List/Create TimeSlots
- **Endpoint**: `GET/POST /api/timeslots/`
- **Requires**: Authentication
- **POST Body**:
```json
{
  "event": 1,
  "start_time": "2024-05-10T09:00:00Z",
  "end_time": "2024-05-10T10:00:00Z",
  "is_available": true
}
```

#### Get/Update/Delete TimeSlot
- **Endpoint**: `GET/PUT/DELETE /api/timeslots/{id}/`
- **Requires**: Authentication

## Frontend Integration

### Example Flutter API Service

```dart
class ApiService {
  final String baseUrl = 'http://127.0.0.1:8000/api';
  String? token;

  // Login
  Future<void> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      body: {
        'email': email,
        'password': password,
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      token = data['key'];
    }
  }

  // Get Events
  Future<List<Event>> getEvents() async {
    final response = await http.get(
      Uri.parse('$baseUrl/events/'),
      headers: {'Authorization': 'Token $token'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Event.fromJson(json)).toList();
    }
    throw Exception('Failed to load events');
  }

  // Create Event
  Future<Event> createEvent(String title, String description, 
                          DateTime startDate, DateTime endDate) async {
    final response = await http.post(
      Uri.parse('$baseUrl/events/'),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'title': title,
        'description': description,
        'start_date': startDate.toIso8601String(),
        'end_date': endDate.toIso8601String(),
      }),
    );

    if (response.statusCode == 201) {
      return Event.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to create event');
  }
}
```

## Development Tools

### Admin Interface
- Access at `http://127.0.0.1:8000/admin/`
- Use superuser credentials to log in
- Useful for managing data directly

### API Response Formats
- All endpoints return JSON
- Standard HTTP status codes:
  - 200: OK
  - 201: Created
  - 400: Bad Request
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Not Found

## Troubleshooting

### Common Issues

1. **CORS Issues**
   - The backend accepts requests from any origin during development
   - For production, specify allowed origins in settings

2. **Authentication Issues**
   - Include token in all authenticated requests
   - Token format: `Authorization: Token your-auth-token`
   - Check token expiration

3. **DateTime Format**
   - Use ISO 8601 format: `YYYY-MM-DDTHH:mm:ssZ`
   - Django handles timezone conversions

### Database Reset
If you need to reset the database:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details 
