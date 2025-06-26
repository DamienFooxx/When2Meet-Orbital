# Smart Scheduling API Endpoint

### `SchedulingViewSet.find_available_slots` (`POST /smartschedule/find-available-slots/`)
Finds the best available timeslots for a group of users based on their availability.

- **Requires:** Authentication
- **Body:**
    ```json
    {
        "group_id": "string (optional)",
        "users": ["user_id_1", "user_id_2"],
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "start_time": "HH:MM:SS",
        "end_time": "HH:MM:SS",
        "duration": "integer (multiple of 15)",
        "type_of_meetup": "'virtual' or 'physical' (default: 'virtual')",
        "buffer": "integer (optional, multiple of 15, default: 15 for virtual, 30 for physical)",
        "minimum_attendance": "decimal (0.00 to 100.00, default: 50.00)"
    }
    ```
- **Returns:**
    ```json
    {
        "available_slots": [
            {
                "start_date": "YYYY-MM-DD",
                "start_time": "HH:MM:SS",
                "end_date": "YYYY-MM-DD",
                "end_time": "HH:MM:SS",
                "free_count": "integer",
                "group_size": "integer",
                "attendance": "float"
            },
            ...
        ]
    }
    ```
- **Errors:**
    - `400 Bad Request`: If required fields are missing, validation fails, or users are not found.
    - `401 Unauthorized`: If the user is not authenticated.

- **Notes on `duration` and `buffer` requirements:**
    - `duration` must be a positive integer and a multiple of 15 (e.g., 15, 30, 45, 60, ...).
    - `buffer` (if provided) must also be a multiple of 15. If not provided, it defaults to 15 for virtual meetups and 30 for physical meetups.
    - Both `duration` and `buffer` are measured in minutes.
    - If `buffer` is not specified, the system will automatically assign the default based on the `type_of_meetup` field.
    - If an invalid value is provided for either field (e.g., not a multiple of 15, negative, or zero for duration), the API will return a 400 Bad Request with a validation error message.
    - Example valid values: `duration: 30`, `buffer: 15` (virtual), `buffer: 30` (physical).
