from typing import Union

from app.data_access.sql.transfer import transfer_from_sql_to_csv, transfer_from_csv_to_sql
from app.objects.abstract_objects.abstract_text import Heading

from app.data_access.backups.find_and_restore_backups import delete_all_master_data
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    back_menu_button,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.administration.data.merge_delete_cadets import (
    display_form_merge_delete_cadets,
)
from app.frontend.administration.data.merge_delete_volunteers import (
    display_form_merge_delete_volunteers,
)
from app.frontend.administration.data.edit_delete_events import (
    display_form_edit_delete_events,
)

merge_cadet_option = Button("Merge / delete sailor", tile=True)
merge_volunteer_option = Button("Merge / delete volunteer", tile=True)
edit_event = Button("Edit / Delete event", tile=True)
sql_to_csv = Button("Write SQL data as CSV", tile=True)
csv_to_sql = Button("Write CSV data as SQL", tile=True)

option_buttons = Line([edit_event, merge_cadet_option, merge_volunteer_option, sql_to_csv, csv_to_sql])

nav_buttons = ButtonBar([back_menu_button])


def display_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    lines_inside_form = ListOfLines([nav_buttons, option_buttons])

    return Form(lines_inside_form)


def post_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if back_menu_button.pressed(last_button):
        return interface.get_new_display_form_for_parent_of_function(post_form_data)

    if merge_cadet_option.pressed(last_button):
        return interface.get_new_form_given_function(display_form_merge_delete_cadets)
    elif merge_volunteer_option.pressed(last_button):
        return interface.get_new_form_given_function(
            display_form_merge_delete_volunteers
        )
    elif edit_event.pressed(last_button):
        return interface.get_new_form_given_function(display_form_edit_delete_events)
    elif sql_to_csv.pressed(last_button):
        transfer_from_sql_to_csv()
        interface.log_error("Done SQL to CSV")
        return interface.get_new_form_given_function(display_form_data)
    elif csv_to_sql.pressed(last_button):
        transfer_from_csv_to_sql()
        interface.log_error("Done CSV to SQL")
        return interface.get_new_form_given_function(display_form_data)
    else:
        return button_error_and_back_to_initial_state_form(interface)
