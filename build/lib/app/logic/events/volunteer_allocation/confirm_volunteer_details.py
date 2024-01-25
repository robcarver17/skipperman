from app.backend.volunteer_allocation import get_volunteer_from_id, update_volunteer_at_event
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_allocated_volunteer_id
from app.backend.volunteer_allocation import get_volunteer_at_event
from app.logic.events.volunteer_allocation.relevant_information import RelevantInformationForVolunteer
from app.logic.events.constants import *
from app.objects.abstract_objects.abstract_form import Form, NewForm, checkboxInput, textInput
from app.logic.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.events import Event
from app.objects.volunteers_at_event import VolunteerAtEvent
from app.backend.volunteer_allocation import get_relevant_information_for_current_volunteer
from app.objects.food import OTHER_IN_FOOD_REQUIRED, FoodRequirements
from app.objects.day_selectors import DaySelector

## once a volunteer is added, generate a form to capture / confirm availabilty and food preferences

FOOD_REQUIREMENTS="food_requirements"
OTHER_FOOD = "other_food_required"
AVAILABILITY = "availability"
## THIS IS NOT ROLE ALLOCATION

def display_form_confirm_volunteer_details(interface: abstractInterface):
    volunteer_id = get_allocated_volunteer_id(interface)
    event =get_event_from_state(interface)
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    relevant_information = get_relevant_information_for_current_volunteer(interface=interface)

    food_requirements_text = get_food_requirements_text(relevant_information)
    food_requirements_input = get_food_requirements_input(volunteer_at_event)
    available_text = get_availablity_text(relevant_information)
    available_checkbox = get_availability_checkbox(volunteer_at_event=volunteer_at_event, event=event)

    other_information = relevant_information.details.any_other_information

    return Form(ListOfLines([
        "Volunteer %s" % str(get_volunteer_from_id(volunteer_id)),
        other_information,
        food_requirements_text,
        food_requirements_input,
        available_text,
        available_checkbox,
        Button(SAVE_CHANGES)
    ]))


def get_food_requirements_text(relevant_information: RelevantInformationForVolunteer):
    dietary_requirements = relevant_information.details.food_preference
    if len(dietary_requirements)>0:
        selected_diet = "(Specified in form as %s)" % dietary_requirements
    else:
        selected_diet = ""

    return "Select food for volunteer %s" % selected_diet

def get_food_requirements_input(volunteer_at_event: VolunteerAtEvent) -> ListOfLines:
    existing_food_requirements = volunteer_at_event.food_requirements
    existing_food_requirements_as_dict = existing_food_requirements.as_dict()
    existing_food_requirements_other = existing_food_requirements_as_dict.pop(OTHER_IN_FOOD_REQUIRED)

    existing_food_requirements_labels = list(existing_food_requirements_as_dict.keys())
    dict_of_labels = dict([(required, required) for required in existing_food_requirements_labels])
    dict_of_checked = dict([(required, existing_food_requirements_as_dict.get(required))
                            for required in existing_food_requirements_labels])

    checkbox = checkboxInput(dict_of_labels=dict_of_labels,
                  dict_of_checked=dict_of_checked,
                  input_name=FOOD_REQUIREMENTS,
                  input_label="Enter dietary requirements for volunteer:")
    other_input = textInput(input_label="Other:", input_name=OTHER_IN_FOOD_REQUIRED,
                            value=existing_food_requirements_other)

    return ListOfLines([
        checkbox,
        other_input
    ])

def get_availablity_text(relevant_information: RelevantInformationForVolunteer):
    availability_info = relevant_information.availability
    available_text = "Select availability for volunteer "
    if len(availability_info.day_availability)>0:
        available_text = available_text+ " In form available on %s " % availability_info.day_availability
    if len(availability_info.weekend_availability)>0:
        available_text = available_text + " In form available on %s " % availability_info.weekend_availability

    available_text = available_text + " Cadet registered for %s" % str(availability_info.cadet_availability)

    return available_text
def get_availability_checkbox(volunteer_at_event: VolunteerAtEvent, event: Event):
    current_availability = volunteer_at_event.availablity

    possible_days = event.weekdays_in_event
    dict_of_labels = dict([(day.name, day.name) for day in possible_days])
    dict_of_checked = dict([(day.name, current_availability.get(day, False)) for day in possible_days])

    return checkboxInput(dict_of_labels=dict_of_labels,
                  dict_of_checked=dict_of_checked,
                  input_name=AVAILABILITY,
                  input_label="Confirm availability for volunteer:")


def post_form_confirm_volunteer_details(interface: abstractInterface):
    update_volunteer_at_event_with_form_contents(interface)
    continue_to_next_volunteer()

def update_volunteer_at_event_with_form_contents(interface: abstractInterface):
    other_food = interface.value_from_form(OTHER_IN_FOOD_REQUIRED)
    food_required_as_list = interface.value_of_multiple_options_from_form(FOOD_REQUIREMENTS)
    volunteer_availablity_by_day = interface.value_of_multiple_options_from_form(AVAILABILITY)

    volunteer_id = get_allocated_volunteer_id(interface)
    event =get_event_from_state(interface)
    availability = get_availablity(volunteer_availablity_by_day=volunteer_availablity_by_day, event=event)
    food_requirement = get_food_requirements(food_required_as_list=food_required_as_list, other_food=other_food)

    update_volunteer_at_event_with_new_food_and_availability(event=event,
                                                             volunteer_id=volunteer_id,
                                                             availability=availability,
                                                             food_requirements=food_requirement)

def get_food_requirements(food_required_as_list: list, other_food: str)-> FoodRequirements:
    food_requirements = FoodRequirements()
    possible_fields = list(food_requirements.as_dict().keys())

    for key in possible_fields:
        if key == OTHER_IN_FOOD_REQUIRED:
            setattr(food_requirements, key, other_food)
            continue

        setattr(food_requirements, key, key in food_required_as_list)


    return food_requirements

def get_availablity(volunteer_availablity_by_day: list, event: Event) -> DaySelector:
    possible_days = event.weekdays_in_event
    day_selector = DaySelector()
    for day in possible_days:
        if day.name in volunteer_availablity_by_day:
            day_selector[day] = True
        else:
            day_selector[day] = False

    return day_selector

def update_volunteer_at_event_with_new_food_and_availability(volunteer_id: str, event: Event,
                                                             food_requirements: FoodRequirements,
                                                             availability: DaySelector):

    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    volunteer_at_event.food_requirements = food_requirements
    volunteer_at_event.availablity = availability

    update_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)

def continue_to_next_volunteer():
    ## Now loop to next volunteer for cadet
    return NewForm(WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_LOOP_IN_VIEW_EVENT_STAGE)

