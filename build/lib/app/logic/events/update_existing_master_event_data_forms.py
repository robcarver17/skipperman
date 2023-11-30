from app.logic.events.constants import  USE_NEW_DATA_BUTTON_LABEL, \
    USE_ORIGINAL_DATA_BUTTON_LABEL, USE_DATA_IN_FORM_BUTTON_LABEL, ROW_IN_EVENT_DATA, ROW_STATUS
from app.logic.events.utilities import get_event_from_state
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.forms_and_interfaces.abstract_form import Form, Line, ListOfLines, radioInput, Button, construct_form_field_given_field_name

from app.logic.events.backend.update_master_event_data import new_status_and_status_message, update_row_in_master_event_data, \
    get_row_from_event_file_with_ids, NO_STATUS_CHANGE
from app.logic.events.backend.load_and_save_wa_mapped_events import load_master_event

from app.logic.cadets.view_cadets import cadet_name_from_id
from app.objects.constants import NoMoreData, missing_data
from app.objects.events import Event
from app.objects.master_event import RowInMasterEvent, get_row_of_master_event_from_mapped_row_with_idx_and_status
from app.objects.mapped_wa_event_with_ids import all_possible_status
from app.objects.utils import SingleDiff
from app.objects.field_list import FIELDS_TO_FLAG_WHEN_COMPARING_WA_DIFF

def display_form_for_update_to_existing_row_of_event_data(
        interface: abstractInterface,
        new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
        existing_row_in_master_event: RowInMasterEvent,
) -> Form:
    overall_message = "There have been changes for event registration information about cadet %s" % cadet_name_from_id(existing_row_in_master_event.cadet_id)

    status_change_field = get_status_change_field(new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
                                                  existing_row_in_master_event=existing_row_in_master_event)

    form_fields_with_other_differences = get_form_fields_with_other_differences(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event
    )

    buttons = buttons_for_update_row()

    form = Form(
        ListOfLines(
            [
                overall_message,
                status_change_field,
                form_fields_with_other_differences,
                buttons
            ]
        )
    )

    return form


def get_status_change_field(new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
        existing_row_in_master_event: RowInMasterEvent,
)-> Line:
    new_status, status_message = new_status_and_status_message(existing_row_in_master_event=existing_row_in_master_event,
                                  new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)
    ## TEXT BEFORE, AFTER, FORM FIELD VALUE PREOPULATED WITH AFTER
    ## FIELD IS RADIO BUTTONS

    if status_message is NO_STATUS_CHANGE:
        return Line(radioInput(input_label="Status of entry",
                         input_name=ROW_STATUS,
                         default_label=new_status.name,
                         dict_of_options={
                             new_status.name:new_status.name
                         }))
    else:
        return Line(radioInput(input_label="% select status" % status_message,
                                input_name=ROW_STATUS,
                                default_label=new_status.name,
                                    dict_of_options=dict(
                                     [(status_name, status_name) for
                                        status_name in all_status_names
                                    ]
                                )))


all_status_names = [row_status.name for row_status in all_possible_status]

def get_form_fields_with_other_differences(new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
        existing_row_in_master_event: RowInMasterEvent) -> ListOfLines:

    dict_of_dict_diffs = (
        existing_row_in_master_event.dict_of_row_diffs_in_rowdata(
            new_row_in_mapped_wa_event_with_status
        )
    )

    list_of_field_names = get_list_of_field_names_from_dict_of_dict_diffs(
        dict_of_dict_diffs
    )
    list_of_form_fields = [
        form_field_for_item_with_difference(field_name=field_name,
                                            diff=dict_of_dict_diffs[field_name])
        for field_name in list_of_field_names
        if field_name in FIELDS_TO_FLAG_WHEN_COMPARING_WA_DIFF
        ]

    return ListOfLines(list_of_form_fields)




def form_field_for_item_with_difference(field_name:str, diff: SingleDiff) -> Line:
    form_field = construct_form_field_given_field_name(
        field_name=field_name,
        input_label = "Field %s, was %s now %s: " % (field_name, diff.old_value, diff.new_value),
        input_name = field_name,
        value = diff.new_value
    )

    return Line(form_field)

