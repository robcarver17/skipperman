from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroup

from app.objects.events import Event, ListOfEvents


from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_all_roles_across_recent_events_for_volunteer_as_dict_with_sort_order,
)
from app.objects.volunteers import Volunteer


from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers


def get_volunteer_data_dump(object_store: ObjectStore) -> pd.DataFrame:

    list_of_all_volunteers = get_list_of_volunteers(object_store)
    list_of_all_volunteers = list_of_all_volunteers.sort_by_surname()
    list_of_all_row_data = ListOfVolunteerRowData(
        [
            get_row_data_for_volunteer(object_store=object_store, volunteer=volunteer)
            for volunteer in list_of_all_volunteers
        ]
    )

    all_data_as_dict = {
        "Name": list_of_all_row_data.list_of_names(),
        "Connected cadets": list_of_all_row_data.list_of_connected_cadets(),
        "Skills": list_of_all_row_data.list_of_skills_str(),
    }

    all_data_as_dict.update(
        list_of_all_row_data.dict_of_list_of_roles_and_groups_by_event_as_str()
    )

    return pd.DataFrame(all_data_as_dict)


@dataclass
class VolunteerRowData:
    name: str
    roles_as_dict: Dict[Event, RoleAndGroup]
    skills_as_str: str
    connected_cadets_as_str: str


class ListOfVolunteerRowData(List[VolunteerRowData]):
    def list_of_names(self):
        return [row_data.name for row_data in self]

    def list_of_skills_str(self):
        return [row_data.skills_as_str for row_data in self]

    def list_of_connected_cadets(self):
        return [row_data.connected_cadets_as_str for row_data in self]

    def dict_of_list_of_roles_and_groups_by_event_as_str(self) -> Dict[str, List[str]]:
        ordered_list_of_events = self.all_events_most_recent_first()
        dict_of_list_of_roles_and_groups_by_event_as_str = dict(
            [
                (
                    str(event),
                    self.list_of_roles_and_groups_for_specific_event_as_str(event),
                )
                for event in ordered_list_of_events
            ]
        )

        return dict_of_list_of_roles_and_groups_by_event_as_str

    def list_of_roles_and_groups_for_specific_event_as_str(
        self, event: Event
    ) -> List[str]:
        return [str(row_data.roles_as_dict.get(event, "")) for row_data in self]

    def all_events_most_recent_first(self) -> List[Event]:
        all_events = self.all_events()
        all_events = all_events.sort_by_start_date_desc()

        return all_events

    def all_events(self) -> ListOfEvents:
        all_events = []
        for volunteer_row in self:
            all_events += list(volunteer_row.roles_as_dict.keys())

        return ListOfEvents(list(set(all_events)))

from app.backend.volunteers.skills import get_dict_of_existing_skills_for_volunteer
from app.backend.volunteers.connected_cadets import get_list_of_cadets_associated_with_volunteer

def get_row_data_for_volunteer(
    object_store: ObjectStore, volunteer: Volunteer
) -> VolunteerRowData:
    name = volunteer.name
    roles_with_teams_as_dict = (
        get_all_roles_across_recent_events_for_volunteer_as_dict_with_sort_order(
            object_store=object_store, volunteer=volunteer
        )
    )
    roles_with_groups_as_dict = dict([
        (event, role_with_team.role_and_group()) for event, role_with_team in roles_with_teams_as_dict.items()
    ])

    skills = get_dict_of_existing_skills_for_volunteer(object_store=object_store, volunteer=volunteer)
    skills_as_str = str(skills)

    connected_cadets = get_list_of_cadets_associated_with_volunteer(object_store=object_store, volunteer=volunteer)
    connected_cadets_as_str = connected_cadets.as_str()

    return VolunteerRowData(
        name=name,
        skills_as_str=skills_as_str,
        roles_as_dict=roles_with_groups_as_dict,
        connected_cadets_as_str=connected_cadets_as_str,
    )
