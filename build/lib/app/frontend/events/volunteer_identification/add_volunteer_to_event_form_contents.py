from typing import Union, List

from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, HelpButton
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.forms.form_utils import get_availability_checkbox
from app.backend.registration_data.identified_volunteers_at_event import (
    get_list_of_relevant_information_for_volunteer_in_registration_data,
)
from app.backend.registration_data.cadet_and_volunteer_connections_at_event import (
    get_list_of_active_associated_cadets_in_mapped_event_data_given_identified_volunteer,
)
from app.objects.abstract_objects.abstract_form import textInput, Form
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    _______________,
)
from app.objects.exceptions import missing_data
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import (
    RelevantInformationForVolunteer,
    ListOfRelevantInformationForVolunteer,
    missing_relevant_information,
)
from app.objects.volunteers import Volunteer

AVAILABILITY = "availability"
ANY_OTHER_INFORMATION = "any_other_information"
PREFERRED_DUTIES = "preferred_duties"
SAME_OR_DIFFERENT = "same_or_different"
NOTES = "Notes"


def display_form_to_confirm_volunteer_details(
    interface: abstractInterface, volunteer: Volunteer, event: Event
) -> Form:

    list_of_relevant_information = (
        get_list_of_relevant_information_for_volunteer_in_registration_data(
            object_store=interface.object_store,
            volunteer=volunteer,
            event=event,
        )
    )

    header_text = get_header_text(event=event, volunteer=volunteer, interface=interface)

    any_other_information_text = get_any_other_information_text(
        list_of_relevant_information=list_of_relevant_information
    )
    status_text = get_any_self_declared_status_text(
        list_of_relevant_information=list_of_relevant_information
    )

    preferred_duties_text = get_preferred_duties_text(
        list_of_relevant_information=list_of_relevant_information
    )
    preferred_duties_input = get_preferred_duties_input(
        list_of_relevant_information=list_of_relevant_information
    )

    same_or_different_text = get_same_or_different_text_and_input_box(
        list_of_relevant_information=list_of_relevant_information
    )
    same_or_different_input = get_same_or_different_input(
        list_of_relevant_information=list_of_relevant_information
    )

    available_text = get_availablity_text(
        list_of_relevant_information=list_of_relevant_information
    )
    available_checkbox = (
        get_availability_checkbox_for_volunteer_at_event_based_on_relevant_information(
            list_of_relevant_information=list_of_relevant_information, event=event
        )
    )

    notes_input = get_notes_input_for_volunteer_at_event(list_of_relevant_information)

    return Form(
        ListOfLines(
            [
                button_bar,
                _______________,
                _______________,
                header_text,
                _______________,
                _______________,
                status_text,
                _______________,
                _______________,
                available_text.add_Lines(),
                _______________,
                available_checkbox,
                _______________,
                _______________,
                any_other_information_text,
                _______________,
                _______________,
                preferred_duties_text.add_Lines(),
                _______________,
                preferred_duties_input,
                _______________,
                _______________,
                same_or_different_text.add_Lines(),
                same_or_different_input,
                _______________,
                notes_input,
                _______________,
                Line([Button(SAVE_CHANGES), Button(DO_NOT_ADD_VOLUNTEER_LABEL)]),
            ]
        )
    )


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


button_bar = ButtonBar([HelpButton("resolve_volunteer_registration_issues")])


def get_cadet_names_text_given_identified_volunteer(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> str:
    cadet_names = get_list_of_active_associated_cadet_names_in_mapped_event_data_given_identified_volunteer(
        interface=interface, event=event, volunteer=volunteer
    )

    if len(cadet_names) == 0:
        cadet_names_text = "(No active registered sailors - must all be cancelled)"
    else:
        cadet_names_text = ", ".join(cadet_names)

    return cadet_names_text


def get_list_of_active_associated_cadet_names_in_mapped_event_data_given_identified_volunteer(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> List[str]:
    list_of_cadets = get_list_of_active_associated_cadets_in_mapped_event_data_given_identified_volunteer(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )
    return list_of_cadets.list_of_names()


def get_availablity_text(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    all_available = ListOfLines()
    for relevant_information in list_of_relevant_information:
        all_available = all_available + get_availablity_text_for_single_entry(
            relevant_information=relevant_information
        )

    return all_available


def get_availablity_text_for_single_entry(
    relevant_information: RelevantInformationForVolunteer,
) -> ListOfLines:
    if relevant_information is missing_relevant_information:
        return ListOfLines("")

    cadet_name = get_cadet_name_from_relevant_information(
        relevant_information=relevant_information
    )
    availability_info = relevant_information.availability

    if availability_info.volunteer_availablity.is_empty():
        volunteer_availability = "No availability for volunteer in form"
    else:
        volunteer_availability = (
            "In form volunteer said they were available on %s"
            % str(availability_info.volunteer_availablity.days_available_as_str())
        )

    cadet_availabilty = "Cadet registered in form available on %s" % str(
        availability_info.cadet_availability.days_available_as_str()
    )

    available_text = ListOfLines(
        [
            "Availability for volunteer in form when registered with sailor %s:"
            % cadet_name,
            "    - Sailor available: %s" % cadet_availabilty,
            "    - Volunteer available: %s" % volunteer_availability,
        ]
    )

    return available_text


def get_cadet_name_from_relevant_information(
    relevant_information: RelevantInformationForVolunteer,
) -> str:
    NO_CADET = "(no cadet)"
    if relevant_information is missing_relevant_information:
        return NO_CADET
    cadet = relevant_information.identify.cadet
    if cadet is missing_data:
        return NO_CADET

    return cadet.name


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

    for relevant_information in list_of_relevant_information:
        availabilty = relevant_information.availability.volunteer_availablity
        if availabilty.is_empty():
            continue
        else:
            return availabilty

    availabilty = event.day_selector_for_days_in_event()

    return availabilty


def get_any_other_information_text(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    list_of_other_information = ListOfLines(
        ["Other information in form: (for each registration)"]
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
        ["Self declared status in form: (for each registration)"]
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
        ["Preferred duties in form (for each registration):"]
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


def get_same_or_different_text_and_input_box(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfLines:
    same_or_different_text = get_same_or_different_text(list_of_relevant_information)
    if same_or_different_text is None:
        return ListOfLines([""])

    same_or_different_input_line = get_same_or_different_input(
        list_of_relevant_information
    )
    same_or_different_input_header = (
        "Same or different duties in form (for each registration):"
    )

    return ListOfLines(
        [same_or_different_input_header]
        + same_or_different_text
        + [same_or_different_input_line]
    ).add_Lines()


def get_same_or_different_text(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> Union[list, None]:
    list_of_same_or_different = []

    for relevant_information in list_of_relevant_information:
        try:
            same_or_different_text = relevant_information.availability.same_or_different
            if len(same_or_different_text) == 0:
                continue
            list_of_same_or_different.append(Line(same_or_different_text))
        except:
            continue

    if len(list_of_same_or_different) == 0:
        return None

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


SAVE_CHANGES = "Save changes"
DO_NOT_ADD_VOLUNTEER_LABEL = "This volunteer is not available at this event"
save_button = Button(SAVE_CHANGES)
do_not_add_volunteer = Button(DO_NOT_ADD_VOLUNTEER_LABEL)
