from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.objects.abstract_objects.abstract_form import File

from app.objects.events import Event

from app.backend.cadets import get_cadet_from_id

from app.backend.food import update_cadet_food_data, update_volunteer_food_data
from app.objects.food import CadetWithFoodRequirementsAtEvent, FoodRequirements, VolunteerWithFoodRequirementsAtEvent

from app.logic.events.events_in_state import get_event_from_state

from app.backend.data.food import FoodData

from app.logic.events.food_and_clothing.render_food import get_input_name_other_food_for_cadet, \
    get_input_name_food_checkbox_for_cadet, get_input_name_other_food_for_volunteer, \
    get_input_name_food_checkbox_for_volunteer

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.forms.form_utils import get_food_requirements_from_form

def save_food_data_in_form(interface: abstractInterface):
    save_cadet_food_data_in_form(interface)
    save_volunteer_food_data_in_form(interface)

def save_cadet_food_data_in_form(interface: abstractInterface):
    food_data = FoodData(interface.data)
    event = get_event_from_state(interface)

    cadets_with_food_at_event = food_data.list_of_active_cadets_with_food_at_event(event=event)

    for cadet_with_food in cadets_with_food_at_event:
        save_cadet_food_data_for_cadet(interface=interface, cadet_with_food=cadet_with_food, event=event)


def save_cadet_food_data_for_cadet(interface: abstractInterface, event: Event, cadet_with_food: CadetWithFoodRequirementsAtEvent):
    other_input_name = get_input_name_other_food_for_cadet(cadet_id=cadet_with_food.cadet_id)
    checkbox_input_name = get_input_name_food_checkbox_for_cadet(cadet_id=cadet_with_food.cadet_id)

    new_food_requirements = get_food_requirements_from_form(interface=interface,
                                                            other_input_name=other_input_name,
                                                            checkbox_input_name=checkbox_input_name)

    update_cadet_food_data_if_changed(interface=interface, existing_cadet_with_food=cadet_with_food, new_food_requirements=new_food_requirements,
                                      event=event)

def update_cadet_food_data_if_changed(interface: abstractInterface, existing_cadet_with_food: CadetWithFoodRequirementsAtEvent,
                                 new_food_requirements: FoodRequirements,
                                      event: Event):

    if existing_cadet_with_food.food_requirements== new_food_requirements:
        return

    try:
        update_cadet_food_data(interface=interface, cadet_id=existing_cadet_with_food.cadet_id, new_food_requirements=new_food_requirements, event=event)
    except Exception as e:
        cadet = get_cadet_from_id(interface=interface, cadet_id=existing_cadet_with_food.cadet_id)
        interface.log_error("Couldn't update food_report for cadet %s, error %s" % (str(cadet), str(e)))




def save_volunteer_food_data_in_form(interface: abstractInterface):
    food_data = FoodData(interface.data)
    event = get_event_from_state(interface)

    volunteers_with_food_at_event = food_data.list_of_active_volunteers_with_food_at_event(event=event)

    for volunteer_with_food in volunteers_with_food_at_event:
        save_volunteer_food_data_for_volunteer(interface=interface, volunteer_with_food=volunteer_with_food, event=event)


def save_volunteer_food_data_for_volunteer(interface: abstractInterface, event: Event,
                                   volunteer_with_food: VolunteerWithFoodRequirementsAtEvent):
    other_input_name = get_input_name_other_food_for_volunteer(volunteer_id=volunteer_with_food.volunteer_id)
    checkbox_input_name = get_input_name_food_checkbox_for_volunteer(volunteer_id=volunteer_with_food.volunteer_id)

    new_food_requirements = get_food_requirements_from_form(interface=interface,
                                                            other_input_name=other_input_name,
                                                            checkbox_input_name=checkbox_input_name)

    update_volunteer_food_data_if_changed(interface=interface, existing_volunteer_with_food=volunteer_with_food,
                                      new_food_requirements=new_food_requirements,
                                      event=event)


def update_volunteer_food_data_if_changed(interface: abstractInterface,
                                      existing_volunteer_with_food: VolunteerWithFoodRequirementsAtEvent,
                                      new_food_requirements: FoodRequirements,
                                      event: Event):
    if existing_volunteer_with_food.food_requirements == new_food_requirements:
        return

    try:
        update_volunteer_food_data(interface=interface, volunteer_id=existing_volunteer_with_food.volunteer_id,
                               new_food_requirements=new_food_requirements, event=event)
    except Exception as e:
        volunteer = get_volunteer_from_id(interface=interface, volunteer_id=existing_volunteer_with_food.volunteer_id)
        interface.log_error("Couldn't update food_report for volunteer %s, error %s" % (str(volunteer), str(e)))


def download_food_data(interface: abstractInterface) -> File:
    pass
    ## three sheets, summary, one for cadets, one for volunteers
    ## Summary has numbers across cadets and volunteers / days, plus allergies, and list of other allergies
    ## List of allergic by name
    ## Cadets: show days and allergies, group, lake group. Sort by group
    ## Volunteers: show # of days, days, allergies, role. Sort by #days, then role
