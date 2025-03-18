from typing import Union

from app.backend.rota.add_volunteer import (
    get_list_of_volunteers_except_those_already_at_event,
    add_volunteer_to_event_with_full_availability,
)
from app.frontend.shared.add_select_volunteer_form import ParametersForGetOrSelectVolunteerForm, \
    get_add_or_select_existing_volunteer_form, generic_post_response_to_add_or_select_volunteer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.volunteers import Volunteer, default_volunteer

def display_form_add_new_volunteer_to_rota_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return get_add_or_select_existing_volunteer_form(
        volunteer=default_volunteer,
        interface=interface,
        parameters=parameters_for_form
    )


header_text = ListOfLines(
    [
        "Enter the details of a new volunteer to be added, or select an existing volunteer"
    ]
)

parameters_for_form = ParametersForGetOrSelectVolunteerForm(header_text=header_text,
                                                            help_string='volunteer_rota_help#add-a-volunteer',
                                                            cancel_button=True)


def post_form_add_new_volunteer_to_rota_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    result = generic_post_response_to_add_or_select_volunteer(
        interface=interface, parameters=parameters_for_form
    )
    if result.cancel:
        return previous_form(interface)
    elif result.is_form:
        return result.form
    elif result.is_volunteer:
        return action_when_volunteer_known_for_rota(
        volunteer=result.volunteer, interface=interface
    )
    else:
        raise Exception("Return result %s cannot handle" % str(result))





def action_when_volunteer_known_for_rota(
    volunteer: Volunteer, interface: abstractInterface
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    not_at_event = get_list_of_volunteers_except_those_already_at_event(object_store=interface.object_store, event=event)
    if volunteer in not_at_event:
        add_volunteer_to_event_with_full_availability(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
        interface.flush_cache_to_store()
    else:
        interface.log_error("Volunteer %s is already at event %s!" % (volunteer.name, event.name))

    return previous_form(interface)



def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_add_new_volunteer_to_rota_at_event
    )

