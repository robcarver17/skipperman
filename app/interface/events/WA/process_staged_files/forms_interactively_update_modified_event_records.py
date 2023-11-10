from app.interface.events.constants import WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE, USE_NEW_DATA, \
    USE_ORIGINAL_DATA, USE_DATA_IN_FORM, ROW_IN_EVENT_DATA, ROW_STATUS
from app.interface.events.utils import get_event_from_state
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.forms import form_html_wrapper, html_button, html_radio_input
from app.interface.html.html import Html, html_joined_list_as_paragraphs, html_joined_list, html_joined_list_as_lines
from app.interface.html.form_fields import construct_html_form_field_given_field_name

from app.logic.events.update_master_event_data import new_status_and_status_message, update_row_in_master_event_data, \
    get_row_from_event_file_with_ids, NO_STATUS_CHANGE
from app.logic.events.load_and_save_wa_mapped_events import load_master_event

from app.objects.cadets import cadet_name_from_id
from app.objects.constants import NoMoreData, missing_data
from app.objects.events import Event
from app.objects.master_event import RowInMasterEvent, get_row_of_master_event_from_mapped_row_with_idx_and_status
from app.objects.mapped_wa_event_with_ids import all_possible_status
from app.objects.utils import SingleDiff
from app.objects.field_list import FIELDS_TO_IGNORE_WHEN_COMPARING_WA_DIFF

def display_form_for_update_to_existing_row_of_event_data(
        state_data: StateDataForAction,
        new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
        existing_row_in_master_event: RowInMasterEvent,
) -> Html:
    overall_message = Html("There have been changes for event registration information about cadet %s" % cadet_name_from_id(existing_row_in_master_event.cadet_id))
    status_change_field = get_status_change_field(new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
                                                  existing_row_in_master_event=existing_row_in_master_event)
    form_fields_with_other_differences = get_form_fields_with_other_differences(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event
    )

    buttons = buttons_for_update_row()

    ## so gets posted to right place
    state_data.stage = WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE

    form_wrapper = form_html_wrapper(state_data.current_url)
    form = form_wrapper.wrap_around(
        html_joined_list_as_paragraphs(
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
)-> Html:
    new_status, status_message = new_status_and_status_message(existing_row_in_master_event=existing_row_in_master_event,
                                  new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)
    ## TEXT BEFORE, AFTER, FORM FIELD VALUE PREOPULATED WITH AFTER
    ## FIELD IS RADIO BUTTONS

    if status_message is NO_STATUS_CHANGE:
        return html_radio_input(input_label="Status of entry",
                         input_name=ROW_STATUS,
                         default_label=new_status.name,
                         dict_of_options={
                             new_status.name:new_status.name
                         })
    else:
        return html_radio_input(input_label="% select status" % status_message,
                                input_name=ROW_STATUS,
                                default_label=new_status.name,
                                    dict_of_options=dict(
                                     [(status_name, status_name) for
                                        status_name in all_status_names
                                    ]
                                ))


all_status_names = [row_status.name for row_status in all_possible_status]

def get_form_fields_with_other_differences(new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
        existing_row_in_master_event: RowInMasterEvent) ->Html:

    dict_of_dict_diffs = (
        existing_row_in_master_event.dict_of_row_diffs_in_rowdata(
            new_row_in_mapped_wa_event_with_status
        )
    )

    list_of_field_names = get_list_of_field_names_from_dict_of_dict_diffs(
        dict_of_dict_diffs
    )
    list_of_html_form_fields = [
        form_field_for_item_with_difference(field_name=field_name,
                                            diff=dict_of_dict_diffs[field_name])
        for field_name in list_of_field_names
        if field_name not in FIELDS_TO_IGNORE_WHEN_COMPARING_WA_DIFF
        ]

    return html_joined_list_as_paragraphs(list_of_html_form_fields)




def form_field_for_item_with_difference(field_name:str, diff: SingleDiff) -> Html:
    html_field = construct_html_form_field_given_field_name(
        field_name=field_name,
        input_label = "Field %s, was %s now %s: " % (field_name, diff.old_value, diff.new_value),
        input_name = field_name,
        value = diff.new_value
    )

    return html_field

def buttons_for_update_row() -> Html:
    use_new_data =html_button(USE_NEW_DATA)
    use_original_data = html_button(USE_ORIGINAL_DATA)
    use_data_in_form = html_button(USE_DATA_IN_FORM)

    return html_joined_list([
        use_original_data, use_new_data, use_data_in_form
    ])

## Functions called on post
def update_mapped_wa_event_data_with_new_data(state_data: StateDataForAction):
    event = get_event_from_state(state_data)
    new_row_in_mapped_wa_event_with_status = get_new_row_in_mapped_wa_event_from_state_data(
        event=event,
        state_data=state_data
    )
    update_row_in_master_event_data(event=event,
                                    new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)


def update_mapped_wa_event_data_with_form_data(state_data: StateDataForAction):
    event = get_event_from_state(state_data)
    new_row_in_mapped_wa_event_with_status = get_new_row_merged_with_form_data_in_mapped_wa_event(
        state_data=state_data,
        event=event
    )
    update_row_in_master_event_data(event=event,
                                    new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)


def get_new_row_in_mapped_wa_event_from_state_data(state_data: StateDataForAction,
                                                   event: Event) -> RowInMasterEvent:
    row_idx = get_current_row_id_in_event_data(state_data)

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


def get_new_row_merged_with_form_data_in_mapped_wa_event(state_data: StateDataForAction,
                                                   event: Event) -> RowInMasterEvent:
    new_row_in_mapped_wa_event_with_status = get_new_row_in_mapped_wa_event_from_state_data(
        state_data=state_data,
        event=event
    )
    new_row_in_mapped_wa_event_with_status = replace_row_values_from_form_values_in_mapped_wa_event(state_data= state_data, new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)

    return new_row_in_mapped_wa_event_with_status


def replace_row_values_from_form_values_in_mapped_wa_event(
        state_data: StateDataForAction,
        new_row_in_mapped_wa_event_with_status: RowInMasterEvent
) -> RowInMasterEvent:
    field_names = get_field_names_for_recently_posted_event_diff_form(state_data=state_data,
                                                                      new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)
    for field in field_names:
        try:
            new_row_in_mapped_wa_event_with_status.data_in_row[field] = state_data.value_from_form(field)
        except:
            raise Exception("Value for field %s not found in form" % field)

    return new_row_in_mapped_wa_event_with_status

def get_field_names_for_recently_posted_event_diff_form(state_data: StateDataForAction,
                                         new_row_in_mapped_wa_event_with_status: RowInMasterEvent
                                         ):
    event = get_event_from_state(state_data)
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


def increment_and_save_id_in_event_data(state_data: StateDataForAction):
    id = get_current_row_id_in_event_data(state_data)
    id+=1
    state_data.set_value(ROW_IN_EVENT_DATA, id)


def get_current_row_id_in_event_data(state_data: StateDataForAction):
    id = state_data.get_value(ROW_IN_EVENT_DATA)
    if id is missing_data:
        return 0

def get_list_of_field_names_from_dict_of_dict_diffs(dict_of_dict_diffs: dict) -> list:
    return [field_name
            for field_name in dict_of_dict_diffs.items()
            if field_name not in FIELDS_TO_IGNORE_WHEN_COMPARING_WA_DIFF
            ]
