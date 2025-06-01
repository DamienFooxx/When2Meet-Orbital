# When2Meet setup guide
when2meet aims to make group hang outs easier by integrating google calendar syncs, auto scheduling and smart polls/locations

# Table of Contents
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [How to Setup](#how-to-setup)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Notes](#notes)
- [License](#license)
--- 

## Tech Stack
**Frontend**
This is the React Native frontend for When2Meet mobile app, built with TypeScript
- [React Native](https://reactnative.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [React Navigation](https://reactnavigation.org/)
- [Axios](https://axios-http.com/)
- [Google Sign-In](https://github.com/react-native-google-signin/google-signin)
- [AsyncStorage](https://react-native-async-storage.github.io/async-storage/)

**Backend**
This is the Django backend for When2Meet mobile app.
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [psycopg2](https://pypi.org/project/psycopg2/)
- [django-allauth](https://django-allauth.readthedocs.io/en/latest/)
- [dj-rest-auth](https://dj-rest-auth.readthedocs.io/en/latest/)
- [Google OAuth2](https://developers.google.com/identity/protocols/oauth2)

## Prerequisites

Before you begin setting up the When2Meet application, ensure you have the following prerequisites installed and configured:

### Required Software
- **Python**: Version 3.8 or higher. You can download it from [python.org](https://www.python.org/downloads/).
- **Django**: Version 3.2 or higher. You can install it using pip: `pip install django`.
- **Node.js**: Version 14 or higher. You can download it from [nodejs.org](https://nodejs.org/).
- **npm**: Usually comes with Node.js. You can check your version by running `npm -v`.
- **PostgreSQL**: Version 12 or higher. You can download it from [postgresql.org](https://www.postgresql.org/download/).
- **Git**: For version control. You can download it from [git-scm.com](https://git-scm.com/downloads).

### Development Tools
- **Code Editor**: A code editor like [Visual Studio Code](https://code.visualstudio.com/).

### Additional Tools
- **Metro Bundler**: Required for running the React Native application. It comes with React Native, but ensure it's installed and configured correctly.

Please ensure that you have fulfilled the prequisites for testing this application.

## How to Setup
### Step 1. Clone the Repository
```bash
git clone https://github.com/DamienFooxx/When2Meet-Orbital.git
# Navigate to the When2Meet-Orbital directory
cd When2Meet-Orbital
```

### Step 2. Create and Activate Virtual Environment
```bash
# For macOS/Linux
python -m venv w2w
source w2w/bin/activate

# For Windows
python -m venv w2w
.\w2w\Scripts\activate
```

### Step 3. Install Dependencies
```bash
# Install dependencies for backend
cd ./Django\ Code\ Base/
pip install -r requirements.txt
# Move to frontend directory
cd ..
cd when2meet_frontend 
# Install dependencies for frontend
npm install 
```

### Step 4. Set Up Environment Variables
Create a `.env` file in the root of the frontend folder or configure your `config.js` to define your backend base URL:
These are for the frontend.
```ts
// While in when2meet_frontend directory
// utils/config.js
export const BASE_URL = 'http://127.0.0.1:8000/';
```
**Navigate to Django Code Base Directory**
Rename ".env.example" file to just ".env"

### Step 5. Install Database
Set up a local postgreSQL database.
**for macOS**
```bash
# If not already installed
brew install postgresql
# After installation
brew services start postgresql
```
**for Windows**
download and run the PostgreSQL installer

The pyscopg2-binary shouldve been downloaded already in step 3 when installing dependencies

### Step 6. Setting up DB
Open the postgresql interactive shell using
```bash
psql postgres
```
Then follow the postgreSQL_setupDB.sql script, inserting line by line
```bash
CREATE DATABASE when2meet;
CREATE USER admin WITH PASSWORD 'orbital2425';
ALTER ROLE admin SET client_encoding TO 'utf8;
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin SET timezone TO 'ASIA/SINGAPORE';
GRANT ALL PRIVILEGES ON DATABASE when2meet TO admin;
ALTER DATABASE when2meet OWNER TO admin;
-- type \l to check if the database is setup correctly
```

### Step 7. Apply Database Migrations
In the Django Code Base directory, input this into the terminal
```bash
python manage.py migrate
```

### Step 8. Run the Development Server
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`
Navigate to the website using the url.
It should say "When2Meet Backend is running!.

### Step 9. Start the Metro Bundler
```bash
npx react-native start
```

### Step 10. **Run on iOS**
```bash
npx react-native run-ios
```
## Troubleshooting Common Issues

### Database Connection Issues
- **Error**: Unable to connect to PostgreSQL.
    - **Solution**: Ensure PostgreSQL is running. On macOS, use `brew services start postgresql`. On Windows, check the PostgreSQL service in the Services app.

### Migration Errors
- **Error**: `No migrations to apply` or `django.db.utils.OperationalError`.
    - **Solution**: Ensure you are in the correct directory (`Django Code Base`) and that your virtual environment is activated. Run `python manage.py migrate` again.

### Environment Variables
- **Error**: Missing environment variables.
    - **Solution**: Ensure you have created a `.env` file in the root of the frontend folder and the `Django Code Base` directory, and that it contains the necessary variables.

### Frontend Build Issues
- **Error**: Metro Bundler fails to start.
    - **Solution**: Ensure you are in the `when2meet_frontend` directory and that all dependencies are installed. Run `npm install` again if necessary.

### API Endpoint Issues
- **Error**: 404 Not Found when accessing API endpoints.
    - **Solution**: Check the URL patterns in your `urls.py` files to ensure they are correctly defined and included in the main URL configuration.

### Authentication Issues
- **Error**: Unable to authenticate with Google OAuth.
    - **Solution**: Ensure your Google OAuth credentials are correctly set up in the Google Cloud Console and that the redirect URIs are properly configured.

### General Issues
- **Error**: Any other unexpected errors.
    - **Solution**: Check the console output for error messages, ensure all dependencies are up to date, and consult the documentation for the specific libraries you are using.

## Notes
- Ensure you handle errors gracefully and store the authentication token securely.
- Replace `http://127.0.0.1:8000` with your actual API base URL in production.

## License
This project is licensed under the GNU General Public License - see the LICENSE file for details 

