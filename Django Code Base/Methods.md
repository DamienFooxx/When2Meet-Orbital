# Core CRUD Methods
All API Endpoints start with this url
https://when2meetimage-686579494898.asia-southeast1.run.app/

## Accounts API Endpoints

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

---
## Groups API Endpoints

### Group Management

- `GroupViewSet.create` (`POST /groups/`)
    Creates a new group. The `perform_create` hook is used to automatically make the requesting user the creator and an 'organiser'.
    - **Requires:** Authentication.
    - **Body:** `{ "name": "...", "description": "..." }`
    - **Returns:** 
    ```
    {
        "id": "...", 
        "name": "Group name", 
        "description": "Optional description",
        "created_at": "2025-06-20T10:00:00Z",
        "invite_code": "AbC123xy",
        "creator": { "user_id": "abc123", "name": "John Doe"},
        "members": [
            {
            "user_id": "abc123",
            "name": "John Doe",
            "role": "organiser",
            "joined_at": "2025-06-20T10:00:00Z"
            }, [...]
        ]
    }
    ```

- `GroupViewSet.list` (`GET /groups/`)
    Lists all available groups.
    - **Requires:** Authentication.
    - **Returns:** 
    ```
    {
        "id": "...", 
        "name": "Group name", 
        "description": "Optional description",
        "created_at": "2025-06-20T10:00:00Z",
        "invite_code": "AbC123xy",
        "creator": { "user_id": "abc123", "name": "John Doe"},
    }
    ```

- `GroupViewSet.retrieve` (`GET /groups/{id}/`)
    Retrieves the details of a specific group.
    - **Requires:** Authentication.
    - **Returns:** 
    ```
    {
        "id": "...", 
        "name": "Group name", 
        "description": "Optional description",
        "created_at": "2025-06-20T10:00:00Z",
        "invite_code": "AbC123xy",
        "creator": { "user_id": "abc123", "name": "John Doe"},
        "members": #List of members [
            {
            "user_id": "abc123",
            "name": "John Doe",
            "role": "organiser",
            "joined_at": "2025-06-20T10:00:00Z"
            }, [...]
        ]
    }
    ```

- `GroupViewSet.destroy` (`DELETE /groups/{id}/`)
    Deletes a group. The standard `destroy` method is overridden to check that the user is an organiser.
    - **Requires:** Authentication (user must be an organiser).
    - **Returns:** Status 204 (No Content) on success.

### Membership Management

- `list_members` (`GET /groups/{id}/members/`)
    Lists all members of a specific group, with organisers appearing first.
    - **Requires:** Authentication.
    - **Returns:** members in order of organisers first than alphabetically
    ```
    {
        "members": #List of members [ 
            {
            "user_id": "abc123",
            "name": "John Doe",
            "role": "organiser",
            "joined_at": "2025-06-20T10:00:00Z"
            }, 
            {...}
        ]
    }
    ```

- `leave_group` (`POST /groups/{id}/leave/`)
    Allows a user to leave a group.
    - **Requires:** Authentication.
    - **Body:** `{ "confirm_delete": true }` is required if the user is the last member, which will delete the group.
    - **Returns:**
    ```
    # If not a member
    {Not a member of the group}, returns HTTP 400 error
    
    # If last member
    {You are the last member of "Group name", Leaving the group will cause the group to be deleted. Confirm by sending {{"confirm_delete": true}} in your request. }
    After confirmation
    {Group "group name" deleted as you were the last member.}

    # If Organiser and last organiser
    {'You are the last organiser of the group. Assign another member as an organiser before leaving.'} returns HTTP 403 error

    # If normal
    {You have left the group}
    ```

### Invitations and Requests

- `invitations` (`GET /groups/invitations/`)
    Lists all pending group invitations for the authenticated user.
    - **Requires:** Authentication.
    - **Returns:**
    ```
    {
        "name": "Group name",
        "invite_code": "Invite code 
        "creator" : "Creator name"
    }
    ```

