import os.path
from typing import Union

from app.logic.reporting.qualifications.achieved_qualifications import (
    write_qualifications_to_temp_csv_file_and_return_filename,
)

from app.data_access.file_access import (
    get_files_in_directory,
    public_reporting_directory,
)

from app.logic.shared.events_state import (
    update_state_for_specific_event_given_event_description,
)

from app.OLD_backend.events import (
    sort_buttons_for_event_list,
    all_sort_types_for_event_list,
    confirm_event_exists_given_description,
)
from app.OLD_backend.ticks_and_qualifications.ticksheets import (
    get_list_of_events_entitled_to_see,
    is_volunteer_SI_or_super_user,
)

from app.objects.abstract_objects.abstract_text import Heading

from app.logic.events.ENTRY_view_events import display_given_list_of_events_with_buttons
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
from app.OLD_backend.data.security import get_volunteer_id_of_logged_in_user_or_superuser
from app.objects.events import SORT_BY_START_DSC
from app.logic.instructors.ENTRY2_choose_group import (
    display_form_choose_group_for_event,
)


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
    if button_pressed in all_sort_types_for_event_list:
        ## no change to stage required
        sort_by = interface.last_button_pressed()
        return display_form_main_instructors_page_sort_order_passed(
            interface=interface, sort_by=sort_by
        )
    elif button_pressed in list_of_file_buttons():
        return File(os.path.join(public_reporting_directory, button_pressed))
    elif button_pressed == DOWNLOAD_QUALIFICATION_LIST:
        filename = write_qualifications_to_temp_csv_file_and_return_filename(interface)
        return File(filename)
    else:  ## must be an event
        return action_when_event_button_clicked(interface)


def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event_description_selected = interface.last_button_pressed()
    confirm_event_exists_given_description(
        interface=interface, event_description=event_description_selected
    )
    update_state_for_specific_event_given_event_description(
        interface=interface, event_description=event_description_selected
    )

    return form_for_view_event(interface)


def form_for_view_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_choose_group_for_event)


def get_event_buttons(interface: abstractInterface, sort_by: str) -> Line:
    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser(interface)
    list_of_events = get_list_of_events_entitled_to_see(
        interface=interface, volunteer_id=volunteer_id, sort_by=sort_by
    )
    return display_given_list_of_events_with_buttons(list_of_events)


def list_of_all_files_in_public_directory_with_clickable_buttons() -> ListOfLines:
    all_files = get_files_in_directory(public_reporting_directory)

    return ListOfLines(
        [line_for_file_in_directory(filename=filename) for filename in all_files]
    ).add_Lines()


def line_for_file_in_directory(filename: str):
    return Button(filename)


def list_of_file_buttons():
    all_files = get_files_in_directory(public_reporting_directory)
    return all_files
