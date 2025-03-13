from typing import Union

from app.data_access.store.object_store import ObjectStore

from app.backend.registration_data.identified_cadets_at_event import (
    cadet_at_event_given_row_id,
)
from app.objects.cadets import default_cadet
from app.objects.exceptions import missing_data
from app.objects.cadet_with_id_at_event import (
    get_sailor_attendance_selection_from_event_row,
)

from app.objects.events import Event
from app.data_access.configuration.field_list import (
    REGISTERED_BY_FIRST_NAME,
    VOLUNTEER_STATUS,
    ANY_OTHER_INFORMATION,
)
from app.data_access.configuration.field_list_groups import (
    NAME_KEY_IN_VOLUNTEER_FIELDS_DICT,
    AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT,
    WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT,
    DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT,
    SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT,
    FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT,
    LIST_OF_VOLUNTEER_FIELDS,
)
from app.objects.registration_data import RowInRegistrationData
from app.objects.relevant_information_for_volunteers import (
    RelevantInformationForVolunteer,
    RelevantInformationForVolunteerIdentification,
    RelevantInformationForVolunteerAvailability,
    RelevantInformationForVolunteerDetails,
    missing_relevant_information,
)
from app.objects.volunteers import Volunteer

NO_VOLUNTEER_IN_FORM = "NO_VOLUNTEER_IN_FORM"


def get_relevant_information_for_volunteer(
    object_store: ObjectStore,
    row_in_mapped_event: RowInRegistrationData,
    volunteer_index: int,
    event: Event,
) -> RelevantInformationForVolunteer:
    return RelevantInformationForVolunteer(
        identify=get_identification_information_for_volunteer(
            object_store=object_store,
            row_in_mapped_event=row_in_mapped_event,
            volunteer_index=volunteer_index,
            event=event,
        ),
        availability=get_availability_information_for_volunteer(
            row_in_mapped_event=row_in_mapped_event,
            volunteer_index=volunteer_index,
            event=event,
        ),
        details=get_details_information_for_volunteer(
            row_in_mapped_event=row_in_mapped_event, volunteer_index=volunteer_index
        ),
    )


def get_identification_information_for_volunteer(
    object_store: ObjectStore,
    row_in_mapped_event: RowInRegistrationData,
    volunteer_index: int,
    event: Event,
) -> RelevantInformationForVolunteerIdentification:
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    name_key = dict_of_fields_for_volunteer[NAME_KEY_IN_VOLUNTEER_FIELDS_DICT]

    try:
        cadet = cadet_at_event_given_row_id(
            object_store=object_store, event=event, row_id=row_in_mapped_event.row_id
        )
        if cadet is missing_data:
            raise
    except:
        ## Won't always have cadets maybe in the future
        cadet = default_cadet

    return RelevantInformationForVolunteerIdentification(
        cadet=cadet,
        passed_name=row_in_mapped_event.get_item(
            name_key, default=NO_VOLUNTEER_IN_FORM
        ),
        registered_by_firstname=row_in_mapped_event.get_item(
            REGISTERED_BY_FIRST_NAME, default=""
        ),
        self_declared_status=row_in_mapped_event.get_item(VOLUNTEER_STATUS, default=""),
        any_other_information=row_in_mapped_event.get_item(
            ANY_OTHER_INFORMATION, default=""
        ),
    )