- `invite_users` (`POST /groups/{id}/invite/`)
    Invites one or more users to a group via their email address.
    - **Requires:** Authentication.
    - **Body:** `{ "identifier": "user@example.com" }` or `{ "identifiers": ["user1@example.com", "user2@example.com"] }`.
    - **Returns:** 
    ```
    # If no emails provided
    {
    "error": "No email(s) provided."
    }

    # If a list of members
    {
        "message": "2 invited, 1 already in group, 1 not found.",
        "invited": [
            "newuser1@example.com",
            "newuser2@example.com"
            ],
        "already_members": [
            "existinguser@example.com"
            ],
        "not_found": [
            "unknownuser@example.com"
            ]
    }
    ```

- `join_by_code` (`POST /groups/join-by-code/`)
    Allows a user to request to join a group using its invite code.
    - **Requires:** Authentication.
    - **Body:** First send `{ "invite_code": "..." }`. If confirmation is needed, resend with `{ "invite_code": "...", "confirm_join": true }`.
    - **Returns:** 
    ```
    # Missing invite code
    {"error": "Invite code is required."}

    # Invalid Code
    {"error": "Invalid invite code or Group does not exist."}

    # Already a member
    {"error": "Already a group member."}

    # Already sent request
    {'error': 'You have already sent a join request to this group. Please wait for the organizer to approve your request.'}

    # If group is already full
    {'error' : 'Group is full.'}

    # Confirmation message
    {
        "confirmation_needed": true,
        "group_name": "Study Buddies",
        "message": "Do you want to request to join the group \"Study Buddies\"?",
        "group_info": {
            "name": "Study Buddies",
            "invite_code": "AbC123xy"
            }
    }

    # After confirmation
    {
        "message": "Your request to join group \"Study Buddies\" has been sent to organizer.",
        "group_name": "Study Buddies"
    }
    ```

- `accept_request` (`POST /groups/{id}/accept-request/`)
    Allows a group organiser to accept a user's join request.
    - **Requires:** Authentication (user must be an organiser).
    - **Body:** `{ "user_id": <user_id_to_accept> }`.
    - **Returns:** 
    ```
    {'message': f'User {membership_request.profile.user.username} has been added to the group "{group.name}".'}
    ```

- `accept_invitation` (`POST /groups/{id}/accept-invitation/`)
    Accepts a pending invitation to join a group.
    - **Requires:** Authentication.
    - **Returns:**
    ```
    {'message': f'You have joined the group "{group.name}".'}
    ```

- `decline_invitation` (`POST /groups/{id}/decline-invitation/`)
    Declines a pending invitation to join a group.
    - **Requires:** Authentication.
    - **Returns:** 
    ```
    # If there are no invitations
    {'error': 'No pending invitation to decline'}

    # If there is invitation
    {'message': f'You have declined the invitation to join "{group.name}".'}
    ```

---
## Events API Endpoints

### `EventViewSet` (`/events/`)
This endpoint manages events. Users can create events, and view events they have created or are participating in.

- `POST /events/`
    - Creates a new event. The user making the request will be set as the creator and automatically added as a participant with a 'going' status.
    - **Requires:** Authentication.
    - **Body:**
    ```json
    {
      "title": "New Team Meeting",
      "description": "Weekly sync-up meeting.",
      "location": 1,
      "group": 1,
      "participants_to_add": [2, 3]
    }
    ```
    - The `location` and `group` fields are optional and expect the ID of the location and group respectively.
    - `participants_to_add` is an optional array of user profile IDs to invite to the event. They will be added with a 'maybe' status.
    - **Returns:** The created event object.
    ```json
    {
        "id": 1,
        "title": "New Team Meeting",
        "description": "Weekly sync-up meeting.",
        "created_at": "2025-06-26T10:00:00Z",
        "creator": 1,
        "location": 1,
        "group": 1,
        "participants": [
            {
                "participant_id": 1,
                "participant_name": "Creator Name",
                "is_joining": "going"
            },
            {
                "participant_id": 2,
                "participant_name": "Participant Two",
                "is_joining": "maybe"
            },
            {
                "participant_id": 3,
                "participant_name": "Participant Three",
                "is_joining": "maybe"
            }
        ]
    }
    ```

