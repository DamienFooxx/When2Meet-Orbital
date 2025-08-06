---

### `EventParticipantViewSet` (`/eventparticipants/`)
Read-only endpoint to list participants and their status for a given event.

- `GET /eventparticipants/?event=<event_id>`
    - Lists all participants and their RSVP status for the specified event.
    - **Returns:**
    ```json
    [
      {
        "participant_id": 123,
        "participant_name": "Alice Smith",
        "is_joining": "going" // or "maybe", "declined"
      },
      ...
    ]
    ``` 