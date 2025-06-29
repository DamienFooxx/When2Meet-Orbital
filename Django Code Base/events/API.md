# Events API Endpoints

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
