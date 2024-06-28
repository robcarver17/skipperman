from typing import Union, List

from app.objects.cadets import Cadet

from app.backend.cadets import (
    get_list_of_cadets_not_on_committee_ordered_by_age,
    get_list_of_cadets_on_committee,
    get_list_of_cadets_not_on_committee_in_right_age_bracket,
    get_next_year_for_cadet_committee,
    get_cadet_given_cadet_as_str,
    add_new_cadet_to_committee,
    toggle_selection_for_cadet_committee_member,
    month_name_when_cadet_committee_age_bracket_begins,
    get_cadet_from_id,
    start_and_end_date_on_cadet_commmittee,
)
from app.objects.committee import CadetOnCommittee
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    dropDownInput,
    dateInput,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    DetailListOfLines,
)
from app.objects.abstract_objects.abstract_text import Heading
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_tables import Table, RowInTable

ADD_MEMBER = "Add new member"


def display_form_cadet_committee(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    nav_buttons = ButtonBar([cancel_menu_button])
    cadet_table = table_of_all_committee_members(interface)

    suggestions = suggested_cadets_for_next_committee(interface)

    list_of_lines_inside_form = ListOfLines(
        [
            nav_buttons,
            Heading("Edit cadet committee members", size=4),
            suggestions,
            _______________,
            cadet_table,
            _______________,
        ]
    )

    return Form(list_of_lines_inside_form)


def table_of_all_committee_members(interface: abstractInterface) -> Table:
    existing_cadet_rows = table_rows_for_existing_cadets_on_committee(
        interface=interface
    )
    new_cadet_row = table_row_for_new_cadet_on_committee(interface=interface)
    cadet_table = Table([new_cadet_row] + existing_cadet_rows)

    return cadet_table


def table_rows_for_existing_cadets_on_committee(
    interface: abstractInterface,
) -> List[RowInTable]:
    list_of_cadets_with_names_on_committee = get_list_of_cadets_on_committee(
        interface.data
    )
    return [
        get_row_for_existing_cadets_on_committee(cadet_on_committee)
        for cadet_on_committee in list_of_cadets_with_names_on_committee
    ]


def get_row_for_existing_cadets_on_committee(
    cadet_on_committee: CadetOnCommittee,
) -> RowInTable:
    selection_button = select_or_deselect_button(cadet_on_committee)
    return RowInTable(
        [
            cadet_on_committee.cadet.name,
            str(cadet_on_committee.cadet_on_committee.date_term_starts),
            str(cadet_on_committee.cadet_on_committee.date_term_ends),
            cadet_on_committee.cadet_on_committee.status_string(),
            selection_button,
        ]
    )


def select_or_deselect_button(cadet_on_committee: CadetOnCommittee) -> Button:
    if cadet_on_committee.deselected:
        button_text = "Reselect"
    else:
        button_text = "Deselect from committee (can be reinstated)"

    selection_button = Button(
        value=get_select_or_deselect_button_name_for_committee_member(
            cadet_on_committee
        ),
        label=button_text,
    )

    return selection_button


def table_row_for_new_cadet_on_committee(interface: abstractInterface) -> RowInTable:
    dropdown = dropdown_list_of_cadets_not_on_committee(interface)

    (
        start_date_on_committee,
        end_date_on_committee,
    ) = start_and_end_date_on_cadet_commmittee()

    start_date = dateInput(
        input_label="Date term starts",
        input_name=DATE_TERM_STARTS,
        value=start_date_on_committee,
    )
    end_date = dateInput(
        input_label="Date term ends",
        input_name=DATE_TERM_END,
        value=end_date_on_committee,
    )

    return RowInTable(
        [dropdown, start_date, end_date, "Prospective committee member", add_button]
    )


def dropdown_list_of_cadets_not_on_committee(interface: abstractInterface):
    list_of_cadets_not_on_committee_ordered_by_age = (
        get_list_of_cadets_not_on_committee_ordered_by_age(data_layer=interface.data)
    )
    dict_of_members = dict(
        [
            (str(cadet), str(cadet))
            for cadet in list_of_cadets_not_on_committee_ordered_by_age
        ]
    )

    return dropDownInput(
        input_label="",
        input_name=NEW_COMMITTEE_MEMBER_DROPDOWN,
        dict_of_options=dict_of_members,
    )


def suggested_cadets_for_next_committee(
    interface: abstractInterface,
) -> DetailListOfLines:
    next_year_for_committee = get_next_year_for_cadet_committee()
    month_name = month_name_when_cadet_committee_age_bracket_begins()
    list_of_cadets_not_on_committee_born_in_right_age_bracket = (
        get_list_of_cadets_not_on_committee_in_right_age_bracket(
            data_layer=interface.data, next_year_for_committee=next_year_for_committee
        )
    )

    list_of_cadet_as_str_not_on_committee_born_in_right_age_bracket = [
        str(cadet)
        for cadet in list_of_cadets_not_on_committee_born_in_right_age_bracket
    ]

    list_of_lines = ListOfLines(
        [
            "Following to join cadet commmitee after 1st %s %d:"
            % (month_name, next_year_for_committee),
            _______________,
        ]
        + list_of_cadet_as_str_not_on_committee_born_in_right_age_bracket
        + [
            _______________,
            "Not exhaustive - must have downloaded membership list from WA recently and may include lapsed or non-members",
        ]
    )

    list_of_lines = list_of_lines.add_Lines()

    return DetailListOfLines(list_of_lines, name="Suggested members")


def post_form_cadet_committee(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button_pressed = interface.last_button_pressed()
    if cancel_menu_button.pressed(button_pressed):
        return previous_form(interface)
    elif add_button.pressed(button_pressed):
        add_new_cadet_to_committee_from_form(interface)
    elif button_pressed in get_list_of_all_select_or_deselect_button_names(interface):
        select_or_deselect_cadet_from_committee(
            interface=interface, button_name=button_pressed
        )
    else:
        button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return display_form_cadet_committee(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_cadet_committee
    )


## Add new
def add_new_cadet_to_committee_from_form(interface: abstractInterface):
    cadet_selected_as_str = interface.value_from_form(NEW_COMMITTEE_MEMBER_DROPDOWN)
    cadet = get_cadet_given_cadet_as_str(
        data_layer=interface.data, cadet_as_str=cadet_selected_as_str
    )
    date_term_starts = interface.value_from_form(DATE_TERM_STARTS, value_is_date=True)
    date_term_ends = interface.value_from_form(DATE_TERM_END, value_is_date=True)

    add_new_cadet_to_committee(
        data_layer=interface.data,
        cadet=cadet,
        date_term_start=date_term_starts,
        date_term_end=date_term_ends,
    )


## Selection/Deselection
def select_or_deselect_cadet_from_committee(
    interface: abstractInterface, button_name: str
):
    cadet = cadet_from_select_or_deselect_button_name(
        interface=interface, button_name=button_name
    )
    toggle_selection_for_cadet_committee_member(data_layer=interface.data, cadet=cadet)


def cadet_from_select_or_deselect_button_name(
    interface: abstractInterface, button_name: str
) -> Cadet:
    cadet_id = cadet_id_from_select_or_deselect_button_name(button_name)
    cadet = get_cadet_from_id(data_layer=interface.data, cadet_id=cadet_id)

    return cadet


def cadet_id_from_select_or_deselect_button_name(button_name: str) -> str:
    return button_name.split("_")[1]


def get_select_or_deselect_button_name_for_committee_member(
    cadet: CadetOnCommittee,
) -> str:
    return "ds_%s" % cadet.cadet_id


def get_list_of_all_select_or_deselect_button_names(
    interface: abstractInterface,
) -> List[str]:
    list_of_cadets_with_names_on_committee = get_list_of_cadets_on_committee(
        interface.data
    )

    return [
        get_select_or_deselect_button_name_for_committee_member(cadet)
        for cadet in list_of_cadets_with_names_on_committee
    ]


## FIELD NAMES
DATE_TERM_STARTS = "dateTermStart"
DATE_TERM_END = "dateTermEnd"
NEW_COMMITTEE_MEMBER_DROPDOWN = "NewCommDrop"


add_button = Button(ADD_MEMBER)
