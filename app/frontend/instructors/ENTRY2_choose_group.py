from typing import Union

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_list_of_all_groups_at_event,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.frontend.reporting.sailors.qualification_status import (
    write_expected_qualifications_to_temp_csv_file_and_return_filename,
)

from app.backend.security.user_access import (
    get_list_of_groups_volunteer_can_see,
    can_see_all_groups_and_award_qualifications,
)
from app.frontend.shared.qualification_and_tick_state_storage import (
    update_state_for_group_name,
)
from app.objects.events import Event

from app.backend.security.logged_in_user import (
    get_volunteer_for_logged_in_user_or_superuser,
)
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
from app.frontend.shared.buttons import (
    get_attributes_from_button_pressed_of_known_type,
    get_button_value_given_type_and_attributes,
    is_button_of_type,
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
    volunteer = get_volunteer_for_logged_in_user_or_superuser(interface)
    if can_see_all_groups_and_award_qualifications(
        object_store=interface.object_store,
        event=get_event_from_state(interface),
        volunteer=volunteer,
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

    volunteer = get_volunteer_for_logged_in_user_or_superuser(interface)
    list_of_groups = get_list_of_groups_volunteer_can_see(
        object_store=interface.object_store, event=event, volunteer=volunteer
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
        Button(label=group.name, value=value_for_group_button(group.name), tile=True)
        for group in list_of_groups
    ]

    return Line(list_with_buttons)


def event_is_empty_of_groups(interface: abstractInterface, event: Event) -> bool:
    return (
        len(
            get_list_of_all_groups_at_event(
                object_store=interface.object_store, event=event
            )
        )
        == 0
    )


def post_form_choose_group_for_event(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        ## no change to stage required
        return previous_form(interface)

    elif download_qualification_list_button.pressed(button_pressed):
        filename = write_expected_qualifications_to_temp_csv_file_and_return_filename(
            interface=interface, event=get_event_from_state(interface)
        )
        return File(filename)

    elif is_group_button(button_pressed):
        return action_when_group_button_clicked(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_choose_group_for_event
    )


def action_when_group_button_clicked(interface: abstractInterface) -> NewForm:
    group_name_selected = group_name_from_button(interface.last_button_pressed())
    update_state_for_group_name(interface=interface, group_name=group_name_selected)

    return form_for_view_group_level(interface)


def form_for_view_group_level(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_choose_level_for_group_at_event
    )


group_select_type = "groupSelect"


def value_for_group_button(group_name: str):
    return get_button_value_given_type_and_attributes(group_select_type, group_name)


def is_group_button(button_pressed: str):
    return is_button_of_type(
        value_of_button_pressed=button_pressed, type_to_check=group_select_type
    )


def group_name_from_button(button_pressed: str):
    return get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_pressed, type_to_check=group_select_type
    )
