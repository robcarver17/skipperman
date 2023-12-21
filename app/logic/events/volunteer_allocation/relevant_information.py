from dataclasses import dataclass

from app.objects.day_selectors import DaySelector
from app.objects.field_list import LIST_OF_VOLUNTEER_FIELDS, REGISTERED_BY_FIRST_NAME, REGISTERED_BY_LAST_NAME, \
    DAYS_ATTENDING
from app.objects.master_event import RowInMasterEvent
from app.logic.cadets.backend import get_cadet_from_id
from app.logic.cadets.backend import get_list_of_cadets

from app.objects.constants import missing_data

list_of_cadets = get_list_of_cadets()## won't change here
@dataclass
class RelevantInformationForVolunteerIdentification:
    passed_name: str
    cadet_id: str
    cadet_surname: str
    registered_by_firstname: str
    self_declared_status: str


@dataclass
class RelevantInformationForVolunteerDetails: ##copied across
    preferred_duties: str ## information only
    same_or_different: str ## information only
    food_preference: str ## can be edited
    self_declared_status: str ## information only - double counted as required twice


@dataclass
class RelevantInformationForVolunteerAvailability:
    day_availability: str
    weekend_availability: str
    cadet_availability: DaySelector


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
    name_key = dict_of_fields_for_volunteer['NAME']
    data_in_row = row_in_master_event.data_in_row
    cadet_id=row_in_master_event.cadet_id
    cadet = get_cadet_from_id(id=cadet_id, list_of_cadets=list_of_cadets)

    return RelevantInformationForVolunteerIdentification(
        cadet_id=cadet_id,
        cadet_surname=cadet.surname,
        passed_name=data_in_row.get(name_key, ""),
        registered_by_firstname=  data_in_row.get(REGISTERED_BY_FIRST_NAME, ''),
        self_declared_status=data_in_row.get('VOLUNTEER_STATUS', "")
    )


def get_availability_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerAvailability:
    data_in_row = row_in_master_event.data_in_row
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    day_available_key = dict_of_fields_for_volunteer['AVAILABILITY']
    weekend_available_key = dict_of_fields_for_volunteer['WEEKEND_AVAILABILITY']
    return RelevantInformationForVolunteerAvailability(
        cadet_availability=data_in_row.get(DAYS_ATTENDING, missing_data),
        day_availability=data_in_row.get(day_available_key, missing_data),
        weekend_availability=data_in_row.get(weekend_available_key,missing_data),
    )


def get_details_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerDetails:
    data_in_row = row_in_master_event.data_in_row
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    food_preference_key = dict_of_fields_for_volunteer['FOOD_PREFERENCE']
    same_or_different_key = dict_of_fields_for_volunteer['SAME_OR_VARIED']
    preferred_duties = dict_of_fields_for_volunteer['DUTIES']

    return RelevantInformationForVolunteerDetails(
        food_preference=data_in_row.get(food_preference_key,''),
        same_or_different=data_in_row.get(same_or_different_key,''),
        preferred_duties=data_in_row.get(preferred_duties,''),
        self_declared_status = data_in_row.get('VOLUNTEER_STATUS', "")
    )


def suggested_volunteer_availability(self, relevant_information: RelevantInformationForVolunteerAvailability)-> DaySelector:
    pass
