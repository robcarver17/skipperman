from typing import Union, List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.cadets import cadet_name_from_id
from app.frontend.forms.form_utils import get_availability_checkbox
from app.OLD_backend.volunteers.volunteers import (
    are_all_cadet_ids_in_list_already_connection_to_volunteer,
)
from app.OLD_backend.volunteers.volunteer_allocation import (
    get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet,
)
from app.OLD_backend.volunteers.volunter_relevant_information import (
    suggested_volunteer_availability,
)
from app.objects.abstract_objects.abstract_form import checkboxInput, textInput
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.exceptions import missing_data
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects_OLD.relevant_information_for_volunteers import (
    RelevantInformationForVolunteer,
    ListOfRelevantInformationForVolunteer,
    missing_relevant_information,
)
from app.objects.volunteers import Volunteer


AVAILABILITY = "availability"
MAKE_CADET_CONNECTION = "connection"
ANY_OTHER_INFORMATION = "any_other_information"
PREFERRED_DUTIES = "preferred_duties"
SAME_OR_DIFFERENT = "same_or_different"
NOTES = "Notes"


def get_header_text(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> Line:
    volunteer_name = volunteer.name
    cadet_names_text = get_cadet_names_text_given_identified_volunteer(
        interface=interface, event=event, volunteer=volunteer
    )
    header_text = (
        "Details for volunteer %s - related to following cadets at event: %s"
        % (volunteer_name, cadet_names_text)
    )

    return Line(header_text)


def get_cadet_names_text_given_identified_volunteer(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> str:
    cadet_names = get_list_of_active_associated_cadet_names_in_mapped_event_data_given_identified_volunteer(
        interface=interface, event=event, volunteer=volunteer
    )

    if len(cadet_names) == 0:
        cadet_names_text = "(No active cadets - must all be cancelled)"
    else:
        cadet_names_text = ", ".join(cadet_names)

    return cadet_names_text


def get_list_of_active_associated_cadet_names_in_mapped_event_data_given_identified_volunteer(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> List[str]:
    list_of_cadet_ids = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        volunteer_id=volunteer.id, event=event, interface=interface
    )
    cadet_names = [
        cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        for cadet_id in list_of_cadet_ids
    ]

    return cadet_names


def get_connection_checkbox(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> Union[checkboxInput, str]:
    list_of_cadet_ids = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        interface=interface, volunteer_id=volunteer.id, event=event
    )

    already_all_connected = are_all_cadet_ids_in_list_already_connection_to_volunteer(
        data_layer=interface.data, volunteer=volunteer, list_of_cadet_ids=list_of_cadet_ids
    )

    if already_all_connected:
        return ""

    dict_of_labels = dict(
        [
            (cadet_id, cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id))
            for cadet_id in list_of_cadet_ids
        ]
    )
    dict_of_checked = dict(
        [(cadet_id, True) for cadet_id in list_of_cadet_ids]
    )  ## we assume we want to connect by default

    connection_checkbox = checkboxInput(
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
        input_name=MAKE_CADET_CONNECTION,
        input_label="Tick to permanently connect cadet with volunteer in main volunteer list (leave blank if not usually connected):",
    )

    return connection_checkbox


def get_availablity_text(
    interface: abstractInterface,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    all_available = ListOfLines()
    for relevant_information in list_of_relevant_information:
        all_available = all_available + get_availablity_text_for_single_entry(
            interface=interface, relevant_information=relevant_information
        )

    return all_available


def get_availablity_text_for_single_entry(
    interface: abstractInterface, relevant_information: RelevantInformationForVolunteer
) -> ListOfLines:
    if relevant_information is missing_relevant_information:
        return ListOfLines("")

    cadet_name = get_cadet_name_from_relevant_information(
        interface=interface, relevant_information=relevant_information
    )
    availability_info = relevant_information.availability
    available_text = ListOfLines(
        [
            "Availability for volunteer in form when registered with cadet %s"
            % cadet_name
        ]
    )
    if availability_info.day_availability is not missing_data:
        available_text.append(
            "- In form said they were available on %s "
            % availability_info.day_availability
        )
    elif availability_info.weekend_availability is not missing_data:
        available_text.append(
            "- In form said they were available on %s "
            % availability_info.weekend_availability
        )
    else:
        available_text.append(
            "- Cadet registered in form for %s"
            % str(availability_info.cadet_availability)
        )

    available_text.append("")

    return available_text


def get_cadet_name_from_relevant_information(
    interface: abstractInterface, relevant_information: RelevantInformationForVolunteer
) -> str:
    NO_CADET = "(no cadet)"
    if relevant_information is missing_relevant_information:
        return NO_CADET
    cadet_id = relevant_information.identify.cadet_id
    if cadet_id is missing_data:
        return NO_CADET

    cadet_name = cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)

    return cadet_name


def get_availability_checkbox_for_volunteer_at_event_based_on_relevant_information(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer, event: Event
):
    availability = first_valid_availability(list_of_relevant_information, event=event)
    return get_availability_checkbox(
        availability=availability,
        event=event,
        input_name=AVAILABILITY,
        input_label="Confirm availability for volunteer (leave all blank if not volunteering at all):",
        include_all=True,
    )


def first_valid_availability(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer, event: Event
) -> DaySelector:
    availabilty = event.day_selector_with_covered_days()

    for relevant_information in list_of_relevant_information:
        try:
            availabilty = suggested_volunteer_availability(
                relevant_information.availability
            )
            break
        except:
            continue

    if len(availabilty.days_available()) == 0:
        availabilty = event.day_selector_with_covered_days()

    return availabilty


def get_any_other_information_text(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    list_of_other_information = ListOfLines(
        ["Other information in form: (for each cadet entered with)"]
    )
    for relevant_information in list_of_relevant_information:
        try:
            other_information = relevant_information.details.any_other_information
            if len(other_information) == 0:
                continue
            list_of_other_information.append(Line(other_information))
        except:
            pass

    if len(list_of_other_information) == 1:
        return ListOfLines([""])

    return list_of_other_information


def get_any_self_declared_status_text(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    list_of_self_declared = ListOfLines(
        ["Self declared status in form: (for each cadet entered with)"]
    )
    for relevant_information in list_of_relevant_information:
        try:
            self_declared = relevant_information.identify.self_declared_status
            if len(self_declared) == 0:
                continue
            list_of_self_declared.append(Line(self_declared))
        except:
            pass

    if len(list_of_self_declared) == 0:
        return ListOfLines([""])

    return list_of_self_declared


def get_preferred_duties_text(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    list_of_preferred_duties = ListOfLines(
        ["Preferred duties in form (for each cadet registered with):"]
    )
    for relevant_information in list_of_relevant_information:
        try:
            duties = relevant_information.availability.preferred_duties
            if len(duties) == 0:
                continue
            list_of_preferred_duties.append(Line(duties))
        except:
            continue

    if len(list_of_preferred_duties) == 1:
        return ListOfLines([""])

    return list_of_preferred_duties


def get_preferred_duties_input(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> textInput:
    return textInput(
        input_name=PREFERRED_DUTIES,
        input_label="Enter preferred duties",
        value=first_valid_preferred_duties(list_of_relevant_information),
    )


def first_valid_preferred_duties(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    for relevant_information in list_of_relevant_information:
        try:
            duties = relevant_information.availability.preferred_duties
            if len(duties) == 0:
                continue
            return relevant_information.availability.preferred_duties
        except:
            continue

    return ""


def get_same_or_different_text(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    list_of_same_or_different = ListOfLines(
        ["Same or different duties in form (for each cadet registered with):"]
    )
    for relevant_information in list_of_relevant_information:
        try:
            same_or_different_text = relevant_information.availability.same_or_different
            if len(same_or_different_text) == 0:
                continue
            list_of_same_or_different.append(Line(same_or_different_text))
        except:
            continue

    if len(list_of_same_or_different) == 1:
        return ListOfLines([""])

    return list_of_same_or_different


def get_same_or_different_input(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> textInput:
    return textInput(
        input_name=SAME_OR_DIFFERENT,
        input_label="Enter same or different preference",
        value=first_valid_same_or_different(list_of_relevant_information),
    )


def get_notes_input_for_volunteer_at_event(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> textInput:
    return textInput(
        input_name=NOTES,
        input_label="Enter any notes about volunteer (can be edited later)",
        value="",
    )


def first_valid_same_or_different(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    for relevant_information in list_of_relevant_information:
        try:
            same_or_different_text = relevant_information.availability.same_or_different
            if len(same_or_different_text) == 0:
                continue

            return same_or_different_text
        except:
            continue

    return ""
