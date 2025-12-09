import pandas as pd

from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore

from app.backend.rota.sorting_and_filtering import (
    RotaSortsAndFilters,
    get_sorted_and_filtered_dict_of_volunteers_at_event,
)

from app.objects.day_selectors import Day
from app.objects.events import Event


def get_volunteer_matrix(
    object_store: ObjectStore, event: Event, sorts_and_filters: RotaSortsAndFilters
) -> pd.DataFrame:
    dict_of_volunteers_at_event = get_sorted_and_filtered_dict_of_volunteers_at_event(
        object_store=object_store,
        event=event,
        sorts_and_filters=sorts_and_filters,
    )

    list_of_rows = [
        row_for_volunteer_at_event(volunteer=volunteer, volunteer_data=volunteer_data)
        for volunteer, volunteer_data in dict_of_volunteers_at_event.items()
    ]

    return pd.DataFrame(list_of_rows)


def row_for_volunteer_at_event(
    volunteer: Volunteer, volunteer_data: AllEventDataForVolunteer
) -> pd.Series:
    name = volunteer.name
    skills_dict = volunteer_data.volunteer_skills
    preferred = volunteer_data.registration_data.preferred_duties
    same_different = volunteer_data.registration_data.same_or_different

    volunteers_in_roles_dict = dict(
        [
            (
                day.name,
                role_and_group_string_for_day(
                    volunteer_data=volunteer_data,
                    day=day,
                ),
            )
            for day in volunteer_data.event.days_in_event()
        ]
    )

    result_dict = dict(
        Name=name,
        Skills=str(skills_dict),
        preferred=preferred,
        same_different=same_different,
    )
    result_dict.update(volunteers_in_roles_dict)

    return pd.Series(result_dict)


def role_and_group_string_for_day(
    volunteer_data: AllEventDataForVolunteer,
    day: Day,
) -> str:
    availability = volunteer_data.registration_data.availablity
    if not availability.available_on_day(day):
        return "Unavailable"
    else:
        return str(volunteer_data.roles_and_groups.role_and_group_on_day(day))
