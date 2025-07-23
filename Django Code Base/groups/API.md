# Groups API Endpoints

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