- `GET /events/`
    - Lists all events the user has created or is a participant in.
    - **Requires:** Authentication.
    - **Returns:** A list of event objects.

- `GET /events/{id}/`
    - Retrieves the details of a specific event. The user must be a creator or a participant.
    - **Requires:** Authentication.
    - **Returns:** An event object.

- `DELETE /events/{id}/`
    - Deletes an event.
    - **Requires:** Authentication.
    - **Permissions:**
        - If the event is associated with a group, the user must be an 'organiser' of the group.
        - If the event is not associated with a group, the user must be the creator of the event.
    - **Returns:** Status 204 (No Content) on success.

---
## AvailCalendar API Endpoint Details

Has the following view classes
* TimeSlotViewSet
    * Manage time slot suggestions for events the user is involved in.
* CalendarEntryViewSet
    * Manage the user's personal calendar entries (manual or synced).
* CalendarIntegrationViewSet
    * Check if Google Calendar is connected for the user.
* ManualAvailabilityViewSet
    * Manage manual availability time blocks for the user.
* ReminderViewSet
    * Manage reminders linked to a calendar entry.
* GoogleCalendarSyncView
    * Asynchronously sync busy slots from Google Calendar into the database and allow viewing.

### `TimeSlotViewSet` (`/availcalendar/timeslots/`)
Manage time slot suggestions for events the user is involved in.

- `GET /availcalendar/timeslots/`
    - Lists all relevant time slots for the user.
    - **Returns:**
    ```json
    [
      {
        "id": 12,
        "event": 5,
        "user": 7,
        "start_date": "2025-06-21",
        "start_time": "10:00:00",
        "end_date": "2025-06-21",
        "end_time": "11:00:00",
        "duration": 60,
        "status": "not confirmed"
      },
      ...
    ]
    ```

- `POST /availcalendar/timeslots/`
    - Creates a new time slot for an event.
    - **Body:**
    ```json
    {
      "event": 5,
      "user": 7,
      "start_date": "2025-06-21",
      "start_time": "10:00:00",
      "end_date": "2025-06-21",
      "end_time": "11:00:00",
      "duration": 60,
      "status": "not confirmed"
    }
    ```
    - **Returns:** Created time slot object.
    - **Validation:**
      - `end` must be after `start`.
      - `duration` must match the difference between start and end (in minutes).
      - `duration` must be a multiple of 15 minutes.
      - `start_time` and `end_time` must be on a 15-minute boundary (e.g. 00, 15, 30, 45).

---

### `CalendarEntryViewSet` (`/availcalendar/calendar-entries/`)
Manage the user's personal calendar entries (manual or synced).

- `GET /availcalendar/calendar-entries/`
    - Returns all calendar entries owned by the user.
    - **Returns:**
    ```json
    [
      {
        "id": 101,
        "title": "Gym",
        "description": "",
        "start_date": "2025-06-21",
        "start_time": "16:00:00",
        "end_date": "2025-06-21",
        "end_time": "17:00:00",
        "duration": 60,
        "created_at": "2025-06-20T15:00:00Z",
        "updated_at": "2025-06-20T15:00:00Z",
        "source": "manual",
        "google_event_id": null,
        "location": 3,
        "user": 7,
        "event": null
      },
      ...
    ]
    ```

- `POST /availcalendar/calendar-entries/`
    - Creates a new calendar entry (manual, group, or Google event).
    - **Body:**
    ```json
    {
      "title": "Gym",
      "description": "",
      "start_date": "2025-06-21",
      "start_time": "16:00:00",
      "end_date": "2025-06-21",
      "end_time": "17:00:00",
      "duration": 60,
      "source": "manual",
      "location": 3,
      "user": 7,
      "event": 2
    }
    ```
    - **Returns:** Created calendar entry object.
    - **Validation:**
      - `end` must be after `start`.
      - `duration` must match the difference between start and end (in minutes).
      - `duration` must be a multiple of 15 minutes.
      - `start_time` and `end_time` must be on a 15-minute boundary (e.g. 00, 15, 30, 45).

