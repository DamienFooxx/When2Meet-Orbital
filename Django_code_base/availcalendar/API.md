# AvailCalendar API Endpoint Details

Has the following view classes
* EventViewSet
    * Manage user-created events or events the user is participating in.
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

### `EventViewSet` (`/availcalendar/events/`)
Manage user-created events or events the user is participating in.

- `GET /availcalendar/events/`
    - Lists all events the user created or is a participant of.
    - **Returns:**
    ```json
    [
      {
        "id": 1,
        "title": "Dinner",
        "description": "Let's meet",
        "group": 3,
        "location": 5,
        "creator": 7,
        "confirmed_timeslot": null,
        "created_at": "2025-06-20T15:00:00Z"
      },
      ...
    ]
    ```

- `POST /availcalendar/events/`
    - Creates a new event.
    - **Body:**
    ```json
    {
      "title": "Dinner",
      "description": "...",
      "group": 1,
      "location": 3,
      "participants": [1, 2, 3]
    }
    ```
    - **Returns:** Created event object.

---

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
