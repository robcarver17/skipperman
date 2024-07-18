
import pandas as pd

from app.OLD_backend.rota.sorting_and_filtering import \
    RotaSortsAndFilters, get_sorted_and_filtered_list_of_volunteers_at_event
from app.OLD_backend.rota.volunteer_rota import get_volunteers_in_role_at_event
from app.OLD_backend.volunteers.volunteers import (
 get_dict_of_existing_skills,
)
from app.objects.day_selectors import Day
from app.objects.volunteers_at_event import (
    DEPRECATE_VolunteerAtEvent, )
from app.objects.primtive_with_id.volunteer_roles_and_groups import ListOfVolunteersWithIdInRoleAtEvent

from app.objects.events import Event

from app.data_access.data_layer.ad_hoc_cache import AdHocCache

def get_volunteer_matrix(
    cache: AdHocCache, event: Event, sorts_and_filters: RotaSortsAndFilters
) -> pd.DataFrame:

    list_of_volunteers_at_event = get_sorted_and_filtered_list_of_volunteers_at_event(
        cache=cache,
        event=event,
        sorts_and_filters=sorts_and_filters,
    )
    volunteers_in_roles_at_event = cache.get_from_cache(get_volunteers_in_role_at_event, event=event)

    list_of_rows = [
        row_for_volunteer_at_event(
            cache=cache,
            event=event,
            volunteer_at_event=volunteer_at_event,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event
        )
        for volunteer_at_event in list_of_volunteers_at_event
    ]

    return pd.DataFrame(list_of_rows)


def row_for_volunteer_at_event(
        cache: AdHocCache,
    volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    event: Event,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> pd.Series:

    volunteer = volunteer_at_event.volunteer
    name = volunteer.name
    skills_dict = cache.get_from_cache(get_dict_of_existing_skills, volunteer=volunteer)
    preferred = volunteer_at_event.preferred_duties
    same_different = volunteer_at_event.same_or_different


    volunteers_in_roles_dict = dict(
        [
            (
                day.name,
                role_and_group_string_for_day(
                    volunteer_at_event=volunteer_at_event,
                    day=day,
                    volunteers_in_roles_at_event=volunteers_in_roles_at_event,
                ),
            )
            for day in event.weekdays_in_event()
        ]
    )

    result_dict = dict(Name=name, Skills=str(skills_dict), preferred=preferred, same_different=same_different)
    result_dict.update(volunteers_in_roles_dict)

    return pd.Series(result_dict)


def role_and_group_string_for_day(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    day: Day,
    volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
) -> str:
    if not volunteer_at_event.available_on_day(day):
        return "Unavailable"
    else:
        return str(
            volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(
                volunteer_id=volunteer_at_event.volunteer_id,
                day=day,
                return_empty_if_missing=True,
            ).role_and_group
        )