---

### `CalendarIntegrationViewSet.get` (`GET /availcalendar/calendar-integration/`)
Check if Google Calendar is connected for the user.

- **Returns:**
    ```json
    { "connected": true }
    ```
    - **Note:** Returns `false` if not connected. Checks for provider = 'google' and user = current user.

---

### `ManualAvailabilityViewSet` (`/availcalendar/manual-availability/`)
Manage manual availability time blocks for the user.

- `GET /availcalendar/manual-availability/`
    - Lists all recurring and one-time availability blocks.
    - **Returns:**
    ```json
    [
      {
        "id": 8,
        "start_date": "2025-06-21",
        "start_time": "14:00:00",
        "end_date": "2025-06-21",
        "end_time": "15:00:00",
        "duration": 60,
        "recurrence": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE;UNTIL=20250801T000000Z"
      },
      ...
    ]
    ```

- `POST /availcalendar/manual-availability/`
    - Adds a new manual availability with recurrence.
    - **Body:**
    ```json
    {
      "start_date": "2025-06-21",
      "start_time": "14:00:00",
      "end_date": "2025-06-21",
      "end_time": "15:00:00",
      "duration": 60,
      "freq": "WEEKLY",
      "interval": 1,
      "by_day": ["MO", "WE"],
      "until": "2025-08-01T00:00:00Z",
      "count": 10
    }
    ```
    - **Returns:** Created manual availability object (with `recurrence` string).
    - **Validation:**
      - `end` must be after `start`.
      - `duration` must match the difference between start and end (in minutes).
      - `duration` must be a multiple of 15 minutes.
      - `start_time` and `end_time` must be on a 15-minute boundary (e.g. 00, 15, 30, 45).
      - Recurrence rule is built from `freq`, `interval`, `by_day`, `until`, `count`.

---

### `ReminderViewSet` (`/availcalendar/reminders/`)
Manage reminders linked to a calendar entry.

- `GET /availcalendar/reminders/`
    - Lists all reminders set by the user.
    - **Returns:**
    ```json
    [
      {
        "id": 4,
        "remind_at": "2025-06-21T12:00:00Z",
        "calendar_entry": 7,
        "user": 7
      },
      ...
    ]
    ```

- `POST /availcalendar/reminders/`
    - Adds a reminder to a calendar entry.
    - **Body:**
    ```json
    {
      "remind_at": "2025-06-21T12:00:00Z",
      "calendar_entry": 7,
      "user": 7
    }
    ```
    - **Returns:** Created reminder object.

---

### `GoogleCalendarSyncView.get` (`GET /availcalendar/google-sync/`)
Preview Google Calendar busy slots via FreeBusy API.

- **Query Params:** `start`, `end`, `calendars?` (ISO 8601, calendars is optional, default ["primary"])
- **Returns:**
    ```json
    {
      "busy": [
        { "start": "2025-06-21T10:00:00Z", "end": "2025-06-21T11:00:00Z" },
        { "start": "2025-06-22T18:00:00Z", "end": "2025-06-22T19:00:00Z" }
      ]
    }
    ```
    - **Error:** `{ "error": "Google account not connected" }` (400) or `{ "error": "Failed to fetch from Google", "details": ... }` (502)

---

### `GoogleCalendarSyncView.put` (`PUT /availcalendar/google-sync/`)
Asynchronously sync busy slots from Google Calendar into the database.

- **Body:**
    ```json
    {
      "start": "2025-06-21T00:00:00Z",
      "end": "2025-06-22T00:00:00Z",
      "calendars": ["primary"]
    }
    ```
- **Returns:**
    ```json
    { "message": "Calendar synchronization initiated." }
    ```
    - **Error:** `{ "error": ... }` (400/502)
