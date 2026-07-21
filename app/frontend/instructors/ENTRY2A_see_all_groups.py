from typing import Union


from app.backend.cadets_at_event.summary_attendance import sort_by_surname, \
    sort_by_firstname, sort_by_group, sort_by_attendance, get_cadet_data_as_list_of_rows_for_cadets, \
    ListOfRowsForCadets, get_summary_table_as_df
from app.data_access.store.object_store import ObjectStore
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.instructors.attendance_table import day_given_current_day_and_event

from app.backend.security.user_access import (

    can_see_all_groups_and_award_qualifications,
)

from app.objects.abstract_objects.abstract_tables import Table, PandasDFTable, RowInTable
from app.objects.events import Event

from app.backend.security.logged_in_user import (
    get_volunteer_for_logged_in_user_or_superuser,
)
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    _______________,
    MainMenuBar, )

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    main_menu_button,
    HelpButton,
    back_menu_button,
)

from app.frontend.shared.events_state import (
    get_event_from_state,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.groups import ListOfGroups


def display_form_see_all_groups_for_event(interface: abstractInterface) -> Union[Form,NewForm]:
    if not user_authorised(interface):
        interface.log_error("Not authorised to see page - log in as skipper or admin level user")
        return previous_form(interface)

    event = get_event_from_state(interface)
    sorted_list_of_rows = get_sorted_rows_for_cadets(interface, event=event)
    summary = get_summary_table(object_store=interface.object_store, sorted_list_of_rows=sorted_list_of_rows)
    table = get_table_to_mark_attendance(sorted_list_of_rows=sorted_list_of_rows)
    navbar = get_nav_bar()
    header = Line(
        Heading(
            "See all registered sailors at %s"
            % str(event),
            centred=False,
            size=4,
        )
    )
    lines_inside_form = ListOfLines(
        [
            MainMenuBar("Instructors"),
            _______________,
            navbar,
            _______________,
            header,
            _______________,
            summary,
            _______________,
            Line("Click button to sort by relevant column"),
            table,
            _______________,
        ]
    )

    return Form(lines_inside_form)

def user_authorised(interface: abstractInterface):
    volunteer = get_volunteer_for_logged_in_user_or_superuser(interface)
    return  can_see_all_groups_and_award_qualifications(
        object_store=interface.object_store,
        event=get_event_from_state(interface),
        volunteer=volunteer)


def get_nav_bar():
    help = HelpButton("see_all_groups_help")
    navbar = [main_menu_button, back_menu_button, help]

    return ButtonBar(navbar)


SORT_ORDER = "sort_order"

sort_by_surname_button = Button(sort_by_surname)
sort_by_firstname_button = Button(sort_by_firstname)
sort_by_group_button = Button(sort_by_group)
sort_by_attendance_button = Button(sort_by_attendance)

def get_sorted_rows_for_cadets(interface: abstractInterface, event: Event) -> ListOfRowsForCadets:
    day = day_given_current_day_and_event(interface=interface, event=event, warn=True)
    list_of_rows  =get_cadet_data_as_list_of_rows_for_cadets(interface=interface, event=event, day=day)
    sort_order = get_sort_order(interface)
    list_of_rows.sort_by(sort_order)

    return list_of_rows

def get_summary_table(object_store: ObjectStore, sorted_list_of_rows: ListOfRowsForCadets,

                      ):

    df=get_summary_table_as_df(object_store=object_store, sorted_list_of_rows=sorted_list_of_rows)

    return PandasDFTable(df)



def get_table_to_mark_attendance(
    sorted_list_of_rows: ListOfRowsForCadets
) -> Table:
    top_row = [get_top_row()]
    body = [row_in_table.as_row_in_table for row_in_table in sorted_list_of_rows]

    return Table(top_row+body, has_column_headings=True)

def get_top_row():
    return RowInTable([sort_by_firstname_button,
                       sort_by_surname_button,
                       sort_by_group_button,sort_by_attendance_button, "History"])


def get_sort_order(interface: abstractInterface):
    return interface.get_persistent_value(SORT_ORDER, sort_by_group)

def update_sort_order(interface: abstractInterface, sort_order: str):
    assert sort_order in [sort_by_surname, sort_by_firstname, sort_by_group, sort_by_attendance]
    interface.set_persistent_value(SORT_ORDER, sort_order)


def post_form_see_all_groups_for_event(
    interface: abstractInterface,
) -> NewForm:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        ## no change to stage required
        return previous_form(interface)
    elif sort_by_group_button.pressed(button_pressed):
        update_sort_order(interface, sort_by_group)
    elif sort_by_attendance_button.pressed(button_pressed):
        update_sort_order(interface, sort_by_attendance)
    elif sort_by_firstname_button.pressed(button_pressed):
        update_sort_order(interface, sort_by_firstname)
    elif sort_by_surname_button.pressed(button_pressed):
        update_sort_order(interface, sort_by_surname)
    else:
        return button_error_and_back_to_initial_state_form(interface)

    return interface.get_new_form_given_function(display_form_see_all_groups_for_event)

def previous_form(interface: abstractInterface):

    return interface.get_new_display_form_for_parent_of_function(
        post_form_see_all_groups_for_event
    )




