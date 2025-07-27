# Polls API Endpoints

### Poll Management

- `PollViewSet.create` (`POST /polls/`)
    Creates a new poll with specified timeslot options. Only event organisers can create polls.
    - **Requires:** Authentication (user must be an event organiser).
    - **Body:** 
    ```
    {
        "event": <event_id>,
        "option_ids": [<timeslot_id1>, <timeslot_id2>, ...]
    }
    ```
    - **Returns:** 
    ```
    {
        "id": <poll_id>,
        "created_at": "2025-06-20T10:00:00Z",
        "event": <event_id>,
        "options": [
            {
                "id": <option_id>,
                "timeslot": <timeslot_id>,
                "start_date": "2025-06-20",
                "start_time": "10:00:00",
                "end_date": "2025-06-20",
                "end_time": "11:00:00",
                "vote_count": 0
            }
        ],
        "total_votes": 0
    }
    ```

- `PollViewSet.list` (`GET /polls/`)
    Lists all available polls.
    - **Requires:** Authentication.
    - **Returns:** 
    ```
    [
        {
            "id": <poll_id>,
            "created_at": "2025-06-20T10:00:00Z",
            "event": <event_id>,
            "options": [...],
            "total_votes": 5
        }
    ]
    ```

- `PollViewSet.retrieve` (`GET /polls/{id}/`)
    Retrieves the details of a specific poll including all options and vote counts.
    - **Requires:** Authentication.
    - **Returns:** 
    ```
    {
        "id": <poll_id>,
        "created_at": "2025-06-20T10:00:00Z",
        "event": <event_id>,
        "options": [
            {
                "id": <option_id>,
                "timeslot": <timeslot_id>,
                "start_date": "2025-06-20",
                "start_time": "10:00:00",
                "end_date": "2025-06-20",
                "end_time": "11:00:00",
                "vote_count": 3
            }
        ],
        "total_votes": 5
    }
    ```

- `PollViewSet.destroy` (`DELETE /polls/{id}/`)
    Deletes a poll. Only event organisers can delete polls.
    - **Requires:** Authentication (user must be an event organiser).
    - **Returns:** 
    ```
    # Success
    {"message": "Poll deleted successfully."} (HTTP 204)
    
    # Permission denied
    {"error": "Only organisers can delete the poll."} (HTTP 403)
    ```

### Poll Generation

- `generate_poll` (`POST /polls/generate/`)
    Automatically generates a poll using smart scheduling to find the best timeslots based on participant availability.
    - **Requires:** Authentication (user must be an event organiser).
    - **Body:** 
    ```
    {
        "event": <event_id>,
        "start_date": "2025-06-20",
        "start_time": "09:00:00",
        "end_date": "2025-06-25",
        "end_time": "17:00:00",
        "duration": 60,
        "buffer": 15,
        "min_attendance": 0.5
    }
    ```
    - **Returns:** 
    ```
    # Success
    {
        "id": <poll_id>,
        "created_at": "2025-06-20T10:00:00Z",
        "event": <event_id>,
        "options": [
            {
                "id": <option_id>,
                "timeslot": <timeslot_id>,
                "start_date": "2025-06-22",
                "start_time": "14:00:00",
                "end_date": "2025-06-22",
                "end_time": "15:00:00",
                "vote_count": 0
            }
        ],
        "total_votes": 0
    }
    
    # No suitable timeslots
    {
        "error": "No timeslots fit the criteria. Adjust the date range or attendance threshold."
    } (HTTP 204)
    
    # Permission denied
    {"error": "Only organisers can generate a poll."} (HTTP 403)
    ```

### Poll Options

- `list_options` (`GET /polls/{id}/options/`)
    Lists all poll options with their vote counts for a specific poll.
    - **Requires:** Authentication.
    - **Returns:** 
    ```
    [
        {
            "id": <option_id>,
            "timeslot": <timeslot_id>,
            "start_date": "2025-06-20",
            "start_time": "10:00:00",
            "end_date": "2025-06-20",
            "end_time": "11:00:00",
            "vote_count": 3
        }
    ]
    ```

- `PollOptionViewSet.destroy` (`DELETE /poll-options/{id}/`)
    Removes a specific poll option. Only event organisers can delete poll options.
    - **Requires:** Authentication (user must be an event organiser).
    - **Returns:** 
    ```
    # Success
    {"message": "Poll option removed."} (HTTP 204)
    
    # Permission denied
    {"error": "Only organisers can delete poll options."} (HTTP 403)
    ```

### Voting

- `PollVoteViewSet.create` (`POST /poll-votes/`)
    Casts a vote for a specific poll option. Users can only vote once per option and must be event participants.
    - **Requires:** Authentication (user must be an event participant).
    - **Body:** 
    ```
    {
        "poll_option": <option_id>
    }
    ```
    - **Returns:** 
    ```
    # Success
    {
        "id": <vote_id>,
        "poll_option": <option_id>,
        "voter": {
            "user_id": "abc123",
            "name": "John Doe"
        },
        "voted_at": "2025-06-20T10:00:00Z"
    }
    
    # Already voted
    {"poll_option": ["You have already voted for this option."]} (HTTP 400)
    
    # Not a participant
    {"detail": "You are not a participant of this event."} (HTTP 403)
    ```

- `PollVoteViewSet.destroy` (`DELETE /poll-votes/{id}/`)
    Removes a specific vote. Users can only revoke their own votes.
    - **Requires:** Authentication (user must own the vote).
    - **Returns:** 
    ```
    # Success
    {"message": "Vote removed."} (HTTP 204)
    
    # Permission denied
    {"error": "You can only revoke your own vote."} (HTTP 403)
    ```

### Error Responses

All endpoints may return the following error responses:

- **400 Bad Request:** Invalid data format or validation errors
- **401 Unauthorized:** Missing or invalid authentication
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server-side errors

### Data Models

**Poll:**
- `id`: Unique identifier
- `created_at`: Timestamp when poll was created
- `event`: Associated event ID
- `options`: List of poll options
- `total_votes`: Total number of votes across all options

**PollOption:**
- `id`: Unique identifier
- `timeslot`: Associated timeslot ID
- `start_date`: Start date of the timeslot
- `start_time`: Start time of the timeslot
- `end_date`: End date of the timeslot
- `end_time`: End time of the timeslot
- `vote_count`: Number of votes for this option

**PollVote:**
- `id`: Unique identifier
- `poll_option`: Associated poll option ID
- `voter`: User profile who cast the vote
- `voted_at`: Timestamp when vote was cast 