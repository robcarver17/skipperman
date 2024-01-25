from dataclasses import dataclass

from app.objects.day_selectors import DaySelector, any_day_selector_from_short_form_text
from app.objects.field_list import LIST_OF_VOLUNTEER_FIELDS, REGISTERED_BY_FIRST_NAME, REGISTERED_BY_LAST_NAME, VOLUNTEER_STATUS,\
    DAYS_ATTENDING, VOLUNTEER_STATUS, NAME_KEY_IN_VOLUNTEER_FIELDS_DICT, FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT, DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT, AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT, WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT,SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT, ANY_OTHER_INFORMATION

from app.objects.master_event import RowInMasterEvent
from app.backend.cadets import get_list_of_cadets, get_cadet_from_id

from app.objects.constants import missing_data
from app.objects.volunteers import Volunteer
from app.objects.volunteers_at_event import VolunteerAtEvent

list_of_cadets = get_list_of_cadets()## won't change here

@dataclass
class RelevantInformationForVolunteerIdentification:
    passed_name: str
    cadet_id: str
    cadet_surname: str
    registered_by_firstname: str
    self_declared_status: str
    any_other_information: str ## information only - double counted as required twice


@dataclass
class RelevantInformationForVolunteerDetails: ##copied across
    food_preference: str
    any_other_information: str ## information only - double counted as required twice

@dataclass
class RelevantInformationForVolunteerAvailability:
    day_availability: str
    weekend_availability: str
    cadet_availability: DaySelector
    preferred_duties: str ## information only
    same_or_different: str ## information only
    any_other_information: str ## information only - double counted as required twice


@dataclass
class RelevantInformationForVolunteer:
    identify: RelevantInformationForVolunteerIdentification
    availability: RelevantInformationForVolunteerAvailability
    details: RelevantInformationForVolunteerDetails


def get_relevant_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteer:
    return RelevantInformationForVolunteer(
        identify = get_identification_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index),
        availability=get_availability_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index),
        details=get_details_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index)
    )


def get_identification_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerIdentification:
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    name_key = dict_of_fields_for_volunteer[NAME_KEY_IN_VOLUNTEER_FIELDS_DICT]
    data_in_row = row_in_master_event.data_in_row
    cadet_id=row_in_master_event.cadet_id
    cadet = get_cadet_from_id(id=cadet_id, list_of_cadets=list_of_cadets)


    return RelevantInformationForVolunteerIdentification(
        cadet_id=cadet_id,
        cadet_surname=cadet.surname,
        passed_name=data_in_row.get(name_key, ""),
        registered_by_firstname=  data_in_row.get(REGISTERED_BY_FIRST_NAME, ''),
        self_declared_status=data_in_row.get(VOLUNTEER_STATUS, ""),
        any_other_information=data_in_row.get(ANY_OTHER_INFORMATION, "")
    )


def get_availability_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerAvailability:
    data_in_row = row_in_master_event.data_in_row
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    day_available_key = dict_of_fields_for_volunteer[AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT]
    weekend_available_key = dict_of_fields_for_volunteer[WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT]
    preferred_duties_key = dict_of_fields_for_volunteer[DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT]
    same_or_different_key = dict_of_fields_for_volunteer[SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT]

    return RelevantInformationForVolunteerAvailability(
        cadet_availability=data_in_row.get(DAYS_ATTENDING, missing_data),
        day_availability=data_in_row.get(day_available_key, missing_data),
        weekend_availability=data_in_row.get(weekend_available_key,missing_data),
        any_other_information=data_in_row.get(ANY_OTHER_INFORMATION, ""),
        preferred_duties=data_in_row.get(preferred_duties_key, ""),
        same_or_different=data_in_row.get(same_or_different_key, "")

    )


def get_details_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerDetails:
    data_in_row = row_in_master_event.data_in_row
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    food_preference_key = dict_of_fields_for_volunteer[FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT]

    return RelevantInformationForVolunteerDetails(
        food_preference=data_in_row.get(food_preference_key,''),
        any_other_information=data_in_row.get(ANY_OTHER_INFORMATION, "")
    )




def get_volunteer_from_relevant_information(relevant_information_for_id: RelevantInformationForVolunteerIdentification) -> Volunteer:
    first_name = ""
    surname = ""
    if relevant_information_for_id.passed_name!="":
        split_name =relevant_information_for_id.passed_name.split(" ")
        first_name = split_name[0]
        if len(split_name)>1: ## put their full name not just first name
            surname = split_name[-1] ## exclude first and middle names

    if surname =="": ## assume same as cadet
        surname = relevant_information_for_id.cadet_surname

    if first_name=="": ## assume it's who registered
        first_name = relevant_information_for_id.registered_by_firstname

    return Volunteer(first_name=first_name, surname=surname)

def get_volunteer_at_event_from_relevant_information(relevant_information: RelevantInformationForVolunteer,
                                                     cadet_id: str, volunteer_id: str) -> VolunteerAtEvent:
    availability = suggested_volunteer_availability(relevant_information.availability)
    ## availability can be changed and food at next stage

    volunteer_at_event = VolunteerAtEvent(volunteer_id=volunteer_id,
                                          availablity=availability,
                                          list_of_associated_cadet_id=[cadet_id],
                                          preferred_duties=relevant_information.availability.preferred_duties,
                                          same_or_different=relevant_information.availability.same_or_different,
                                          any_other_information=relevant_information.details.any_other_information)

    return volunteer_at_event

def suggested_volunteer_availability(relevant_information: RelevantInformationForVolunteerAvailability)-> DaySelector:
    day_availability = relevant_information.day_availability
    weekend_availability = relevant_information.weekend_availability
    cadet_availability = relevant_information.cadet_availability

    if len(day_availability)>0:
        return any_day_selector_from_short_form_text(day_availability)
    elif len(weekend_availability)>0:
        return any_day_selector_from_short_form_text(weekend_availability)
    else:
        return cadet_availability


