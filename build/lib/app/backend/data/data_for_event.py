from dataclasses import dataclass

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.cadets import DEPRECATE_load_list_of_all_cadets
from app.backend.data.group_allocations_old import load_list_of_cadets_with_allocated_groups_at_event
from app.backend.data.cadets_at_event import load_list_of_cadets_at_event_with_dinghies, DEPRECATED_load_cadets_at_event
from app.backend.data.resources import load_list_of_boat_classes, load_list_of_club_dinghies, DEPRECATE_load_list_of_cadets_at_event_with_club_dinghies

from app.objects.cadet_at_event import ListOfCadetsAtEvent
from app.objects.cadets import ListOfCadets
from app.objects.dinghies import ListOfCadetAtEventWithDinghies
from app.objects.club_dinghies import ListOfClubDinghies, ListOfCadetAtEventWithClubDinghies
from app.objects.dinghies import ListOfDinghies
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups


##### MORE GENERIC VERSION OF THIS - WE USE THIS SORT OF GLUE CODE A LOT
##### TO WORK FOR ALL TABLES AND REPORTS
@dataclass
class RequiredDataForReport:
    list_of_all_cadets: ListOfCadets
    list_of_cadets_at_event_with_dinghies: ListOfCadetAtEventWithDinghies
    list_of_cadets_at_event: ListOfCadetsAtEvent
    list_of_boat_classes: ListOfDinghies
    list_of_club_dinghies: ListOfClubDinghies
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
    list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithClubDinghies

def get_data_required_for_event(interface: abstractInterface, event: Event) -> RequiredDataForReport:
    list_of_cadets_at_event_with_dinghies = load_list_of_cadets_at_event_with_dinghies(event)
    list_of_cadets_at_event=DEPRECATED_load_cadets_at_event(event)
    list_of_boat_classes=load_list_of_boat_classes()
    list_of_club_dinghies=load_list_of_club_dinghies()
    list_of_cadet_ids_with_groups = load_list_of_cadets_with_allocated_groups_at_event(event)
    list_of_all_cadets = DEPRECATE_load_list_of_all_cadets()
    list_of_cadets_at_event_with_club_dinghies = DEPRECATE_load_list_of_cadets_at_event_with_club_dinghies(event)

    return RequiredDataForReport(
        list_of_all_cadets=list_of_all_cadets,
        list_of_cadets_at_event_with_dinghies=list_of_cadets_at_event_with_dinghies,
        list_of_boat_classes=list_of_boat_classes,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets_at_event=list_of_cadets_at_event,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        list_of_cadets_at_event_with_club_dinghies=list_of_cadets_at_event_with_club_dinghies
    )
