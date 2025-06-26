from smartScheduling.scheduling_utils import generate_potential_timeslots, count_number_of_free_users_per_slot

def schedule_best_timeslots(
    users,
    start_date, start_time,
    end_date, end_time,
    duration, buffer,
    min_attendance
    ):
    """
    Scheduling Engine to output best_timeslots based on set criteria
    
    Returns slots as a list of dictionaries with (start_date, start_time, end_date, end_time) as keys
    Values of the dict are free_count (number of users free for that slot), attendance, group_size 
    """
    # Get list of potential timeslots
    potential_timeslots = generate_potential_timeslots(
        start_date,
        end_date,
        start_time,
        end_time,
        duration
    )

    # Retrieve the busy slots 
    best_timeslots = count_number_of_free_users_per_slot(
        potential_timeslots,
        users,
        start_date,
        start_time,
        end_date,
        end_time,
        min_attendance,
        buffer
    )

    return best_timeslots
