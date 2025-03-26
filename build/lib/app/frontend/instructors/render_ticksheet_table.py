from app.frontend.shared.events_state import get_event_from_state
from app.objects.exceptions import MissingData, MISSING_FROM_FORM

from app.frontend.shared.cadet_state import get_cadet_from_state
from typing import List, Dict

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.composed.ticksheet import DictOfCadetsAndTicksWithinQualification
from app.objects.composed.ticks_for_qualification import (
    DictOfTickSheetItemsAndTicksForCadet,
    TicksForQualification,
)

from app.frontend.instructors.buttons import (
    get_cadet_buttons_at_start_of_row_in_edit_state,
    get_button_or_label_for_tickitem_name,
    get_select_cadet_button_when_in_no_edit_mode,
)
from app.backend.qualifications_and_ticks.ticksheets import (
    get_ticksheet_data_for_cadets_at_event_in_group_with_qualification,
)

from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.frontend.shared.qualification_and_tick_state_storage import (
    get_edit_state_of_ticksheet,
    NO_EDIT_STATE,
    EDIT_CHECKBOX_STATE,
    EDIT_DROPDOWN_STATE,
    not_editing,
    return_true_if_a_cadet_id_been_set,
    get_group_from_state,
    get_qualification_from_state,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import checkboxInput, dropDownInput
from app.objects.qualifications import Qualification

from app.objects.ticks import (
    Tick,
    tick_as_str,
    no_tick,
    full_tick,
    list_of_tick_options,
)
from app.objects.substages import TickSheetItem


def get_ticksheet_table(
    interface: abstractInterface,
) -> Table:
    ticksheet_data = get_ticksheet_data_from_state(interface=interface)
    print("Length of ticksheet %d" % len(ticksheet_data))
    top_rows = get_top_two_rows_for_table(
        interface=interface, ticksheet_data=ticksheet_data
    )
    other_rows = get_body_of_table(interface=interface, ticksheet_data=ticksheet_data)

    return Table(top_rows + other_rows, has_column_headings=True, has_row_headings=True)


def get_top_two_rows_for_table(
    interface: abstractInterface,
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
) -> List[RowInTable]:
    list_of_tick_list_items = (
        ticksheet_data.list_of_tick_sheet_items_for_this_qualification
    )
    list_of_substage_names = (
        ticksheet_data.list_of_substage_names_aligned_to_tick_sheet_items
    )

    first_row = [""]
    second_row = [""]
    current_substage = ""
    for tick_item, substage_name in zip(
        list_of_tick_list_items, list_of_substage_names
    ):
        if current_substage != substage_name:
            subheading = current_substage = substage_name
        else:
            subheading = ""

        tick_item_button_or_label = get_button_or_label_for_tickitem_name(
            interface=interface, tick_item=tick_item
        )

        first_row.append(subheading)
        second_row.append(tick_item_button_or_label)

    first_row = RowInTable(first_row)
    second_row = RowInTable(second_row)

    return [first_row, second_row]


def get_body_of_table(
    interface: abstractInterface,
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
) -> List[RowInTable]:
    return [
        get_row_for_cadet_in_ticksheet(
            interface=interface,
            row_in_ticksheet_data=row_in_ticksheet_data,
            cadet=cadet,
        )
        for cadet, row_in_ticksheet_data in ticksheet_data.items()
    ]


def get_row_for_cadet_in_ticksheet(
    interface: abstractInterface,
    row_in_ticksheet_data: TicksForQualification,
    cadet: Cadet,
) -> RowInTable:
    all_tick_sheet_items_and_ticks = (
        row_in_ticksheet_data.all_tick_sheet_items_and_ticks()
    )

    already_qualified = row_in_ticksheet_data.already_qualified
    first_cell_in_row = get_cadet_cell_at_start_of_row(
        interface=interface,
        qualification=row_in_ticksheet_data._qualification,
        already_qualified=already_qualified,
        cadet=cadet,
    )
    rest_of_row = get_rest_of_row_in_table_for_dict_of_tick_item(
        interface=interface,
        all_tick_sheet_items_and_ticks=all_tick_sheet_items_and_ticks,
        cadet=cadet,
        already_qualified=already_qualified,
    )

    return RowInTable([first_cell_in_row] + rest_of_row)


def get_cadet_cell_at_start_of_row(
    interface: abstractInterface,
    qualification: Qualification,
    cadet: Cadet,
    already_qualified: bool,
) -> list:
    has_an_id_been_set = return_true_if_a_cadet_id_been_set(interface)

    cadet_name = cadet.name
    qualification_name = qualification.name

    if already_qualified:
        cadet_label = "%s (%s)" % (cadet_name, qualification_name)
    else:
        cadet_label = cadet_name

    if not_editing(interface):
        return get_select_cadet_button_when_in_no_edit_mode(
            cadet=cadet,
            cadet_label=cadet_label,
            has_an_id_been_set=has_an_id_been_set,
        )
    else:
        return get_cadet_buttons_at_start_of_row_in_edit_state(
            interface=interface,
            cadet_id=cadet.id,
            qualification_name=qualification_name,
            cadet_name=cadet_name,
            already_qualified=already_qualified,
        )


def get_rest_of_row_in_table_for_dict_of_tick_item(
    interface: abstractInterface,
    cadet: Cadet,
    all_tick_sheet_items_and_ticks: DictOfTickSheetItemsAndTicksForCadet,
    already_qualified: bool,
) -> list:
    return [
        get_cell_in_table_for_tick(
            interface=interface,
            tick=tick,
            item=item,
            cadet=cadet,
            already_qualified=already_qualified,
        )
        for item, tick in all_tick_sheet_items_and_ticks.items()
    ]


def get_cell_in_table_for_tick(
    interface: abstractInterface,
    tick: Tick,
    cadet: Cadet,
    item: TickSheetItem,
    already_qualified: bool,
):
    state = get_edit_state_of_ticksheet(interface)
    if already_qualified:
        return get_cell_in_table_for_view_only(full_tick)
    if state == NO_EDIT_STATE:
        return get_cell_in_table_for_view_only(tick)
    elif state == EDIT_DROPDOWN_STATE:
        return get_cell_in_table_for_dropdown_edit(
            tick=tick, item_id=item.id, cadet_id=cadet.id
        )
    elif state == EDIT_CHECKBOX_STATE:
        return get_cell_in_table_for_checkbox_edit(
            tick=tick, item_id=item.id, cadet_id=cadet.id
        )
    else:
        raise Exception("state %s not known" % state)


def get_cell_in_table_for_view_only(tick: Tick):
    return tick_as_str(tick)


def get_cell_in_table_for_checkbox_edit(tick: Tick, cadet_id: str, item_id: str):
    if tick == no_tick:
        return get_checkbox_input(False, cadet_id=cadet_id, item_id=item_id)
    elif tick == full_tick:
        return get_checkbox_input(True, cadet_id=cadet_id, item_id=item_id)
    else:
        ## can't edit
        return tick_as_str(tick)


FULL_TICK = "full"


def get_checkbox_input(ticked: bool, cadet_id: str, item_id: str) -> checkboxInput:
    return checkboxInput(
        input_name=get_name_of_cell(item_id=item_id, cadet_id=cadet_id, dropdown=False),
        dict_of_labels={FULL_TICK: ""},
        dict_of_checked={FULL_TICK: ticked},
        input_label="",
    )


def get_tick_from_checkbox_or_none(
    interface: abstractInterface, cadet_id: str, item_id: str
) -> Tick:
    selected_ticks = interface.value_of_multiple_options_from_form(
        get_name_of_cell(
            item_id=item_id,
            cadet_id=cadet_id,
            dropdown=False,
        ),
        default=MISSING_FROM_FORM,
    )
    if selected_ticks is MISSING_FROM_FORM:
        ## must be half or no tick
        return None

    if FULL_TICK in selected_ticks:
        return full_tick
    else:
        return no_tick


def get_cell_in_table_for_dropdown_edit(
    tick: Tick, cadet_id: str, item_id: str
) -> dropDownInput:
    current_tick_name = tick.name
    dict_of_tick_options = get_dict_of_tick_options()

    return dropDownInput(
        input_label="",
        dict_of_options=dict_of_tick_options,
        default_label=current_tick_name,
        input_name=get_name_of_cell(item_id=item_id, cadet_id=cadet_id, dropdown=True),
    )


def get_dict_of_tick_options() -> Dict[str, str]:
    option_names = [option.name for option in list_of_tick_options]
    dict_of_options = dict([(name, name) for name in option_names])

    return dict_of_options


def get_tick_from_dropdown_or_none(
    interface: abstractInterface, cadet_id: str, item_id: str
) -> Tick:
    selected_tick_name = interface.value_from_form(
        get_name_of_cell(item_id=item_id, cadet_id=cadet_id, dropdown=True),
        default=MISSING_FROM_FORM,
    )
    if selected_tick_name is MISSING_FROM_FORM:
        ## happens if tick can't be edited
        return None

    return Tick[selected_tick_name]


def get_name_of_cell(item_id: str, cadet_id: str, dropdown: bool):
    return "%s_%s_%s" % (item_id, cadet_id, str(dropdown))


def get_ticksheet_data_from_state(
    interface: abstractInterface,
) -> DictOfCadetsAndTicksWithinQualification:
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)

    ticksheet_data = get_ticksheet_data_for_cadets_at_event_in_group_with_qualification(
        object_store=interface.object_store,
        event=event,
        group=group,
        qualification=qualification,
    )
    ticksheet_data = filter_ticksheet_for_selected_cadet(
        ticksheet_data=ticksheet_data, interface=interface
    )

    return ticksheet_data


def filter_ticksheet_for_selected_cadet(
    interface: abstractInterface,
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
) -> DictOfCadetsAndTicksWithinQualification:
    try:
        cadet = get_cadet_from_state(interface)
        return ticksheet_data.subset_for_list_of_cadets(ListOfCadets([cadet]))
    except MissingData:
        return ticksheet_data


def get_dropdown_mode_from_state(interface: abstractInterface):
    state = get_edit_state_of_ticksheet(interface)
    if state == NO_EDIT_STATE:
        raise Exception("can't get dropdown mode if not editing")
    elif state == EDIT_DROPDOWN_STATE:
        return True
    elif state == EDIT_CHECKBOX_STATE:
        return False
    else:
        raise Exception("State %s not recognised " % state)
