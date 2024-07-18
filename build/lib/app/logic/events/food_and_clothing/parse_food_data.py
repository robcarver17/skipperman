from app.OLD_backend.volunteers.volunteers import DEPRECATE_get_volunteer_from_id
from app.objects.abstract_objects.abstract_form import File

from app.objects.events import Event

from app.OLD_backend.cadets import DEPRECATE_get_cadet_from_id

from app.OLD_backend.food import update_cadet_food_data, update_volunteer_food_data, download_food_data_and_return_filename
from app.objects.food import CadetWithFoodRequirementsAtEvent, FoodRequirements, VolunteerWithFoodRequirementsAtEvent

from app.logic.shared.events_state import get_event_from_state

from app.OLD_backend.data.food import FoodData

from app.logic.events.food.render_food import get_input_name_other_food_for_cadet, \
    get_input_name_food_checkbox_for_cadet, get_input_name_other_food_for_volunteer, \
    get_input_name_food_checkbox_for_volunteer

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.OLD_backend.forms.form_utils import get_food_requirements_from_form

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
        cadet = DEPRECATE_get_cadet_from_id(interface=interface, cadet_id=existing_cadet_with_food.cadet_id)
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
        volunteer = DEPRECATE_get_volunteer_from_id(interface=interface, volunteer_id=existing_volunteer_with_food.volunteer_id)
        interface.log_error("Couldn't update food_report for volunteer %s, error %s" % (str(volunteer), str(e)))


def download_food_data(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    filename = download_food_data_and_return_filename(interface=interface, event=event)
    return File(filename)


