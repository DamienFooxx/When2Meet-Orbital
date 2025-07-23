# When2Meet
## Level of Achievement: Artemis
## Project Scope: Creating a mobile application for groups to easily find a time and place to meet.
## Detailed Scope
The When2Meet project aims to deliver a full-stack, production-level mobile application that simplifies the process of scheduling group meetups by leveraging real-time availability data, smart scheduling algorithms, calendar integrations, and event management tools. The application targets users with varying degrees of tech-savviness and scheduling habits, providing both automated and manual options to facilitate seamless coordination across friend groups, professional teams, and social communities.

The app positions itself as a Smart Meet-Up Scheduler capable of both understanding user availability and recommending the most optimal time and place to meet, thereby reducing the cognitive and logistical burden typically associated with group planning.

## Table of Contents
- [Motivation](#motivation)
- [Aim](#aim)
- [User Stories](#user-stories)
- [Features](#features)
- [Project Timeline](#project-timeline)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [How to Setup](#how-to-setup)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Software Engineering Principles](#software-engineering-principles)
- [Notes](#notes)
- [License](#license)

### Motivation
People find it very difficult to find a consensus on when to meet because of conflicting schedules. In addition, discussing when to meet can cause very long chats which may result in an unclear decision on where and when to meet. Moreover, people may easily forget about arrangements made with the group because of it being in text form and making it hard to remember and find chats about the event.

### Aim
We hope to create an app that makes scheduling meet-ups between multiple groups more convenient and hassle-free. The app serves as a Smart MeetUp Scheduler that finds a time convenient for all if not most users to meet-up.

## User Stories
1. As a friend who wants to catch up with their friend group who may not be doing the same things together anymore (i.e. going school together or working in the same company), I want to be able to easily find a time for the friend group to meet up without me having to spend so much effort on my side to coordinate.
2. I just want to be able to upload my calendar and schedule to an app and it will automatically find a timeslot where everyone is free. Even if my friends do not record their schedules on a calendar they can still fill out when they are free.
3. Even when there isn't a timeslot where everyone is free, the system will automatically rank timeslots where the most amount of people are free.
4. The system will automatically create an event where people can add it to their individual calendars. It will also send a notification closer to the date of the event.
5. The system can also suggest potential spots to meet up to eat or do activities.
6. The system could also book the restaurant or place for the group as well.

## Features

### Feature 1: Create a group
- Users can create custom groups for recurring meet-ups or one-time planning
- Users can create a named group
- Users can be categorised as Organiser with administrative rights for the group (e.g. adding people, creating events)
- Users can be categories as Participants with only viewing rights
- Members are added via username search, with validation to ensure users exist
- Users can join groups using the unique group code
- Users can join groups via a link
- Groups can be edited (rename, remove/add users, assigning of roles)
- Group data is saved for easy access to prior meet-ups and schedules

### Feature 2: Sync Google Calendar
- Enable users to integrate their Google account to streamline scheduling
- Upon login, users are prompted to grant permission to access their Google Calendar
- The app reads busy slots and avoids them in scheduling logic
- Synced events from this app are pushed back to the user's Google Calendar with full details (title, time, location)

### Feature 3: Smart Meet-Up Scheduling
- Simplify planning by letting the app handle availability logic
- The host chooses:
  - Date range
  - Preferred meeting duration
  - Location type: face-to-face or online
- The app fetches availability for all group members via:
  - Synced Google Calendar data
  - In-app manually blocked times (if calendar not linked)
- The app finds optimal time slots with full or partial overlap

### Feature 4: Polling System
- Scheduling when a perfect overlap is not possible:
  - Case 1 - No full overlap: App suggests top time slots with majority availability. Users vote for their preference
  - Case 2 - Multiple perfect overlaps: Users vote on preferred time based on convenience
- Polls are time-limited; the host can choose auto-close or manual close
- Results are summarized for easy confirmation

### Feature 5: Event Creation + Set Reminder
- Finalize meetings and notify participants proactively
- The host creates the official event once a time slot is confirmed (via auto-pick or poll result)
- All participants:
  - Receive a push notification/email
  - Have the event added to their calendar (if synced)
  - Optionally, users can configure reminder frequency: 1 hour before, 1 day before, etc.

### Feature 6: Venue Booking Links
- Integrate with external reservation systems for real-world meetups
- Once a face-to-face location is selected, the app suggests platforms like:
  - Chope, OpenTable, Google Maps reservation
- The host can open the link directly to book a table or room
- The booking link is stored in the event description for future reference

### Feature 7: Location Suggestions
- Suggest convenient meeting spots based on participants' locations and meeting type
- The host selects a vibe:
  - Business (cafes, meeting rooms)
  - Chill (parks)
  - Dining (restaurants, food courts)
- The app:
  - Geolocates all participants (or accepts ZIP codes if privacy preferred)
  - Calculates a central meeting point
  - Suggests locations via Google Places API
  - Displays options sorted by travel time

## Timeline

### Lift Off — Technical Proof of Concept
**Target Date: 15 May 2025**
#### Scope
- Basic Integration: Set up the frontend (React Native) and backend (Django) so data can flow end-to-end
- Allow users to sign up and login
- Create a database (SQL) to store user data

#### Deliverables
- A functioning prototype where a user can sign up using their email account
- Minimal UI/UX for input and confirmation
- Demonstration of a functional, integrated system (frontend + backend + database)

#### Outcome
- Users can sign up for the app and login

### Milestone 1 — Proof of Concept with more Features
**Target Date: 2 June 2025**
#### Scope
**Feature 1 (Core) Creating Group:**
- Users can create their own profiles and sign in using Google Social account
- Being able to send invite links to people to sign up for the app or login and join the group created by the host
- Groups are permanent
- Users can join using a group code

**Feature 2 (Core) Sync Google Calendar:**
- Users can sign in using their Google Accounts and sync their Google Calendars with the app
- The app can access the users live Google Calendar Data on demand
- The app can read which time slots the users are free

#### Deliverables
- Working prototype run locally with:
  - User sign in using Google Social Account
  - Basic Group Management features

#### Outcome
- An interactable user interface that testers can interact with
- Able to join and create groups

### Milestone 2 – Prototype
**Target Date: 30 June 2025**
#### Scope
**Feature 3 (Core) Smart Meetup Scheduling:**
- The app can automatically match the free time slots for all users in the group and find a common free time slot
- The app can filter out time slots that are too short based on the demands of the host
- Users without google calendar can manually block out dates in the app

**Feature 4 (Core) Polling System:**
- Allow users to vote which time slot they prefer
- The app can rank time slots based on the number of people available for that time slot

#### Deliverables
- Working Prototype with robust scheduling logic:
  - Group Creation
  - Priority attendees
  - Google Calendar sync
  - Automated poll creation
  - Basic acceptance testing
  - Group members can accept time slots or reject time slots
  - Improved UI/UX so participants can see suggested times, cast votes, and confirm the final timeslot

#### Outcome
- A feature-complete scheduling engine covering most core features
- Users can realistically organize a meetup with minimal friction, progressing from input to confirmed timeslot in one flow

### Milestone 3 — Extended System
**Target Date: 28 July 2025**
#### Scope
**Feature 5 (Core) Event Creation + Set Reminder:**
- Automatic notifications or emails sent to all participants once a final slot is chosen
- "Are you still coming?" confirmations leading up to the event
- Auto-add the event to synced calendars (for Google-linked users) with date, time, location, and participant info

**Feature 6 (Extension) Venue Booking Links:**
- Participants can book venues directly through the app
- Done via a hyperlink to various booking websites like OpenTable
- Use an in app browser

**Feature 7 (Extension) Location Suggestions:**
- The app can check where group members are coming from and choose a venue that is convenient for all group members
- The app can check via Google Maps what venue to recommend based on the vibe that the host is going for

#### Deliverables
- An extended system combining advanced notifications, user-friendly reminders, and location suggestions and booking
- Polished UI/UX, with improved reliability and error handling
- Basic performance checks for moderate-scale usage (e.g., multiple events, bigger participant groups)

#### Outcome
- A complete app capable of coordinating both the time and place of meetups, offering a smooth experience for all participants
- Sufficient maturity for final Splashdown or demonstration

## Summary
- **Lift off 1 (14 May 2025)**: Minimal proof-of-concept with sign in
- **Milestone 1 (2 June 2025)**: Completed Feature 1 and established base for future features
- **Milestone 2 (30 June 2025)**: Completed Feature 2, 3 and 4 forming a solid core prototype
- **Milestone 3 (28 July 2025)**: Completed Feature 5, 6, 7 for a more value adding experience

## Software Engineering Principles & Workflow

### Architecture & Design
#### Layered/MVC Structure
- **Backend (Django)**: We keep logic clean by separating models, views, and service logic (e.g., user features and group features are in separate apps)
- **Frontend (React Native)**: Components are modular and each one has a single, clear responsibility

#### UML & Diagrams
- **Use Case Diagrams**: Map out how users interact with features like group creation, scheduling, and external APIs (Google Calendar/Maps)
- **Class/ER Diagrams**: Visualise the database schema—users, events, availability slots, groups, etc
- **Sequence Diagrams**: Used for flows like scheduling logic, polls, or reminder notifications

#### Design Patterns
- **Singleton/Dependency Injection**: Shared services (e.g., notification sender) are written so there's a single source of truth
- **Observer/Publish-Subscribe**: Real-time update features (like reminders or voting updates) use publish-subscribe style logic where possible

### Code Quality & Version Control
#### Branching Strategy
- Each new feature is developed in its own branch, named for its purpose (e.g., feature/google-calendar-sync)
- All feature branches are merged into a dev branch after thorough testing
- The dev branch is only merged into main after all tests pass and code reviews are completed
- This ensures stability and allows parallel development

#### Pull Requests & Code Review
- Every merge to dev or main goes through a pull request and is reviewed by at least one team member

#### Coding Standards
- We follow PEP 8 for Python code readability
- Short functions, clear variable names, and good commenting are enforced

### Continuous Integration (CI)
#### Automated Testing
- GitHub Actions is set up to run unit and integration tests on every pull request
- Static analysis tools are run automatically to catch code issues early

### Testing Strategy
#### Unit Testing
- Core modules (e.g., scheduling, poll logic, reminders) have unit tests using written test cases
- Tests are using Django in built test functions
- External APIs (Google Calendar/Maps) are mocked for reliable tests

#### Integration Testing
- End-to-end checks of critical flows, like submitting availability and confirming an event

#### User Acceptance Testing
- Peers use the app in realistic scenarios; feedback is used to refine features

### Project Management
#### Agile-Lite Approach
- Work is split into two-week sprints
- Progress is tracked with GitHub Projects using issues, tasks, milestones, and labels

#### Regular Check-ins
- Team syncs weekly to track progress and re-assign tasks if needed

### Documentation & Knowledge Sharing
#### ReadMe and Docs
- The project ReadMe documents key architecture, API endpoints, setup, and important design decisions

### Security & Data Protection
#### Authentication
- Django handles user logins; role checks restrict sensitive actions
- OAuth 2.0: Google Calendar integration uses secure OAuth flows and only the minimum required permissions

#### Data Safety
- No sensitive information is committed to the repo (e.g., secrets in .env files)
- Passwords are hashed

#### HTTPS
- For production deployment, all traffic will be encrypted


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


 ## Contact Emails

 If you are a peer team evaluating this project and require read-only access to clone the repository, please email us your GitHub username so we can add you as a viewer.

Damien Foo: damienfoo@u.nus.edu

Joanne Koe: e1355447@u.nus.edu

Once added, you will be able to clone the private repository and test the app according to the setup instructions above.

## How to Setup

### Backend Setup
1. **Clone the Repository**
   ```bash
   git clone https://github.com/DamienFooxx/When2Meet-Orbital.git
   cd When2Meet-Orbital
   ```
2. **Create and Activate Virtual Environment**
   ```bash
   # For macOS/Linux
   python -m venv w2m
   source w2m/bin/activate
   # For Windows
   python -m venv w2m
   .\w2m\Scripts\activate
   ```
3. **Install Backend Dependencies**
   ```bash
   cd "Django Code Base"
   pip install -r requirements.txt
   cd ..
   ```
4. **Set Up Environment Variables**
   - Copy `.env.example` to `.env` in the Django Code Base directory and update as needed.
5. **Set Up PostgreSQL Database**
   - Install PostgreSQL and follow the provided SQL setup script.
6. **Apply Migrations**
   ```bash
   cd "Django Code Base"
   python manage.py makemigrations
   python manage.py migrate
   cd ..
   ```
7. **Run the Backend Server**
   ```bash
   cd "Django Code Base"
   python manage.py runserver 0.0.0.0:8000
   cd ..
   ```

### Frontend Setup
1. **Install Node.js and npm**
   - Make sure you have Node.js (v14 or higher) and npm installed. Check with `node -v` and `npm -v`.
2. **Install Frontend Dependencies**
   ```bash
   cd Frontend
   npm install
   ```
3. **Set Up iOS Environment (for Mac/iOS only)**
   - Install Ruby and rbenv if not already installed:
     ```bash
     brew install rbenv
     rbenv init
     rbenv install 3.4.4
     gem install bundler -v 2.6.9
     gem install cocoapods
     ```
   - Install CocoaPods dependencies:
     ```bash
     cd ios
     pod install
     cd ..
     ```
4. **Configure API Base URL**
   - Edit `Frontend/src/utils/config.js` and set `API_BASE` to your backend server's IP address, e.g.:
     ```js
     export const API_BASE = "http://<your-ip>:8000/api";
     ```
5. **Start Metro Bundler**
   ```bash
   npx react-native start
   ```
6. **Run the App on iOS Simulator**
   ```bash
   cd ios
   pod install
   cd ..
   npx react-native run-ios
   ```

---

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

### Node.js Not Found or Wrong Version
- **Error:** `/Users/Joanne/.nvm/versions/node/v18.20.8/bin/node: No such file or directory`
- **Cause:** The iOS build is trying to use a Node.js path from another developer's machine.
- **Solution:**
  1. On your own machine, run:
     ```sh
     which node
     ```
  2. Create or edit the file `Frontend/ios/.xcode.env.local` and add:
     ```sh
     export NODE_BINARY=/path/to/your/node
     ```
     (Replace with the output from `which node`.)
  3. Clean and rebuild:
     ```sh
     cd ios
     xcodebuild clean
     cd ..
     npx react-native run-ios
     ```
- **Note:** Each developer must set their own Node path in `.xcode.env.local` to match their system. Do not use a hardcoded path from another machine.

### iOS Build: CLEAN FAILED
- **Error:** `Could not delete .../ios/build because it was not created by the build system.`
- **Solution:**
  - Manually delete the build directory:
    ```sh
    rm -rf ./Frontend/ios/build
    ```
  - Then try cleaning and rebuilding again.

### CocoaPods or Ruby/Bundler Issues
- **Error:** `cannot load such file -- cocoapods (LoadError)` or `Could not find cocoapods-1.15.2 ... in locally installed gems (Bundler::GemNotFound)`
- **Solution:**
  - Make sure you are using the correct Ruby version (check with `rbenv versions` and `rbenv global 3.4.4`).
  - Install CocoaPods and Bundler:
    ```sh
    gem install bundler -v 2.6.9
    gem install cocoapods
    ```
  - If you have a `Gemfile`, run `bundle install` in the `ios` directory.
  - Then run `pod install` in the `ios` directory.

### Metro Bundler Fails to Start
- **Solution:**
  - Make sure you are in the `Frontend` directory and all dependencies are installed (`npm install`).
  - Try restarting Metro with `npx react-native start --reset-cache`.

### API/Network Issues
- **Error:** `Network error` or `Request failed with status code 500/404`
- **Solution:**
  - Make sure your backend server is running and accessible from your device/simulator.
  - Double-check the `API_BASE` in `config.js` matches your backend IP and port.
  - Ensure your device/simulator is on the same network as your backend.
---
## Notes
- Ensure you handle errors gracefully and store the authentication token securely.
- Replace `http://127.0.0.1:8000` with your actual API base URL in production.

## License
This project is licensed under the GNUn General Public License v3.0 License - see the LICENSE file for details