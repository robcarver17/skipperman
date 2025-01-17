from app.objects.volunteers import Volunteer

from app.objects.cadets import Cadet


from app.backend.food.active_cadets_and_volunteers_with_food import (
    get_dict_of_active_cadets_with_food_requirements_at_event,
    get_dict_of_active_volunteers_with_food_requirements_at_event,
)
from app.objects.abstract_objects.abstract_form import File

from app.objects.events import Event

from app.backend.food.download_food_data import download_food_data_and_return_filename
from app.backend.food.modify_food_data import (
    update_cadet_food_data,
    update_volunteer_food_data,
)
from app.objects.food import (
    FoodRequirements,
)

from app.frontend.shared.events_state import get_event_from_state


from app.frontend.events.food.render_food import (
    get_input_name_other_food_for_cadet,
    get_input_name_food_checkbox_for_cadet,
    get_input_name_other_food_for_volunteer,
    get_input_name_food_checkbox_for_volunteer,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.forms.form_utils import get_food_requirements_from_form


def save_food_data_in_form(interface: abstractInterface):
    save_cadet_food_data_in_form(interface)
    save_volunteer_food_data_in_form(interface)


def save_cadet_food_data_in_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    cadets_with_food_at_event = (
        get_dict_of_active_cadets_with_food_requirements_at_event(
            object_store=interface.object_store, event=event
        )
    )

    for cadet, existing_food_requirements in cadets_with_food_at_event:
        save_cadet_food_data_for_cadet(
            interface=interface,
            event=event,
            cadet=cadet,
            existing_food_requirements=existing_food_requirements,
        )


def save_cadet_food_data_for_cadet(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    existing_food_requirements: FoodRequirements,
):
    other_input_name = get_input_name_other_food_for_cadet(cadet_id=cadet.id)
    checkbox_input_name = get_input_name_food_checkbox_for_cadet(cadet_id=cadet.id)

    new_food_requirements = get_food_requirements_from_form(
        interface=interface,
        other_input_name=other_input_name,
        checkbox_input_name=checkbox_input_name,
    )

    update_cadet_food_data_if_changed(
        interface=interface,
        cadet=cadet,
        existing_food_requirements=existing_food_requirements,
        new_food_requirements=new_food_requirements,
        event=event,
    )


def update_cadet_food_data_if_changed(
    interface: abstractInterface,
    cadet: Cadet,
    existing_food_requirements: FoodRequirements,
    new_food_requirements: FoodRequirements,
    event: Event,
):
    if existing_food_requirements == new_food_requirements:
        return

    try:
        update_cadet_food_data(
            object_store=interface.object_store,
            event=event,
            cadet=cadet,
            new_food_requirements=new_food_requirements,
        )
    except Exception as e:
        interface.log_error(
            "Couldn't update food_report for cadet %s, error %s" % (str(cadet), str(e))
        )


def save_volunteer_food_data_in_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    volunteers_with_food_at_event = (
        get_dict_of_active_volunteers_with_food_requirements_at_event(
            object_store=interface.object_store, event=event
        )
    )

    for volunteer, existing_food_requirements in volunteers_with_food_at_event.items():
        save_volunteer_food_data_for_volunteer(
            interface=interface,
            event=event,
            volunteer=volunteer,
            existing_food_requirements=existing_food_requirements,
        )


def save_volunteer_food_data_for_volunteer(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    existing_food_requirements: FoodRequirements,
):
    other_input_name = get_input_name_other_food_for_volunteer(
        volunteer_id=volunteer.id
    )
    checkbox_input_name = get_input_name_food_checkbox_for_volunteer(
        volunteer_id=volunteer.id
    )

    new_food_requirements = get_food_requirements_from_form(
        interface=interface,
        other_input_name=other_input_name,
        checkbox_input_name=checkbox_input_name,
    )

    update_volunteer_food_data_if_changed(
        interface=interface,
        event=event,
        volunteer=volunteer,
        existing_food_requirements=existing_food_requirements,
        new_food_requirements=new_food_requirements,
    )


def update_volunteer_food_data_if_changed(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    existing_food_requirements: FoodRequirements,
    new_food_requirements: FoodRequirements,
):
    if existing_food_requirements == new_food_requirements:
        return

    try:
        update_volunteer_food_data(
            object_store=interface.object_store,
            volunteer=volunteer,
            new_food_requirements=new_food_requirements,
            event=event,
        )
    except Exception as e:
        interface.log_error(
            "Couldn't update food_report for volunteer %s, error %s"
            % (str(volunteer), str(e))
        )


def download_food_data(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    filename = download_food_data_and_return_filename(
        object_store=interface.object_store, event=event
    )
    return File(filename)
