from dataclasses import dataclass

from app.OLD_backend.cadets import load_list_of_all_cadets

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.group_allocations.cadet_event_allocations import (
    load_list_of_cadets_with_allocated_groups_at_event,
)
from app.OLD_backend.data.cadets_at_event_id_level import load_cadets_at_event
from app.OLD_backend.group_allocations.boat_allocation import (
    load_list_of_cadets_at_event_with_dinghies,
)
from app.OLD_backend.data.dinghies import load_list_of_cadets_at_event_with_club_dinghies
from app.OLD_backend.configuration import (
    load_list_of_boat_classes,
    load_list_of_club_dinghies,
)

from app.objects.cadet_with_id_at_event import ListOfCadetsWithIDAtEvent
from app.objects.cadets import ListOfCadets
from app.objects.cadet_at_event_with_dinghy_with_ids import ListOfCadetAtEventWithDinghies
from app.objects.club_dinghies import (
    ListOfClubDinghies,
)
from app.objects.cadet_at_event_with_club_boat_with_ids import ListOfCadetAtEventWithClubDinghies
from app.objects.boat_classes import ListOfBoatClasses
from app.objects.events import Event
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups


##### MORE GENERIC VERSION OF THIS - WE USE THIS SORT OF GLUE CODE A LOT
##### TO WORK FOR ALL TABLES AND REPORTS
@dataclass
class RequiredDataForReport:
    list_of_all_cadets: ListOfCadets
    list_of_cadets_at_event_with_dinghies: ListOfCadetAtEventWithDinghies
    list_of_cadets_at_event: ListOfCadetsWithIDAtEvent
    list_of_boat_classes: ListOfBoatClasses
    list_of_club_dinghies: ListOfClubDinghies
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
    list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithClubDinghies


def get_data_required_for_event(
    interface: abstractInterface, event: Event
) -> RequiredDataForReport:
    list_of_cadets_at_event_with_dinghies = load_list_of_cadets_at_event_with_dinghies(
        interface=interface, event=event
    )
    list_of_cadets_at_event = load_cadets_at_event(interface=interface, event=event)
    list_of_boat_classes = load_list_of_boat_classes(interface)
    list_of_club_dinghies = load_list_of_club_dinghies(interface)
    list_of_cadet_ids_with_groups = load_list_of_cadets_with_allocated_groups_at_event(
        interface=interface, event=event
    )
    list_of_all_cadets =load_list_of_all_cadets(interface.data)
    list_of_cadets_at_event_with_club_dinghies = (
        load_list_of_cadets_at_event_with_club_dinghies(
            interface=interface, event=event
        )
    )

    return RequiredDataForReport(
        list_of_all_cadets=list_of_all_cadets,
        list_of_cadets_at_event_with_dinghies=list_of_cadets_at_event_with_dinghies,
        list_of_boat_classes=list_of_boat_classes,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets_at_event=list_of_cadets_at_event,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        list_of_cadets_at_event_with_club_dinghies=list_of_cadets_at_event_with_club_dinghies,
    )