def get_availability_information_for_volunteer(
    row_in_mapped_event: RowInRegistrationData, volunteer_index: int, event: Event
) -> RelevantInformationForVolunteerAvailability:
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    preferred_duties_key = dict_of_fields_for_volunteer[
        DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT
    ]
    same_or_different_key = dict_of_fields_for_volunteer[
        SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT
    ]

    cadet_availability = get_sailor_attendance_selection_from_event_row(
        event=event, row=row_in_mapped_event
    )  ## will cover all days

    volunteer_availability = get_availability_for_volunteer(
        row_in_mapped_event=row_in_mapped_event,
        volunteer_index=volunteer_index,
        event=event,
    )

    if volunteer_availability.is_empty():
        volunteer_availability = cadet_availability

    return RelevantInformationForVolunteerAvailability(
        cadet_availability=cadet_availability,
        volunteer_availablity=volunteer_availability,
        any_other_information=row_in_mapped_event.get_item(ANY_OTHER_INFORMATION, ""),
        preferred_duties=row_in_mapped_event.get_item(preferred_duties_key, ""),
        same_or_different=row_in_mapped_event.get_item(same_or_different_key, ""),
        row_status=row_in_mapped_event.registration_status,
    )


from app.objects.day_selectors import (
    DaySelector,
    create_day_selector_from_short_form_text_with_passed_days,
)


def get_availability_for_volunteer(
    row_in_mapped_event: RowInRegistrationData, volunteer_index: int, event: Event
) -> Union[DaySelector, object]:
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    day_available_key = dict_of_fields_for_volunteer[
        AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT
    ]
    weekend_available_key = dict_of_fields_for_volunteer[
        WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT
    ]

    weekend_available_text = row_in_mapped_event.get_item(weekend_available_key, "")
    day_available_text = row_in_mapped_event.get_item(day_available_key, "")

    days_in_event = event.days_in_event()

    if len(weekend_available_text) > 0:
        return create_day_selector_from_short_form_text_with_passed_days(
            weekend_available_text, days_in_event=days_in_event
        )
    elif len(day_available_text) > 0:
        return create_day_selector_from_short_form_text_with_passed_days(
            day_available_text, days_in_event=days_in_event
        )
    else:

        return DaySelector.create_empty()


def get_details_information_for_volunteer(
    row_in_mapped_event: RowInRegistrationData, volunteer_index: int
) -> RelevantInformationForVolunteerDetails:
    dict_of_fields_for_volunteer = LIST_OF_VOLUNTEER_FIELDS[volunteer_index]
    food_preference_key = dict_of_fields_for_volunteer[
        FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT
    ]

    return RelevantInformationForVolunteerDetails(
        food_preference=row_in_mapped_event.get_item(food_preference_key, ""),
        any_other_information=row_in_mapped_event.get_item(ANY_OTHER_INFORMATION, ""),
    )


no_volunteer_in_position_at_form = object()


def get_volunteer_from_relevant_information(
    relevant_information_for_volunteer: RelevantInformationForVolunteer,
) -> Volunteer:
    if relevant_information_for_volunteer is missing_relevant_information:
        return missing_relevant_information
    relevant_information_for_id = relevant_information_for_volunteer.identify
    if minimum_volunteer_information_is_missing(relevant_information_for_id):
        return missing_relevant_information

    inferred_volunteer = infer_volunteer_from_provided_information(
        relevant_information_for_id
    )
    if inferred_volunteer is NO_VOLUNTEER_IN_FORM:
        return missing_relevant_information

    return inferred_volunteer


def infer_volunteer_from_provided_information(
    relevant_information_for_id: RelevantInformationForVolunteerIdentification,
) -> Volunteer:
    passed_name = relevant_information_for_id.passed_name

    if passed_name == "":
        ## completely empty, not going to guess as will cause problems
        return NO_VOLUNTEER_IN_FORM

    split_name = relevant_information_for_id.passed_name.split(" ")
    first_name = split_name[0]
    if len(split_name) > 1:  ## OK they have put their full name not just first name
        surname = split_name[-1]  ## exclude first and middle names
    else:
        ## Only put first name, assume same surname as cadet
        surname = relevant_information_for_id.cadet_surname

    return Volunteer(
        first_name=first_name.strip().title(), surname=surname.strip().title()
    )


def minimum_volunteer_information_is_missing(
    relevant_information_for_id: RelevantInformationForVolunteerIdentification,
):
    return relevant_information_for_id.passed_name == NO_VOLUNTEER_IN_FORM
