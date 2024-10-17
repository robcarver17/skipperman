from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
from app.objects.volunteer_roles_and_groups_with_id import RoleAndGroupDEPRECATE

from app.objects.events import Event, ListOfEvents

from app.OLD_backend.volunteers.volunteers import (
    get_dict_of_existing_skills,
    get_connected_cadets,
)

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import \
    get_all_roles_across_recent_events_for_volunteer_as_dict_with_sort_order
from app.objects.volunteers import Volunteer

from app.data_access.store.data_access import DataLayer


from app.OLD_backend.data.volunteers import VolunteerData


def get_volunteer_data_dump(data_layer: DataLayer) -> pd.DataFrame:
    volunteer_data = VolunteerData(data_layer)
    list_of_all_volunteers = volunteer_data.get_list_of_volunteers()
    list_of_all_volunteers = list_of_all_volunteers.sort_by_surname()
    list_of_all_row_data = ListOfVolunteerRowData(
        [
            get_row_data_for_volunteer(data_layer=data_layer, volunteer=volunteer)
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
    roles_as_dict: Dict[Event, RoleAndGroupDEPRECATE]
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


def get_row_data_for_volunteer(
    data_layer: DataLayer, volunteer: Volunteer
) -> VolunteerRowData:
    name = volunteer.name
    roles_as_dict = get_all_roles_across_recent_events_for_volunteer_as_dict_with_sort_order(
        data_layer=data_layer, volunteer=volunteer
    )
    skills = get_dict_of_existing_skills(data_layer=data_layer, volunteer=volunteer)
    skills_as_str = str(skills)

    connected_cadets = get_connected_cadets(data_layer=data_layer, volunteer=volunteer)
    connected_cadets_as_str = connected_cadets.as_str()

    return VolunteerRowData(
        name=name,
        skills_as_str=skills_as_str,
        roles_as_dict=roles_as_dict,
        connected_cadets_as_str=connected_cadets_as_str,
    )
