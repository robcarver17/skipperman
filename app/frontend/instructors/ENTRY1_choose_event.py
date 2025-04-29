import os.path
from typing import Union

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.reporting.sailors.achieved_qualifications import (
    write_qualifications_to_temp_csv_file_and_return_filename,
)

from app.data_access.file_access import (
    get_files_in_directory,
)
from app.data_access.init_directories import public_reporting_directory

from app.frontend.shared.events_state import (
    update_state_for_specific_event,
)

from app.backend.events.list_of_events import (
    all_sort_types_for_event_list,
)
from app.backend.security.user_access import (
    get_list_of_events_entitled_to_see,
    is_volunteer_SI_or_super_user,
)

from app.objects.abstract_objects.abstract_text import Heading

from app.frontend.shared.event_selection import display_given_list_of_events_with_buttons
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    ButtonBar,
    Button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
    DetailListOfLines,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.security.logged_in_user import (
    get_volunteer_for_logged_in_user_or_superuser,
)
from app.objects.events import SORT_BY_START_DSC
from app.frontend.instructors.ENTRY2_choose_group import (
    display_form_choose_group_for_event,
)
from app.frontend.shared.buttons import get_attributes_from_button_pressed_of_known_type, is_button_of_type, \
    get_button_value_given_type_and_attributes, is_button_sort_order, \
    sort_order_from_button_pressed, get_button_value_for_sort_order, is_button_event_selection, \
    event_from_button_pressed


def display_form_main_instructors_page(interface: abstractInterface) -> Form:
    return display_form_main_instructors_page_sort_order_passed(
        interface=interface, sort_by=SORT_BY_START_DSC
    )


def display_form_main_instructors_page_sort_order_passed(
    interface: abstractInterface, sort_by: str
) -> Form:
    event_buttons = get_event_buttons(interface=interface, sort_by=sort_by)
    navbar = get_nav_bar(interface=interface)
    sort_buttons = sort_buttons_for_event_list
    reports = list_of_all_files_in_public_directory_with_clickable_buttons()
    header1 = Line(get_heading(interface))
    header2 = Line(Heading("Select report/document", centred=False, size=4))
    header3 = Line(Heading("Select event to see ticksheet", centred=False, size=4))

    report_detail = DetailListOfLines(
        ListOfLines(
            [
                _______________,
                header2,
                reports,
                _______________,
            ]
        ),
        name="Click triangle to see downloadable documents",
    )

    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header1,
            report_detail,
            header3,
            sort_buttons,
            _______________,
            event_buttons,
        ]
    )

    return Form(lines_inside_form)


def get_heading(interface: abstractInterface):
    if is_volunteer_SI_or_super_user(interface):
        text = "Tick sheets and documents for senior instructors and skippers"
    else:
        text = "Tick sheets and documents for instructors"

    return Heading(text, centred=True, size=3)


def get_nav_bar(interface: abstractInterface):
    navbar = [main_menu_button]
    if is_volunteer_SI_or_super_user(interface):
        navbar.append(download_qualification_list_button)
        help = HelpButton("ticksheets_SI_skipper_help")
    else:
        help = HelpButton("ticksheets_help")

    navbar.append(help)
    return ButtonBar(navbar)


DOWNLOAD_QUALIFICATION_LIST = "Download qualification list"
download_qualification_list_button = Button(
    DOWNLOAD_QUALIFICATION_LIST, nav_button=True
)


def post_form_main_instructors_page(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()
    if is_button_sort_order(button_pressed):
        ## no change to stage required
        sort_by = sort_order_from_button_pressed(button_pressed)
        return display_form_main_instructors_page_sort_order_passed(
            interface=interface, sort_by=sort_by
        )

    elif is_filename_button_pressed(button_pressed):
        return get_file_given_button_pressed(button_pressed)

    elif download_qualification_list_button.pressed(button_pressed):
        filename = write_qualifications_to_temp_csv_file_and_return_filename(
            interface.object_store
        )
        return File(filename)

    elif is_button_event_selection(button_pressed):
        return action_when_event_button_clicked(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


def get_file_given_button_pressed(button_pressed: str) -> File:
    filename = filename_from_pressed_button(button_pressed)
    return File(os.path.join(public_reporting_directory, filename))


def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event = event_from_button_pressed(value_of_button_pressed=interface.last_button_pressed(), object_store=interface.object_store)
    update_state_for_specific_event(interface=interface, event=event)

    return form_for_view_event(interface)


def form_for_view_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_choose_group_for_event)


def get_event_buttons(interface: abstractInterface, sort_by: str) -> Line:
    volunteer = get_volunteer_for_logged_in_user_or_superuser(interface)
    list_of_events = get_list_of_events_entitled_to_see(
        object_store=interface.object_store, volunteer=volunteer, sort_by=sort_by
    )
    return display_given_list_of_events_with_buttons(list_of_events)


def list_of_all_files_in_public_directory_with_clickable_buttons() -> ListOfLines:
    all_files = get_files_in_directory(public_reporting_directory)

    return ListOfLines(
        [line_for_file_in_directory(filename=filename) for filename in all_files]
    ).add_Lines()


def line_for_file_in_directory(filename: str):
    return Button(label=filename, value = get_button_value_for_filename(filename))

select_file = "selectFileType"
def get_button_value_for_filename(filename:str):
    return get_button_value_given_type_and_attributes(
        select_file,
        filename
    )

def is_filename_button_pressed(value_of_button:str):
    return is_button_of_type(type_to_check=select_file, value_of_button_pressed=value_of_button)

def filename_from_pressed_button(value_of_button:str) ->str:
    return get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=value_of_button,
        type_to_check=select_file
    )

sort_buttons_for_event_list = ButtonBar(
    [Button(label=sortby, value=get_button_value_for_sort_order(sortby),nav_button=True) for sortby in all_sort_types_for_event_list]
)
