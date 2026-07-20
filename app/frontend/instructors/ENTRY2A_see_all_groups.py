from dataclasses import dataclass
from typing import Union, Dict, List

import pandas as pd

from app.backend.cadets_at_event.instructor_marked_attendance import \
    mark_unknown_cadets_across_groups_as_not_attending_or_unregistered, get_attendance_on_day_for_all_cadets_at_event
from app.backend.groups.cadets_with_groups_at_event import (
   get_dict_of_cadets_with_groups_at_event,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.instructors.attendance_table import day_given_current_day_and_event
from app.backend.groups.list_of_groups import get_list_of_groups

from app.backend.security.user_access import (

    can_see_all_groups_and_award_qualifications,
)

from app.objects.abstract_objects.abstract_tables import Table, PandasDFTable, RowInTable
from app.objects.cadets import Cadet
from app.objects.composed.attendance import AttendanceOnDay
from app.objects.composed.cadets_at_event_with_groups import DictOfCadetsWithDaysAndGroupsAtEvent
from app.objects.day_selectors import Day
from app.objects.events import Event

from app.backend.security.logged_in_user import (
    get_volunteer_for_logged_in_user_or_superuser,
)
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    _______________,
    MainMenuBar, make_long_thing_detail_box,
)

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    main_menu_button,
    HelpButton,
    back_menu_button,
)

from app.frontend.shared.events_state import (
    get_event_from_state,
    clear_event_id_stored_in_state,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.groups import Group, ListOfGroups


def display_form_see_all_groups_for_event(interface: abstractInterface) -> Union[Form,NewForm]:
    if not user_authorised(interface):
        interface.log_error("Not authorised to see page - log in as skipper or admin level user")
        return previous_form(interface)

    event = get_event_from_state(interface)
    day = day_given_current_day_and_event(interface=interface, event=event, warn=True)
    list_of_rows  =get_cadet_data_as_list_of_rows(interface=interface, event=event, day=day)
    sort_order = get_sort_order(interface)
    list_of_rows.sort_by(sort_order)
    summary = get_summary_table(list_of_rows)
    table = get_table_to_mark_attendance(sorted_list_of_rows=list_of_rows)
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
sort_by_surname = "Surname"
sort_by_firstname = "First name"
sort_by_group = "Group"
sort_by_attendance = "Current attendance"

sort_by_surname_button = Button(sort_by_surname)
sort_by_firstname_button = Button(sort_by_firstname)
sort_by_group_button = Button(sort_by_group)
sort_by_attendance_button = Button(sort_by_attendance)



@dataclass
class RowForCadet:
    cadet: Cadet
    group: Group
    group_order: int
    attendance: AttendanceOnDay

    @property
    def as_row_in_table(self) -> RowInTable:
        return RowInTable([
            self.cadet_first_name,
            self.cadet_surname,
            self.group_name,
            self.current_attendance,
            self.history
        ])

    @property
    def cadet_first_name(self):
        return self.cadet.first_name

    @property
    def cadet_surname(self):
        return self.cadet.surname

    @property
    def group_name(self):
        return self.group.name


    @property
    def current_attendance(self):
        return self.attendance.current_attendance.name

    @property
    def history(self):
        history = ", ".join(self.attendance.history_of_attendance.as_list_of_str())

        return make_long_thing_detail_box(history, "Click triangle to see history")

class ListOfRowsForCadets(List[RowForCadet]):
    def sort_by(self, sort_by:str):
        if sort_by==sort_by_group:
            self.sort_by_group()
        elif sort_by==sort_by_attendance:
            self.sort_by_attendance()
        elif sort_by==sort_by_firstname:
            self.sort_by_first_name()
        elif sort_by==sort_by_surname:
            self.sort_by_surname()
        else:
            raise Exception("%s not known" % sort_by)

    def sort_by_first_name(self):
        # first name, surname
        self.sort(key=lambda x: (x.cadet_first_name, x.cadet_surname))

    def sort_by_surname(self):
        # surname, first name
        self.sort(key=lambda x: (x.cadet_surname, x.cadet_first_name))

    def sort_by_group(self):
        ## group, attendance, first name, surname
        self.sort(key=lambda x: (x.group_order, x.current_attendance, x.cadet_first_name, x.cadet_surname))

    def sort_by_attendance(self):
        ## attendance, first name, surname
        self.sort(key=lambda x: (x.current_attendance, x.cadet_first_name, x.cadet_surname))

def get_summary_table(    sorted_list_of_rows: ListOfRowsForCadets,

):
    all_group_names = list(set([row.group_name for row in sorted_list_of_rows]))
    all_current_attendance= list(set([row.current_attendance for row in sorted_list_of_rows]))

    df = pd.DataFrame(

                 [
                     counts_over_groups(
                         sorted_list_of_rows=sorted_list_of_rows,
                         group_name=group_name,
                         all_current_attendance=all_current_attendance
                     )  for group_name in all_group_names
                 ]
             )
    df.index = all_group_names

    return PandasDFTable(df)

def counts_over_groups(  sorted_list_of_rows: ListOfRowsForCadets, group_name: str, all_current_attendance: List[str]):
    return dict(
        [(current_attendance, count_of_status_and_group_order(
            sorted_list_of_rows=sorted_list_of_rows,
            group_name=group_name,
            current_attendance=current_attendance
        )) for current_attendance in all_current_attendance]
    )

def count_of_status_and_group_order(    sorted_list_of_rows: ListOfRowsForCadets,
                                       group_name: str,
                                        current_attendance: str

):
    return sum([1 for row in sorted_list_of_rows if row.group_name==group_name
                and row.current_attendance==current_attendance])




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

def get_cadet_data_as_list_of_rows(interface: abstractInterface, event: Event,
        day: Day) -> ListOfRowsForCadets:

    mark_unknown_cadets_across_groups_as_not_attending_or_unregistered(
        interface=interface, event=event,  day=day
    )
    current_attendance = get_attendance_on_day_for_all_cadets_at_event(
        interface.object_store, event=event, day=day
    )
    dict_of_cadets_with_groups_at_event = get_dict_of_cadets_with_groups_at_event(object_store=interface.object_store,
                                                                                  event=event)

    list_of_groups = get_list_of_groups(interface.object_store)

    list_of_rows = [row_for_cadet(cadet, day=day,
                                    attendance=attendance,
                                  list_of_groups=list_of_groups,
                                     dict_of_cadets_with_groups_at_event=dict_of_cadets_with_groups_at_event)
                    for cadet, attendance in current_attendance.items()]

    return ListOfRowsForCadets(list_of_rows)

def row_for_cadet(cadet: Cadet, attendance: AttendanceOnDay,
                     day: Day,
                  list_of_groups: ListOfGroups,
                     dict_of_cadets_with_groups_at_event: DictOfCadetsWithDaysAndGroupsAtEvent)-> RowForCadet:

    group = dict_of_cadets_with_groups_at_event.days_and_groups_for_cadet(cadet).group_on_day(day)
    group_idx = list_of_groups.index(group)

    return RowForCadet(cadet=cadet, attendance=attendance, group=group, group_order=group_idx)


def get_sort_order(interface: abstractInterface):
    return interface.get_persistent_value(SORT_ORDER, sort_by_group)

def update_sort_order(interface: abstractInterface, sort_order: str):
    assert sort_order in [sort_by_surname,sort_by_firstname,sort_by_group,sort_by_attendance]
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
    clear_event_id_stored_in_state(interface)
    return interface.get_new_display_form_for_parent_of_function(
        post_form_see_all_groups_for_event
    )




