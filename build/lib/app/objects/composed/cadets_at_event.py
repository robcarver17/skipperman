from typing import List

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import \
    ListOfCadetsWithBoatClassAndPartnerAtEventOnDay, DictOfDaysBoatClassAndPartners
from app.objects.composed.cadets_at_event_with_club_dinghies import ListOfClubDinghysAtEventOnDayForCadet, \
    DictOfDaysAndClubDinghiesAtEventForCadet
from app.objects.composed.cadets_at_event_with_groups import DaysAndGroups, ListOfCadetsWithGroupOnDay

from app.objects.composed.cadets_at_event_with_registration_data import DictOfCadetsWithRegistrationData
from app.objects_OLD.cadet_at_event import CadetEventData


class CadetAtEvent:
    cadet: Cadet
    cadet_event_data: CadetEventData
    days_and_groups: DaysAndGroups
    days_and_boat_classes: DictOfDaysBoatClassAndPartners
    club_dinghies: DictOfDaysAndClubDinghiesAtEventForCadet

class ListOfCadetsAtEvent(List[CadetAtEvent]):
    pass

def compose_list_of_cadets_at_event(list_of_cadets: ListOfCadets,
                                    list_of_cadets_with_event_data: DictOfCadetsWithRegistrationData,
                                    list_of_cadets_with_group: ListOfCadetsWithGroupOnDay,
                                    list_of_cadets_with_boat_class_and_partner_at_event_on_day: ListOfCadetsWithBoatClassAndPartnerAtEventOnDay,
                                    list_of_club_dinghies_at_event_on_day_for_cadet: ListOfClubDinghysAtEventOnDayForCadet
                                    ):
    pass

