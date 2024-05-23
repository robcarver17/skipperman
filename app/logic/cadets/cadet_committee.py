import datetime
from typing import Union, List

from app.backend.cadets import get_list_of_cadets_not_on_committee_ordered_by_age, \
    get_list_of_cadets_with_names_on_committee, get_list_of_cadets_not_on_committee_born_after_sept_first_in_year, \
    get_next_year_for_cadet_committee, get_cadet_from_list_of_cadets, add_new_cadet_to_committee, \
    CadetOnCommitteeWithName, toggle_selection_for_cadet_committee_member
from app.objects.abstract_objects.abstract_form import Form, NewForm, dropDownInput, dateInput
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, CANCEL_BUTTON_LABEL
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, DetailListOfLines
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


    nav_buttons = ButtonBar([Button(CANCEL_BUTTON_LABEL, nav_button=True)])

    existing_cadet_rows = table_rows_for_existing_cadets_on_committee(interface=interface)
    new_cadet_row = table_row_for_new_cadet_on_committee(interface=interface)
    cadet_table = Table([new_cadet_row]+existing_cadet_rows)

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


def table_rows_for_existing_cadets_on_committee(interface: abstractInterface) -> List[RowInTable]:
    list_of_cadets_with_names_on_committee = get_list_of_cadets_with_names_on_committee(interface)
    return [get_row_for_existing_cadets_on_committee(cadet_on_committee) for cadet_on_committee in list_of_cadets_with_names_on_committee]

def get_row_for_existing_cadets_on_committee(cadet_on_committee: CadetOnCommitteeWithName) -> RowInTable:
    if cadet_on_committee.cadet_on_committee.deselected:
        button_text = "Reselect"
    else:
        button_text = "Deselect from committee (can be reinstated)"

    button = Button(value=get_select_or_deselect_button_name_for_committee_member(cadet_on_committee.cadet_id),
                    label=button_text)
    return RowInTable([cadet_on_committee.cadet.name,
                      str(cadet_on_committee.cadet_on_committee.date_term_starts),
                      str(cadet_on_committee.cadet_on_committee.date_term_ends),
                       cadet_on_committee.cadet_on_committee.status_string(),
                       button])

def add_button() -> Button:
    return Button(ADD_MEMBER)

def table_row_for_new_cadet_on_committee(interface: abstractInterface) -> RowInTable:
    dropdown = dropdown_list_of_cadets_not_on_committee(interface)

    start_date = dateInput(
        input_label="Date term starts",
        input_name=DATE_TERM_STARTS,
        value=datetime.date(day=1, month=11, year =get_next_year_for_cadet_committee()),
    )
    end_date = dateInput(
        input_label="Date term ends",
        input_name=DATE_TERM_END,
        value=datetime.date(day=1, month=11, year =get_next_year_for_cadet_committee()+2),
    )

    return RowInTable([dropdown, start_date, end_date,  'Prospective committee member', add_button()])

def dropdown_list_of_cadets_not_on_committee(interface: abstractInterface):
    list_of_cadets_not_on_committee_ordered_by_age = get_list_of_cadets_not_on_committee_ordered_by_age(interface=interface)
    dict_of_members = dict(
        [
            (str(cadet), str(cadet)) for cadet in list_of_cadets_not_on_committee_ordered_by_age
        ]
    )

    return dropDownInput(
        input_label ='',
        input_name = NEW_COMMITTEE_MEMBER_DROPDOWN,
        dict_of_options = dict_of_members

    )

NEW_COMMITTEE_MEMBER_DROPDOWN = "NewCommDrop"

def suggested_cadets_for_next_committee(interface: abstractInterface) -> DetailListOfLines:
    next_year_for_committee = get_next_year_for_cadet_committee()
    list_of_cadets_not_on_committee_born_after_sept_first_in_year = get_list_of_cadets_not_on_committee_born_after_sept_first_in_year(
        interface=interface,
        next_year_for_committee=next_year_for_committee
    )

    return DetailListOfLines(ListOfLines([
        "Following are in year 12 on 1st September %d:" % next_year_for_committee,
        _______________,
    ]+[str(cadet) for cadet in list_of_cadets_not_on_committee_born_after_sept_first_in_year]+[_______________, "Not exhaustive - must have downloaded membership list from WA recently and may include lapsed members"]).add_Lines(), name="Suggested members")




def post_form_cadet_committee(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==CANCEL_BUTTON_LABEL:
        return previous_form(interface)
    elif button==ADD_MEMBER:
        add_new_cadet_to_committee_from_form(interface)
    elif button in get_list_of_all_select_or_deselect_button_names(interface):
        cadet_id = cadet_id_from_select_or_deselect_button_name(button)
        toggle_selection_for_cadet_committee_member(interface=interface, cadet_id=cadet_id)
    else:
        button_error_and_back_to_initial_state_form(interface)

    interface.save_stored_items()

    return display_form_cadet_committee(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_cadet_committee)


def add_new_cadet_to_committee_from_form(interface: abstractInterface):

    cadet_selected = interface.value_from_form(NEW_COMMITTEE_MEMBER_DROPDOWN)
    cadet = get_cadet_from_list_of_cadets(interface=interface, cadet_selected=cadet_selected)
    date_term_starts = interface.value_from_form(DATE_TERM_STARTS, value_is_date=True)
    date_term_ends = interface.value_from_form(DATE_TERM_END, value_is_date=True)

    add_new_cadet_to_committee(interface=interface, cadet=cadet, date_term_start=date_term_starts, date_term_end=date_term_ends)

def cadet_id_from_select_or_deselect_button_name(button_name: str) -> str:
    return button_name.split("_")[1]

def get_select_or_deselect_button_name_for_committee_member(cadet_id: str) -> str:
    return "ds_%s" % cadet_id

def get_list_of_all_select_or_deselect_button_names(interface: abstractInterface) -> List[str]:
    list_of_cadets_with_names_on_committee = get_list_of_cadets_with_names_on_committee(interface)

    return [get_select_or_deselect_button_name_for_committee_member(cadet.cadet_id) for cadet in list_of_cadets_with_names_on_committee]

DATE_TERM_STARTS = "dateTermStart"
DATE_TERM_END = "dateTermEnd"