def buttons_for_update_row() -> Line:
    use_new_data =Button(USE_NEW_DATA_BUTTON_LABEL)
    use_original_data = Button(USE_ORIGINAL_DATA_BUTTON_LABEL)
    use_data_in_form = Button(USE_DATA_IN_FORM_BUTTON_LABEL)

    return Line([
        use_original_data, use_new_data, use_data_in_form
    ])

## Functions called on post
def update_mapped_wa_event_data_with_new_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    new_row_in_mapped_wa_event_with_status = get_new_row_in_mapped_wa_event_from_state_data(
        event=event,
        interface=interface
    )
    update_row_in_master_event_data(event=event,
                                    new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)


def update_mapped_wa_event_data_with_form_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    new_row_in_mapped_wa_event_with_status = get_new_row_merged_with_form_data_in_mapped_wa_event(
        interface=interface,
        event=event
    )
    update_row_in_master_event_data(event=event,
                                    new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)


def get_new_row_in_mapped_wa_event_from_state_data(interface: abstractInterface,
                                                   event: Event) -> RowInMasterEvent:
    row_idx = get_current_row_id_in_event_data(interface)

    try:
        row_in_mapped_wa_event_with_id = (
            get_row_from_event_file_with_ids(event, row_idx=row_idx)
        )
    except NoMoreData:
        raise Exception("Row index too large when trying to get row from imported WA data")

    new_row_in_mapped_wa_event_with_status = (
        get_row_of_master_event_from_mapped_row_with_idx_and_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
    )
    return new_row_in_mapped_wa_event_with_status


def get_new_row_merged_with_form_data_in_mapped_wa_event(interface: abstractInterface,
                                                   event: Event) -> RowInMasterEvent:
    new_row_in_mapped_wa_event_with_status = get_new_row_in_mapped_wa_event_from_state_data(
        interface=interface,
        event=event
    )
    new_row_in_mapped_wa_event_with_status = replace_row_values_from_form_values_in_mapped_wa_event(interface=interface, new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)

    return new_row_in_mapped_wa_event_with_status


def replace_row_values_from_form_values_in_mapped_wa_event(
        interface: abstractInterface,
        new_row_in_mapped_wa_event_with_status: RowInMasterEvent
) -> RowInMasterEvent:
    field_names = get_field_names_for_recently_posted_event_diff_form(interface=interface,
                                                                      new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)
    for field in field_names:
        try:
            new_row_in_mapped_wa_event_with_status.data_in_row[field] = interface.value_from_form(field)
        except:
            raise Exception("Value for field %s not found in form" % field)

    return new_row_in_mapped_wa_event_with_status

def get_field_names_for_recently_posted_event_diff_form(interface: abstractInterface,
                                         new_row_in_mapped_wa_event_with_status: RowInMasterEvent
                                         ):
    event = get_event_from_state(interface)
    master_event = load_master_event(
        event
    )

    existing_row_in_master_event = (
        master_event.get_row_with_id(
            new_row_in_mapped_wa_event_with_status.cadet_id
        )
    )
    dict_of_dict_diffs = (
        existing_row_in_master_event.dict_of_row_diffs_in_rowdata(
            new_row_in_mapped_wa_event_with_status
        )
    )

    return get_list_of_field_names_from_dict_of_dict_diffs(dict_of_dict_diffs)


def increment_and_save_id_in_event_data(interface: abstractInterface):
    id = get_current_row_id_in_event_data(interface)
    id+=1
    interface.set_persistent_value(ROW_IN_EVENT_DATA, id)


def get_current_row_id_in_event_data(interface: abstractInterface):
    id = interface.get_persistent_value(ROW_IN_EVENT_DATA)
    if id is missing_data:
        return 0
    else:
        return id

def get_list_of_field_names_from_dict_of_dict_diffs(dict_of_dict_diffs: dict) -> list:
    return [field_name
            for field_name in dict_of_dict_diffs.items()
            if field_name in FIELDS_TO_FLAG_WHEN_COMPARING_WA_DIFF
            ]
