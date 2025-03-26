from typing import List

from app.backend.events.list_of_events import get_list_of_last_N_events, get_list_of_events
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line, _______________
from app.objects.events import Event, ListOfEvents
from app.objects.exceptions import missing_data
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_buttons import Button
from app.frontend.shared.buttons import get_button_value_given_type_and_attributes, is_button_of_type

DEFAULT_EVENT_COUNT = 3

def get_previous_event_selection_form(interface: abstractInterface, event: Event) -> ListOfLines:

    return ListOfLines([
        _______________,
        "Choose events to show in group allocation form",
        _______________,
        get_checkbox_for_event_selection(interface=interface, event=event),
        _______________,
        Line([revert_to_default_event_button, save_changes_event_button])
    ])


def get_checkbox_for_event_selection(interface: abstractInterface, event: Event):
    picklist = get_picklist_of_all_events_excluding_current(interface.object_store, event=event)
    selected_events = get_prior_events_to_show(interface=interface, event=event)
    event_names = [str(event) for event in picklist]
    selected_names = [str(event) for event in selected_events]

    dict_of_labels = dict([(name,name) for name in event_names])
    dict_of_checked = dict([(name,name in selected_names) for name in event_names])
    return checkboxInput(
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
        input_name=event_selection_form_value,
        input_label='',
        line_break=True
    )


def is_event_picker_button(button_value:str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=button_type)

def get_prior_events_to_show(interface: abstractInterface, event: Event) -> ListOfEvents:
    event_id_selection = get_prior_event_selection_in_state(interface)
    if event_id_selection is missing_data:
        return default_list_of_prior_events(object_store=interface.object_store, event=event)
    else:
        return get_list_of_events_given_selection(object_store=interface.object_store, event=event, event_id_selection=event_id_selection)

def get_list_of_events_given_selection(object_store: ObjectStore, event: Event, event_id_selection: List[str]) -> ListOfEvents:
    all_events = get_list_of_events(object_store)
    list_of_events = [all_events.event_with_id(event_id) for event_id in event_id_selection if not event.id == event_id]

    return ListOfEvents(list_of_events)

def default_list_of_prior_events(object_store: ObjectStore, event: Event):
    list_of_events = get_list_of_last_N_events(
        object_store=object_store,
        N_events=3,
        excluding_event=event,
        only_events_before_excluded_event=True,
    )

    return list_of_events

def get_picklist_of_all_events_excluding_current(object_store: ObjectStore, event: Event):
    list_of_events = get_list_of_last_N_events(
        object_store=object_store,
        excluding_event=event,
        only_events_before_excluded_event=False
    )
    list_of_events = list_of_events.sort_by_start_date_desc()

    return list_of_events



def save_event_selection_from_form(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if revert_to_default_event_button.pressed(last_button):
        clear_prior_event_selection_in_state(interface)
    else:
        save_event_selection_from_form_if_saved_button_pressed(interface)

def save_event_selection_from_form_if_saved_button_pressed(interface: abstractInterface):
    picklist = get_list_of_events(interface.object_store)
    event_names_chosen = interface.value_of_multiple_options_from_form(event_selection_form_value)

    new_list_of_ids = []
    for event in picklist:
        event_name= str(event)
        if event_name in event_names_chosen:
            new_list_of_ids.append(event.id)

    store_prior_event_selection_in_state(interface=interface, list_of_event_ids=new_list_of_ids)

PRIOR_EVENT_LIST = "PriorEventList"

def store_prior_event_selection_in_state(interface: abstractInterface, list_of_event_ids: List[str]):
    interface.set_persistent_value(PRIOR_EVENT_LIST, list_of_event_ids)

def get_prior_event_selection_in_state(interface: abstractInterface):
    return interface.get_persistent_value(PRIOR_EVENT_LIST, missing_data)

def clear_prior_event_selection_in_state(interface: abstractInterface):
    interface.clear_persistent_value(PRIOR_EVENT_LIST)


button_type = "ChangeEventPic"
event_selection_form_value = "eventSelection"


revert_to_default_event_button = Button("Use default (last %d events)" % DEFAULT_EVENT_COUNT,
                                         get_button_value_given_type_and_attributes(
                                             button_type, 'revertToDefault'
                                         ))


save_changes_event_button = Button("Save changes to event selection",
                                         get_button_value_given_type_and_attributes(
                                             button_type, 'SaveChanges'
                                         ))
