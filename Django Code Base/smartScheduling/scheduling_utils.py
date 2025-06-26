from datetime import datetime, date, time, timedelta
from availcalendar.models import CalendarEntry, ManualAvailability
from accounts.models import Profile
from django.utils.timezone import make_aware

"""
This file stores all the helper methods for the scheduling engine
"""

def generate_potential_timeslots(start_date, end_date, start_time, end_time, duration):
    """
    Generate all timeslots between start_date and end_date,
    bounded daily by start_time and end_time, and of fixed duration.

    Parameters:
    - start_date (datetime.date)
    - end_date (datetime.date)
    - start_time (datetime.time)
    - end_time (datetime.time)
    - duration_minutes (int)

    Returns:
    - List of (datetime_start, datetime_end) tuples
    """
    slots = []
    current_date = start_date

    while current_date <= end_date:
        day_start = datetime.combine(current_date, start_time)
        day_end = datetime.combine(current_date, end_time)
        slot_start = day_start

        while slot_start + timedelta(minutes = duration) <= day_end:
            slot_end = slot_start + timedelta(minutes = duration)
            if slot_start.minute % 15 == 0 and slot_end.minute % 15 == 0:
                # Adds potential timeslot into slots list
                slots.append((slot_start, slot_end))
            # Move on to next timeslot in 15 minute intervals
            slot_start += timedelta(minutes = 15)
        # Move on to the next day
        current_date += timedelta(days = 1)
    
    return slots

def get_user_busy_slots(user_id, start_date, start_time, end_date, end_time, buffer):
    """
    Takes in a user_id and start and end dates for the range of dates and times specified
    It queries from the user linked: 
    CalendarEntries (Added events from groups, google calendar or previous manual availability inputs)
    ManualAvailabilities. (Manually inputted unavailable times on query)

    Returns:
    - The user availabilities as a list of 
        (start_datetime, end_datetime) 
    tuples of all busy slots.
    """
    def get_busy_slots_in_range(model_cls, user_id, start_datetime, end_datetime, buffer_delta):
        """
        Generic helper method to return a List of tuples of start_datetime and end_datetimes.
        This can work with both ManualAvailabilities and CalendarEntry models.
        """
        # Stores the calendar entries within the date and time 
        entries = model_cls.objects.filter(
            user_id = user_id,
            start_date__lte = end_datetime.date(),
            end_date__gte = start_datetime.date()
        )

        busy_slots = []

        for entry in entries:
            entry_start = datetime.combine(entry.start_date, entry.start_time) - buffer_delta
            entry_end = datetime.combine(entry.end_date, entry.end_time)
            # Checks for overlap in datetime and not just date
            if entry_start < end_datetime and entry_end > start_datetime:
                busy_slots.append((entry_start, entry_end))

        return busy_slots

    busy_slots = []
    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)
    # Adds a buffer to the start of each busy slot to account for travel time or preparation
    buffer_delta = timedelta(minutes=buffer)

    # Get Calendar Entries from user
    calendar_busy_slots = get_busy_slots_in_range(
        CalendarEntry,
        user_id,
        start_datetime,
        end_datetime,
        buffer_delta
    )
    # Add slots to busy_slots list
    busy_slots.extend(calendar_busy_slots)

    # Get manual availabilites from user
    manual_busy_slots = get_busy_slots_in_range(
        ManualAvailability,
        user_id,
        start_datetime,
        end_datetime,
        buffer_delta
    )
    # Add slots to busy_slots list
    busy_slots.extend(manual_busy_slots)
    
    return busy_slots

def count_number_of_free_users_per_slot(
        potential_timeslots, 
        group_users, 
        start_date, 
        start_time, 
        end_date, 
        end_time,
        minimum_attendance,
        buffer
        ):
    """
    Helper function to count number of users free in each potential timeslot

    Returns a list of dictionaries with (start_date, start_time, end_date, end_time) as keys
    Values of the dict are free_count (number of users free for that slot), attendance, group_size
    """
    def slots_overlaps_any(slots, busy_slots):
        """
        Helper function to check if a given time slot overlaps with any of a user's busy slots.

        Returns:
            bool: True if there is an overlap, False otherwise.
        """
        slot_start, slot_end = slots
        for busy_start, busy_end in busy_slots:
            # Overlap occurs if one slot starts before the other ends, and vice versa
            if slot_start < busy_end and slot_end > busy_start:
                return True
        return False

    def attendance_percent(free_count, group_size):
        """
        Helper function to calculate the attendance percentage.

        Returns:
            float: The attendance percentage, rounded to two decimal places.
        """
        # Helper to get attendance ratio
        if group_size:
            ratio = (free_count / group_size) * 100
            return round(ratio, 2)
        return 0.0
    
    group_size = len(group_users)

    # Pre-fetch and map all users' busy slots to optimize lookups
    user_busy_map = {}
    for user in group_users:
        # Gets busy slots per user
        busy = get_user_busy_slots(
            user_id = user.unique_id,
            start_date = start_date,
            start_time = start_time,
            end_date = end_date,
            end_time = end_time,
            buffer=buffer
        )
        # Add the list of busy slots to each user, {user_id: [list of busy slots]}
        user_busy_map[user.unique_id] = busy

    potential_slots = {}
    final_slots = {}

    # Find potential_slots
    for slot_start, slot_end in potential_timeslots:
        free_count = 0
        for user in group_users:
            # Iterate all users inside the group
            if not slots_overlaps_any((slot_start, slot_end), user_busy_map[user.unique_id]):
                # Checks if there are any overlap between the users busy slots and potential timeslots
                # If there is no overlap, add 1 count
                free_count += 1
        # Calculate attendance
        attendance = attendance_percent(free_count, group_size)
        # Create dict of slots with details
        potential_slots[(slot_start, slot_end)] = {
            'free_count': free_count,
            'group_size': group_size,
            'attendance': attendance
        }
    # Filter out slots that do not meet the minimum attendance requirement
    min_attendance_slots = {
        k: v for k, v in potential_slots.items()
        if v['attendance'] >= minimum_attendance
    }
    # Split date and time to 2 separate entries
    # Returns a Dictionary where the key are tuple of (start_datetime, end_datetime)
    for (slot_start, slot_end), info in min_attendance_slots.items():
        key = (
            slot_start,
            slot_end,
        )
        final_slots[key] = info

    return final_slots