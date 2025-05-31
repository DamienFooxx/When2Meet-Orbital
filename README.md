# When2Meet setup Guide
when2meet aims to make group hang outs easier by integrating google calendar syncs, auto scheduling and smart polls/locations

# Table of Contents
- [Initial Setup](#initial-setup)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Events](#events)
  - [Time Slots](#time-slots)
- [Frontend Integration](#frontend-integration)

## Initial Setup

1. **Clone the Repository**
```bash
git clone "github url"
cd When2Meet-Orbital
```

2. **Create and Activate Virtual Environment**
```bash
# For macOS/Linux
python -m venv w2w
source w2w/bin/activate

# For Windows
python -m venv w2w
.\w2w\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

copy .env.example to a new .env

5. **Configure Database**
Set up a local postgreSQL database.
**for macOS**
```bash
brew install postgresql
brew services start postgresql
```
**for Windows**

download and run the PostgreSQL installer

The pyscopg2-binary shouldve been downloaded already in step 3 when installing dependencies

## Setting up DB
Open the postgresql interactive shell using
```bash
psql postgres
```
Then follow the postgreSQL_setupDB.sql script, inserting line by line

6. **Apply Database Migrations**
```bash
python manage.py migrate
```

7. **Run the Development Server**
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`
Navigate to the website using the url.
It should say "When2Meet Backend is running!.

## API Documentation

### Authentication

All authenticated endpoints require the header: `Authorization: Token your-auth-token`.

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
- **Response**: Returns a success message if registration is successful.

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
- **Response**: Returns a success message if logout is successful.

### Frontend Integration

To use these API endpoints in your React Native application, you can use the `fetch` API or a library like `axios`. Here's an example using `fetch`:

```javascript
// Example: Login API call
const login = async (email, password) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (response.ok) {
      // Store the token securely (e.g., using AsyncStorage)
      console.log('Login successful:', data);
    } else {
      console.error('Login failed:', data);
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Notes
- Ensure you handle errors gracefully and store the authentication token securely.
- Replace `http://127.0.0.1:8000` with your actual API base URL in production.

## License

This project is licensed under the GNUn General Public License v3.0 License - see the LICENSE file for details 