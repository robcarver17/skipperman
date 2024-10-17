from dataclasses import dataclass
from typing import List

from app.objects.composed.volunteers_with_skills import SkillsDict
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId
from app.objects.volunteers import Volunteer
from app.objects_OLD.cadets_with_groups import ListOfCadetsAtEventWithGroupsByDay


@dataclass
class VolunteerEventData:
    event: Event
    availablity: DaySelector
    list_of_associated_cadets: ListOfCadetsAtEventWithGroupsByDay
    preferred_duties: str = ""  ## information only
    same_or_different: str = ""  ## information only
    any_other_information: str = (
        ""  ## information only - double counted as required twice
    )
    notes: str = ""

    @classmethod
    def from_volunteer_at_event_with_id(cls, event: Event, volunteer_at_event_with_id: VolunteerAtEventWithId, list_of_associated_cadets: ListOfCadetsAtEventWithGroupsByDay):
        availability = volunteer_at_event_with_id.availablity.intersect(event.day_selector_with_covered_days())
        return cls(
            event=event,
            availablity=availability,
            list_of_associated_cadets=list_of_associated_cadets,
            preferred_duties=volunteer_at_event_with_id.preferred_duties,
            same_or_different=volunteer_at_event_with_id.same_or_different,
            any_other_information=volunteer_at_event_with_id.same_or_different
        )


@dataclass
class VolunteerAtEventWithSkills:
    volunteer: Volunteer
    skills_dict: SkillsDict
    volunteer_event_data: VolunteerEventData

    @classmethod
    def from_volunteer_at_event_with_id(cls, event: Event, volunteer: Volunteer, volunteer_at_event_with_id: VolunteerAtEventWithId, skills_dict: SkillsDict, list_of_associated_cadets: ListOfCadetsAtEventWithGroupsByDay):
        return cls(
            volunteer=volunteer,
            skills_dict=skills_dict,
            volunteer_event_data=VolunteerEventData.from_volunteer_at_event_with_id(
                event=event,
                volunteer_at_event_with_id=volunteer_at_event_with_id,
                list_of_associated_cadets=list_of_associated_cadets
            )
        )


class ListOfVolunteersAtEventWithSkills(List[VolunteerAtEventWithSkills]):
    pass
