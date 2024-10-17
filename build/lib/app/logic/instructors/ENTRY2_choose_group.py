from typing import Union

from app.frontend.reporting.qualifications.qualification_status import (
    write_expected_qualifications_to_temp_csv_file_and_return_filename,
)

from app.backend.qualifications_and_ticks.ticksheets import (
    get_list_of_all_groups_at_event,
)
from app.backend.security.user_access import get_list_of_groups_volunteer_can_see, \
    can_see_all_groups_and_award_qualifications
from app.frontend.shared.qualification_and_tick_state_storage import (
    update_state_for_group_name,
)
from app.objects.events import Event

from app.backend.security.logged_in_user import get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    _______________,
)

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    main_menu_button,
    HelpButton,
    back_menu_button,
)

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.instructors.ENTRY3_choose_level import (
    display_form_choose_level_for_group_at_event,
)


def display_form_choose_group_for_event(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    group_buttons = get_group_buttons(interface=interface, event=event)
    navbar = get_nav_bar(interface)
    header = Line(
        Heading(
            "Tick sheets and reports for instructors: Event: %s; Select group"
            % str(event),
            centred=False,
            size=4,
        )
    )
    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header,
            _______________,
            _______________,
            group_buttons,
        ]
    )

    return Form(lines_inside_form)


def get_nav_bar(interface: abstractInterface):
    navbar = [main_menu_button, back_menu_button]
    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER(interface)
    if can_see_all_groups_and_award_qualifications(
        interface=interface,
        event=get_event_from_state(interface),
        volunteer_id=volunteer_id,
    ):
        navbar.append(download_qualification_list_button)
        help = HelpButton("ticksheets_choose_group_SI_skipper_help")
    else:
        help = HelpButton("ticksheets_choose_group_help")

    navbar.append(help)

    return ButtonBar(navbar)


DOWNLOAD_QUALIFICATION_LIST = "Download qualification progress for registered cadets"
download_qualification_list_button = Button(
    DOWNLOAD_QUALIFICATION_LIST, nav_button=True
)


def get_group_buttons(interface: abstractInterface, event: Event) -> Line:
    if event_is_empty_of_groups(interface=interface, event=event):
        return Line(Heading("No groups defined at this event yet"))

    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER(interface)
    list_of_groups = get_list_of_groups_volunteer_can_see(
        interface=interface, event=event, volunteer_id=volunteer_id
    )

    if len(list_of_groups) == 0:
        return Line(
            Heading(
                "The user doesn't have right to see any ticksheets for event %s; must be skipper, admin, SI for event, or DI/AI/RCL2 for a group"
                % str(event),
                centred=False,
                size=4,
            )
        )

    list_with_buttons = [
        Button(group.name, tile=True) for group in list_of_groups
    ]

    return Line(list_with_buttons)


def event_is_empty_of_groups(interface: abstractInterface, event: Event) -> bool:
    return len(get_list_of_all_groups_at_event(interface=interface, event=event)) == 0


def post_form_choose_group_for_event(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        ## no change to stage required
        return previous_form(interface)
    elif button_pressed == DOWNLOAD_QUALIFICATION_LIST:
        filename = write_expected_qualifications_to_temp_csv_file_and_return_filename(
            interface=interface, event=get_event_from_state(interface)
        )
        return File(filename)
    else:  ## must be a group
        return action_when_group_button_clicked(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_choose_group_for_event
    )


def action_when_group_button_clicked(interface: abstractInterface) -> NewForm:
    group_name_selected = interface.last_button_pressed()
    update_state_for_group_name(interface=interface, group_name=group_name_selected)

    return form_for_view_level(interface)


def form_for_view_level(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_choose_level_for_group_at_event
    )
