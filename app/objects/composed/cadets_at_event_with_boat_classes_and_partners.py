from dataclasses import dataclass
from typing import List, Dict, Union

from app.objects.utils import flatten

from app.objects.exceptions import MissingData, missing_data, MultipleMatches

from app.objects.events import Event, ListOfEvents

from app.objects.boat_classes import BoatClass, ListOfBoatClasses, no_boat_class
from app.objects.cadet_at_event_with_dinghy_with_ids import (
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
    CadetAtEventWithBoatClassAndPartnerWithIds,
    NO_PARTNER_REQUIRED,
    NOT_ALLOCATED,
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day
from app.objects.utils import most_common

class NoPartnerCadetRequired:
    def __repr__(self):
        return NO_PARTNER_REQUIRED

class NoPartnerAllocated:
    def __repr__(self):
        return NOT_ALLOCATED


@dataclass
class CadetBoatClassAndPartnerAtEventOnDay:
    cadet: Cadet
    boat_class: BoatClass
    sail_number: str
    day: Day
    partner_cadet: Cadet = NoPartnerCadetRequired

    def partner_cadet_id(self) -> str:
        return from_partner_cadet_to_id_or_string(self.partner_cadet)

    @classmethod
    def from_cadet_at_event_with_boat_class_and_partner_with_ids(
        cls,
        cadet_at_event_with_boat_class_and_partner_with_ids: CadetAtEventWithBoatClassAndPartnerWithIds,
        list_of_cadets: ListOfCadets,
        list_of_boats: ListOfBoatClasses,
    ):
        partner_cadet = from_cadet_id_to_partner_cadet(
            cadet_id=cadet_at_event_with_boat_class_and_partner_with_ids.partner_cadet_id,
            list_of_cadets=list_of_cadets,
        )
        return cls(
            cadet=list_of_cadets.cadet_with_id(
                cadet_at_event_with_boat_class_and_partner_with_ids.cadet_id
            ),
            boat_class=list_of_boats.object_with_id(
                cadet_at_event_with_boat_class_and_partner_with_ids.boat_class_id
            ),
            day=cadet_at_event_with_boat_class_and_partner_with_ids.day,
            sail_number=cadet_at_event_with_boat_class_and_partner_with_ids.sail_number,
            partner_cadet=partner_cadet,
        )


def from_cadet_id_to_partner_cadet(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Union[Cadet, object]:
    if cadet_id == NOT_ALLOCATED:
        return NoPartnerAllocated
    elif cadet_id == NO_PARTNER_REQUIRED:
        return NoPartnerCadetRequired
    else:
        return list_of_cadets.cadet_with_id(cadet_id)

def from_partner_cadet_to_id_or_string(partner_cadet: Union[Cadet, object]):
    if partner_cadet is NoPartnerAllocated:
        return NOT_ALLOCATED
    elif partner_cadet is NoPartnerCadetRequired:
        return NO_PARTNER_REQUIRED

    return partner_cadet.id

@dataclass
class BoatClassAndPartnerAtEventOnDay:
    boat_class: BoatClass
    sail_number: str
    partner_cadet: Cadet = NoPartnerCadetRequired

    @property
    def has_partner(self) -> bool:
        return valid_partnership_given_partner_cadet(self.partner_cadet)

def no_partnership_given_partner_cadet_as_str(partner_as_str: str):
    return partner_as_str in [NO_PARTNER_REQUIRED, NOT_ALLOCATED]

def no_partnership_object_given_str(partner_as_str: str):
    if partner_as_str==NO_PARTNER_REQUIRED:
        return NoPartnerCadetRequired
    elif partner_as_str == NOT_ALLOCATED:
        return NoPartnerAllocated
    else:
        raise Exception("Don't know how to process %s" % partner_as_str)

def no_partnership_given_partner_cadet(partner: Union[Cadet, object]):
    if partner is NoPartnerCadetRequired:
        return True
    elif partner is NoPartnerAllocated:
        return True

    return False


def valid_partnership_given_partner_cadet(partner: Union[Cadet, object]):
    return not no_partnership_given_partner_cadet(partner)



class DictOfDaysBoatClassAndPartners(Dict[Day, BoatClassAndPartnerAtEventOnDay]):
    @property
    def list_of_days(self):
        return list(self.keys())

    def most_common_boat_class(self) -> BoatClass:
        list_of_boat_classes = [boat_class_and_partner.boat_class for boat_class_and_partner in self.values()]

        return most_common(list_of_boat_classes, BoatClass.create_empty())

    def most_common_partner(self) -> Cadet:
        list_of_partners = [boat_class_and_partner.partner_cadet for boat_class_and_partner in self.values()]

        return most_common(list_of_partners, Cadet.create_empty())

    def unique_list_of_boat_classes(self) -> ListOfBoatClasses:
        list_of_boat_classes = [boat_class_and_partner.boat_class for boat_class_and_partner in self.values()]
        return ListOfBoatClasses(list(set(list_of_boat_classes)))

    def is_in_boat_class_on_day(self, day: Day, boat_class: BoatClass):
        try:
            boat_class_and_partner = self.boat_class_and_partner_on_day(day)
        except MissingData:
            return False

        return boat_class_and_partner.boat_class == boat_class

    def sail_number_on_day(self, day: Day) -> str:
        try:
            boat_class_and_partner = self.boat_class_and_partner_on_day(day)
        except:
            return missing_data

        return boat_class_and_partner.sail_number

    def boat_class_on_day(self, day: Day) -> BoatClass:
        try:
            boat_class_and_partner = self.boat_class_and_partner_on_day(day)
        except:
            return no_boat_class

        return boat_class_and_partner.boat_class


    def partner_on_day(self, day: Day) -> [Cadet, object]:
        try:
            boat_class_and_partner = self.boat_class_and_partner_on_day(day)
        except:
            return NoPartnerCadetRequired

        return boat_class_and_partner.partner_cadet

    def boat_class_and_partner_on_day(self, day: Day) -> BoatClassAndPartnerAtEventOnDay:
        boat_class_and_partner = self.get(day, None)
        if boat_class_and_partner is None:
            raise MissingData

        return boat_class_and_partner

    def remove_boat_and_partner_on_day(self, day: Day):
        try:
            self.pop(day)
        except:
            pass

class ListOfCadetBoatClassAndPartnerAtEventOnDay(
    List[CadetBoatClassAndPartnerAtEventOnDay]
):
    @classmethod
    def from_list_of_cadets_at_event_with_boat_class_and_partner_with_ids(
        cls,
        list_of_cadet_at_event_with_boat_class_and_partner_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
        list_of_cadets: ListOfCadets,
        list_of_boats: ListOfBoatClasses,
    ):
        return cls(
            [
                CadetBoatClassAndPartnerAtEventOnDay.from_cadet_at_event_with_boat_class_and_partner_with_ids(
                    cadet_at_event_with_boat_class_and_partner_with_ids,
                    list_of_cadets=list_of_cadets,
                    list_of_boats=list_of_boats,
                )
                for cadet_at_event_with_boat_class_and_partner_with_ids in list_of_cadet_at_event_with_boat_class_and_partner_with_ids
            ]
        )

    def list_of_valid_partners(self) -> ListOfCadets:
        return ListOfCadets([element.partner_cadet for element in self if valid_partnership_given_partner_cadet(element)])


    def unique_list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = [cadet_boat_class.cadet for cadet_boat_class in self]
        return ListOfCadets(list(set(list_of_cadets)))

    def dict_of_days_boat_class_and_partners_for_cadet(
        self, cadet: Cadet
    ) -> DictOfDaysBoatClassAndPartners:
        subset_for_cadet = self.subset_for_cadet(cadet)

        return DictOfDaysBoatClassAndPartners(
            [
                (
                    cadet_with_boat.day,
                    BoatClassAndPartnerAtEventOnDay(
                        boat_class=cadet_with_boat.boat_class,
                        partner_cadet=cadet_with_boat.partner_cadet,
                        sail_number=cadet_with_boat.sail_number,
                    ),
                )
                for cadet_with_boat in subset_for_cadet
            ]
        )

    def subset_for_cadet(
        self, cadet: Cadet
    ) -> "ListOfCadetBoatClassAndPartnerAtEventOnDay":
        return ListOfCadetBoatClassAndPartnerAtEventOnDay(
            [
                cadet_with_boat
                for cadet_with_boat in self
                if cadet_with_boat.cadet == cadet
            ]
        )

    def element_on_day_for_cadet(self, cadet: Cadet, day: Day) -> CadetBoatClassAndPartnerAtEventOnDay:
        list_of_elements = [element for element in self if element.cadet==cadet and element.day==day]
        if len(list_of_elements)>1:
            raise MultipleMatches
        elif len(list_of_elements)==0:
            return missing_data

        return list_of_elements[0]


class DictOfCadetsAndBoatClassAndPartners(Dict[Cadet, DictOfDaysBoatClassAndPartners]):
    def __init__(
        self,
        raw_dict: Dict[Cadet, DictOfDaysBoatClassAndPartners],
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
            list_of_boat_classes: ListOfBoatClasses,
        event: Event,
    ):
        super().__init__(raw_dict)
        self._list_of_cadets_at_event_with_boat_class_and_partners_with_ids = (
            list_of_cadets_at_event_with_boat_class_and_partners_with_ids
        )
        self._list_of_boat_classes = list_of_boat_classes
        self._event = event

    def create_two_handed_partnership(self,
        cadet: Cadet,
                                      new_two_handed_partner: Cadet, day: Day
    ):
        ### FIXME  WE ONLY UPDATE THE UNDERLYING DATA FOR NOW
        ## RATHER THAN, FOR NOW, IMPLEMENT THE COMPLEX LOGIC
        ## THIS DOES MEAN THE MODEL OF FLUSHING AND RELOADING HAS TO BE KEPT

        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.create_two_handed_partnership(
            cadet_id=cadet.id,
            new_two_handed_partner_id=new_two_handed_partner.id,
            day=day
        )

    def update_boat_info_for_updated_cadet_at_event(self, cadet_boat_class_and_partner_at_event_on_day: CadetBoatClassAndPartnerAtEventOnDay):
        ### FIXME: WE ONLY UPDATE THE UNDERLYING DATA FOR NOW
        ## RATHER THAN, FOR NOW, IMPLEMENT THE COMPLEX LOGIC
        ## THIS DOES MEAN THE MODEL OF FLUSHING AND RELOADING HAS TO BE KEPT

        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.update_boat_info_for_cadet_and_partner_at_event_on_day(
            CadetAtEventWithBoatClassAndPartnerWithIds(
                cadet_id=cadet_boat_class_and_partner_at_event_on_day.cadet.id,
                partner_cadet_id=cadet_boat_class_and_partner_at_event_on_day.partner_cadet_id(),
                boat_class_id=cadet_boat_class_and_partner_at_event_on_day.boat_class.id,
                sail_number=cadet_boat_class_and_partner_at_event_on_day.sail_number,
                day=cadet_boat_class_and_partner_at_event_on_day.day
            )
        )

    def as_list_of_cadets_boat_classes_and_partners_at_event_on_day(self) -> ListOfCadetBoatClassAndPartnerAtEventOnDay:
        new_list = []
        for cadet, dict_of_boat_class_and_partners in self.items():
            for day in dict_of_boat_class_and_partners.list_of_days:
                boat_class_and_partner = dict_of_boat_class_and_partners.boat_class_and_partner_on_day(day)
                new_list.append(
                    CadetBoatClassAndPartnerAtEventOnDay(
                        cadet=cadet,
                        day=day,
                        boat_class=boat_class_and_partner.boat_class,
                        partner_cadet=boat_class_and_partner.partner_cadet,
                        sail_number=boat_class_and_partner.sail_number
                    )
                )

            return ListOfCadetBoatClassAndPartnerAtEventOnDay(new_list)

    def unique_sorted_list_of_boat_classes_at_event(self) -> ListOfBoatClasses:
        boat_classes_for_cadets = [dict_of_days_and_boat_classes.unique_list_of_boat_classes() for dict_of_days_and_boat_classes in self.values()]
        boat_classes_across_cadets = flatten(boat_classes_for_cadets)

        sorted_list = [boat_class for boat_class in self.list_of_boat_classes if boat_class in boat_classes_across_cadets]

        return ListOfBoatClasses(sorted_list)

    def remove_cadet_from_event_and_return_messages(self, cadet: Cadet) -> List[str]:
        all_messages = []
        for day in self.event.weekdays_in_event():
            message = self.remove_cadet_from_event_on_day_and_return_message(cadet=cadet, day=day)
            all_messages.append(message)

        try:
            self.pop(cadet)
        except:
            pass

        return all_messages

    def remove_cadet_from_event_on_day_and_return_message(self, cadet: Cadet, day: Day) -> str:
        boat_classes_and_partners = self.boat_classes_and_partner_for_cadet(cadet)
        try:
            boat_classes_and_partner_on_day = boat_classes_and_partners.boat_class_and_partner_on_day(day)
        except MissingData:
            return ""

        if boat_classes_and_partner_on_day.has_partner:
            partner_cadet = boat_classes_and_partner_on_day.partner_cadet
            message = "Cadet %s was sailing with a partner; now they aren't sailing %s has no partner on %s" \
                % (cadet, partner_cadet, day)
            self.remove_two_handed_partner_link_from_existing_cadet_on_day(cadet=partner_cadet, day=day)
        else:
            message = ""

        boat_classes_and_partners.remove_boat_and_partner_on_day(day)

        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.clear_boat_details_from_existing_cadet_id(cadet_id=cadet.id, day=day)

        return message

    def remove_two_handed_partner_link_from_existing_cadet_on_day(self,
        cadet: Cadet, day: Day
    ):

        boat_classes_and_partners = self.boat_classes_and_partner_for_cadet(cadet)
        try:
            boat_classes_and_partner_on_day = boat_classes_and_partners.boat_class_and_partner_on_day(day)
        except MissingData:
            return

        boat_classes_and_partner_on_day.partner_cadet = NoPartnerAllocated
        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.remove_two_handed_partner_from_existing_cadet(cadet_id=cadet.id,
                                                                                                                         day=day)


    def boat_classes_and_partner_for_cadet(self, cadet: Cadet) -> DictOfDaysBoatClassAndPartners:
        boat_classes_and_partners_for_cadet =self.get(cadet, None)
        if boat_classes_and_partners_for_cadet is None:
            return DictOfDaysBoatClassAndPartners()
        return boat_classes_and_partners_for_cadet

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    @property
    def list_of_cadets_at_event_with_boat_class_and_partners_with_ids(
        self,
    ) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
        return self._list_of_cadets_at_event_with_boat_class_and_partners_with_ids

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_boat_classes(self)-> ListOfBoatClasses:
        return self._list_of_boat_classes

def compose_dict_of_cadets_and_boat_classes_and_partners(
    event_id: str,
    list_of_cadets: ListOfCadets,
    list_of_events: ListOfEvents,
    list_of_boat_classes: ListOfBoatClasses,
    list_of_cadets_at_event_with_boat_class_and_partners_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
) -> DictOfCadetsAndBoatClassAndPartners:
    event = list_of_events.object_with_id(event_id)

    raw_dict = compose_raw_dict_of_cadets_and_boat_classes_and_partners(
        list_of_cadets=list_of_cadets,
        list_of_boat_classes=list_of_boat_classes,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
    )

    return DictOfCadetsAndBoatClassAndPartners(
        raw_dict=raw_dict,
        event=event,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
        list_of_boat_classes=list_of_boat_classes
    )


def compose_raw_dict_of_cadets_and_boat_classes_and_partners(
    list_of_cadets: ListOfCadets,
    list_of_boat_classes: ListOfBoatClasses,
    list_of_cadets_at_event_with_boat_class_and_partners_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
) -> Dict[Cadet, DictOfDaysBoatClassAndPartners]:
    list_of_cadet_boat_classes_and_partners_at_event_on_day = ListOfCadetBoatClassAndPartnerAtEventOnDay.from_list_of_cadets_at_event_with_boat_class_and_partner_with_ids(
        list_of_cadet_at_event_with_boat_class_and_partner_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
        list_of_boats=list_of_boat_classes,
        list_of_cadets=list_of_cadets,
    )

    list_of_cadets_at_event = (
        list_of_cadet_boat_classes_and_partners_at_event_on_day.unique_list_of_cadets()
    )

    raw_dict = dict(
        [
            (
                cadet,
                list_of_cadet_boat_classes_and_partners_at_event_on_day.dict_of_days_boat_class_and_partners_for_cadet(
                    cadet
                ),
            )
            for cadet in list_of_cadets_at_event
        ]
    )

    return raw_dict
