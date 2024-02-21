from typing import List, Union

from app.backend.cadets import cadet_name_from_id, cadet_from_id
from app.backend.form_utils import  get_availability_checkbox
from app.backend.volunteers.volunteers import is_cadet_already_connected_to_volunteer_in_volunteer_list
from app.backend.volunteers.volunteer_allocation import get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet
from app.backend.volunteers.volunter_relevant_information import suggested_volunteer_availability
from app.objects.abstract_objects.abstract_form import checkboxInput, textInput
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.constants import missing_data
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer
from app.objects.volunteers import Volunteer


AVAILABILITY = "availability"
MAKE_CADET_CONNECTION = "connection"
ANY_OTHER_INFORMATION = "any_other_information"
PREFERRED_DUTIES= "preferred_duties"
SAME_OR_DIFFERENT = "same_or_different"

def get_header_text(event: Event, volunteer: Volunteer) -> Line:
    list_of_cadet_ids = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(volunteer_id=volunteer.id,
                                                                                                                      event=event)
    cadet_names = [cadet_name_from_id(cadet_id) for cadet_id in list_of_cadet_ids]
    volunteer_name = volunteer.name
    if len(cadet_names)==0:
        cadet_names_text = "(No active cadets - must all be cancelled)"
    else:
        cadet_names_text = ", ".join(cadet_names)

    header_text = "Details for volunteer %s - related to following cadets at event: %s" % (volunteer_name, cadet_names_text)

    return Line(header_text)


def get_connection_checkbox(event: Event, volunteer: Volunteer) -> Union[checkboxInput, str]:
    list_of_cadet_ids = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(volunteer_id=volunteer.id,
                                                                                                                      event=event)

    list_of_already_connected = [is_cadet_already_connected_to_volunteer_in_volunteer_list(volunteer=volunteer, cadet_id=cadet_id) for cadet_id in list_of_cadet_ids]

    if all(list_of_already_connected):
        return ""

    connection_checkbox = checkboxInput(
        dict_of_labels=dict([(cadet_id,cadet_name_from_id(cadet_id)) for cadet_id in list_of_cadet_ids]),
        dict_of_checked=dict([(cadet_id,True) for cadet_id in list_of_cadet_ids]),
        input_name=MAKE_CADET_CONNECTION,
        input_label="Tick to permanently connect cadet with volunteer in main volunteer list (leave blank if not usually connected):"
    )

    return connection_checkbox






def get_availablity_text( list_of_relevant_information: List[RelevantInformationForVolunteer]) -> ListOfLines:
    all_available = ListOfLines()
    for relevant_information in list_of_relevant_information:
        all_available = all_available+get_availablity_text_for_single_entry(relevant_information)

    return all_available

def get_availablity_text_for_single_entry(relevant_information: RelevantInformationForVolunteer) -> ListOfLines:
    cadet_name = get_cadet_name_from_relevant_information(relevant_information)
    availability_info = relevant_information.availability
    available_text = ListOfLines(["Availability for volunteer in form when registered with cadet %s" % cadet_name])
    if availability_info.day_availability is not missing_data:
        available_text.append("- In form said they were available on %s " % availability_info.day_availability)
    elif availability_info.weekend_availability is not missing_data:
        available_text.append("- In form said they were available on %s " % availability_info.weekend_availability)
    else:
        available_text.append("- Cadet registered in form for %s" % str(availability_info.cadet_availability))

    available_text.append("")

    return available_text

def get_cadet_name_from_relevant_information(relevant_information: RelevantInformationForVolunteer) -> str:
    cadet_id = relevant_information.identify.cadet_id
    if cadet_id is missing_data:
        cadet_name = "(no cadet)"
    else:
        cadet_name = cadet_name_from_id(cadet_id)

    return cadet_name

def get_availability_checkbox_for_volunteer_at_event_based_on_relevant_information(list_of_relevant_information: List[RelevantInformationForVolunteer], event: Event):
    relevant_information_to_use = list_of_relevant_information[0]
    availability = suggested_volunteer_availability(relevant_information_to_use.availability)
    return get_availability_checkbox(availability=availability,
                                     event=event,
                                     input_name=AVAILABILITY,
                                     input_label="Confirm availability for volunteer:")


def get_any_other_information_text(list_of_relevant_information: List[RelevantInformationForVolunteer]) -> ListOfLines:
    other_information = ListOfLines(["Other information in form: (for each cadet entered with)"])
    for relevant_information in list_of_relevant_information:
        other_information.append(Line(relevant_information.details.any_other_information))

    return other_information

def get_any_other_information_input(list_of_relevant_information: List[RelevantInformationForVolunteer]) -> textInput:
    return textInput(
        input_name=ANY_OTHER_INFORMATION,
        input_label="Enter any information relevant to volunteer rota duties (or diet, if catering provided)",
        value=list_of_relevant_information[0].details.any_other_information
    )

def get_preferred_duties_text(list_of_relevant_information: List[RelevantInformationForVolunteer]) -> ListOfLines:
    preferred_duties = ListOfLines(["Preferred duties in form (for each cadet registered with):"])
    for relevant_information in list_of_relevant_information:
        preferred_duties.append(Line(relevant_information.availability.preferred_duties))

    return preferred_duties

def get_preferred_duties_input(list_of_relevant_information: List[RelevantInformationForVolunteer]) -> textInput:
    return textInput(
        input_name=PREFERRED_DUTIES,
        input_label="Enter preferred duties",
        value=list_of_relevant_information[0].availability.preferred_duties
    )

def get_same_or_different_text(list_of_relevant_information: List[RelevantInformationForVolunteer]) -> ListOfLines:
    same_or_different = ListOfLines(["Same or different duties in form (for each cadet registered with):"])
    for relevant_information in list_of_relevant_information:
        same_or_different.append(Line(relevant_information.availability.same_or_different))

    return same_or_different

def  get_same_or_different_input(list_of_relevant_information: List[RelevantInformationForVolunteer]) -> textInput:
    return textInput(
        input_name=SAME_OR_DIFFERENT,
        input_label="Enter same or different preference",
        value=list_of_relevant_information[0].availability.same_or_different
    )
