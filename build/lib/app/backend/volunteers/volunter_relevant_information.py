from app.backend.cadets import cadet_from_id
from app.objects.constants import missing_data
from app.objects.day_selectors import DaySelector, any_day_selector_from_short_form_text
from app.objects.field_list import LIST_OF_VOLUNTEER_FIELDS, NAME_KEY_IN_VOLUNTEER_FIELDS_DICT, \
    REGISTERED_BY_FIRST_NAME, VOLUNTEER_STATUS, ANY_OTHER_INFORMATION, AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT, \
    WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT, DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT, \
    SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT, FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT
from app.objects.food import guess_food_requirements_from_food_field
from app.objects.OLDmaster_event import RowInMasterEvent
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer, \
    RelevantInformationForVolunteerIdentification, RelevantInformationForVolunteerAvailability, \
    RelevantInformationForVolunteerDetails
from app.objects.volunteers import Volunteer
from app.objects.volunteers_at_event import VolunteerAtEvent


def get_relevant_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteer:
    return RelevantInformationForVolunteer(
        identify = get_identification_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index),
        availability=get_availability_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index),
        details=get_details_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index)
    )


def get_identification_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerIdentification:
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    name_key = dict_of_fields_for_volunteer[NAME_KEY_IN_VOLUNTEER_FIELDS_DICT]
    cadet_id=row_in_master_event.cadet_id
    cadet =cadet_from_id(cadet_id)

    return RelevantInformationForVolunteerIdentification(
        cadet_id=cadet_id,
        cadet_surname=cadet.surname,
        passed_name=row_in_master_event.get_item(name_key),
        registered_by_firstname= row_in_master_event.get_item(REGISTERED_BY_FIRST_NAME),
        self_declared_status=row_in_master_event.get_item(VOLUNTEER_STATUS),
        any_other_information=row_in_master_event.get_item(ANY_OTHER_INFORMATION)
    )


def get_availability_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerAvailability:

    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    day_available_key = dict_of_fields_for_volunteer[AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT]
    weekend_available_key = dict_of_fields_for_volunteer[WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT]
    preferred_duties_key = dict_of_fields_for_volunteer[DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT]
    same_or_different_key = dict_of_fields_for_volunteer[SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT]

    return RelevantInformationForVolunteerAvailability(
        cadet_availability=row_in_master_event.attendance,
        day_availability=row_in_master_event.get_item(day_available_key, missing_data),
        weekend_availability=row_in_master_event.get_item(weekend_available_key,missing_data),
        any_other_information=row_in_master_event.get_item(ANY_OTHER_INFORMATION),
        preferred_duties=row_in_master_event.get_item(preferred_duties_key),
        same_or_different=row_in_master_event.get_item(same_or_different_key)
    )


def get_details_information_for_volunteer(row_in_master_event: RowInMasterEvent, volunteer_index: int) -> RelevantInformationForVolunteerDetails:

    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    food_preference_key = dict_of_fields_for_volunteer[FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT]

    return RelevantInformationForVolunteerDetails(
        food_preference=row_in_master_event.get_item(food_preference_key),
        any_other_information=row_in_master_event.get_item(ANY_OTHER_INFORMATION)
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
    food_requirements = guess_food_requirements_from_food_field(relevant_information.details.food_preference)
    ## availability can be changed and food at next stage

    volunteer_at_event = VolunteerAtEvent(volunteer_id=volunteer_id,
                                          availablity=availability,
                                          list_of_associated_cadet_id=[cadet_id],
                                          preferred_duties=relevant_information.availability.preferred_duties,
                                          same_or_different=relevant_information.availability.same_or_different,
                                          any_other_information=relevant_information.details.any_other_information,
                                          food_requirements=food_requirements)

    return volunteer_at_event


def suggested_volunteer_availability(relevant_information: RelevantInformationForVolunteerAvailability)-> DaySelector:
    day_availability = relevant_information.day_availability
    weekend_availability = relevant_information.weekend_availability
    cadet_availability = relevant_information.cadet_availability

    if day_availability is not missing_data:
        return any_day_selector_from_short_form_text(day_availability)
    elif weekend_availability is not missing_data:
        return any_day_selector_from_short_form_text(weekend_availability)
    elif cadet_availability is not missing_data:
        return cadet_availability
    else:
        raise Exception("No availability information at all for volunteer!")
