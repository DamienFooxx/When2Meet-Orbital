# Accounts API Endpoints

### Profile information
- `CheckUserByEmail.get` (`GET /accounts/check-user/`)
    Checks if a user exists by email. 
    - **Requires:** authentication
    - **Body:** Query param: `email`.
    - **Returns:** 
    ```
    { 
        exists: true/false, 
        error? 
    }
    ```

- `GoogleLogin` (`POST /accounts/google/login/`)
    Handles Google OAuth login. Used for authenticating users via Google. 
    - **Requires:** OAuth credentials.
    - **Returns:** Auth token and user info on success.

- `ProfileView.get` (`GET /accounts/profile/`)
    Gets the authenticated user's profile info. 
    - **Requires:** authentication.
    - **Returns:** 
    ```
    { 
        unique_id, 
        username, 
        email, 
        name, 
        location
    }
    ```

- `ProfileView.put` (`PUT /accounts/profile/`)
    Updates the authenticated user's profile info. 
    - **Requires:** authentication. 
    - **Body:** `{ name, location }` (optional fields).
    - **Returns:** Updated profile info with 
    ```
    {
        name, 
        location, 
        unique_id
    }
    ```

### Calendar Sync information
- `GoogleCalendarFreeBusyView.post` (`POST /accounts/google/freebusy/`)
    Fetches busy slots from the user's Google Calendar. 
    - **Requires:** authentication and Google account connection. 
    - **Body:** `{ start, end }` (ISO 8601).
    - **Returns:** `{ busy: [ {start, end}, ... ] }` (busy time slots, dictionary of start end times)
