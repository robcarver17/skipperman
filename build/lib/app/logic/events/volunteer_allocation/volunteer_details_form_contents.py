from app.backend.cadets import cadet_name_from_id, cadet_from_id
from app.backend.form_utils import get_food_requirements_input, get_availability_checkbox
from app.backend.volunteers import is_cadet_already_connected_to_volunteer_in_volunteer_list
from app.logic.abstract_interface import abstractInterface
from app.logic.events.volunteer_allocation.volunteer_details_form_contents import FOOD_REQUIREMENTS, OTHER_FOOD, \
    AVAILABILITY, MAKE_CADET_CONNECTION, MAKE_CADET_CONNECTION_LABEL
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_volunteer_index, \
    get_current_cadet_id
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.constants import missing_data
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer
from app.objects.volunteers import Volunteer
from app.objects.volunteers_at_event import VolunteerAtEvent


def get_header_text(interface: abstractInterface, volunteer: Volunteer):

    volunteer_index = get_volunteer_index(interface)
    cadet_id = get_current_cadet_id(interface)
    cadet_name = cadet_name_from_id(cadet_id)
    volunteer_name = volunteer.name

    header_text = "For cadet %s, details for volunteer number %d - %s" % (cadet_name, volunteer_index+1, volunteer_name)
    if volunteer_index>0:
        header_text = header_text + " (Might be a duplicate volunteer - just save if no changes required)"

    return header_text


def get_connection_checkbox(interface: abstractInterface, volunteer: Volunteer):

    cadet_id = get_current_cadet_id(interface)

    cadet = cadet_from_id(cadet_id)

    already_connected = is_cadet_already_connected_to_volunteer_in_volunteer_list(volunteer=volunteer, cadet=cadet)
    if not already_connected:
        connection_checkbox = checkboxInput(
            dict_of_labels={MAKE_CADET_CONNECTION_LABEL: MAKE_CADET_CONNECTION_LABEL},
            dict_of_checked={MAKE_CADET_CONNECTION_LABEL: True},
            input_name=MAKE_CADET_CONNECTION,
            input_label="Tick to connect cadet with volunteer in main volunteer list (leave blank if not usually connected):"
        )
    else:
        connection_checkbox = ""

    return connection_checkbox


def get_food_requirements_text(relevant_information: RelevantInformationForVolunteer):
    dietary_requirements = relevant_information.details.food_preference
    if len(dietary_requirements)>0:
        selected_diet = "(Dietary requirements specified in form as %s)" % dietary_requirements
    else:
        selected_diet = "(No requirements specied in form)"

    return "Select food type for volunteer %s" % selected_diet


def get_food_requirements_input_for_volunteer_at_event(volunteer_at_event: VolunteerAtEvent) -> ListOfLines:
    existing_food_requirements = volunteer_at_event.food_requirements

    return get_food_requirements_input(existing_food_requirements=existing_food_requirements,
                                       checkbox_input_name=FOOD_REQUIREMENTS,
                                       other_input_name=OTHER_FOOD,
                                       other_input_label="Other:"
                                       )


def get_availablity_text(relevant_information: RelevantInformationForVolunteer) -> ListOfLines:
    print("RELEVANT INFORMATION: %s" % relevant_information)
    availability_info = relevant_information.availability
    available_text = ListOfLines(["Select availability for volunteer "])
    if availability_info.day_availability is not missing_data:
        available_text.append(" In form said they were available on %s " % availability_info.day_availability)
    elif availability_info.weekend_availability is not missing_data:
        available_text.append(" In form said they were available on %s " % availability_info.weekend_availability)
    else:
        available_text.append(" Cadet registered for %s" % str(availability_info.cadet_availability))

    return available_text


def get_availability_checkbox_for_volunteer_at_event(volunteer_at_event: VolunteerAtEvent, event: Event):

    return get_availability_checkbox(availability=volunteer_at_event.availablity,
                                     event=event,
                                     input_name=AVAILABILITY,
                                     input_label="Confirm availability for volunteer:")
