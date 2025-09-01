from typing import Union

from app.backend.rota.volunteer_rota_summary import (
    get_summary_list_of_roles_and_groups_for_event,
    get_summary_list_of_teams_and_groups_for_events,
)
from app.backend.volunteers.warnings import (
    process_all_warnings_for_rota,
    get_all_saved_warnings_for_volunteer_rota,
)
from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS
from app.data_access.configuration.fixed import (
    COPY_OVERWRITE_SYMBOL,
    COPY_FILL_SYMBOL,
    SWAP_SHORTHAND,
    NOT_AVAILABLE_SHORTHAND,
    REMOVE_SHORTHAND,
)

from app.frontend.events.volunteer_rota.volunteer_rota_buttons import (
    get_header_buttons_for_rota,
)
from app.frontend.events.volunteer_rota.volunteer_targets_and_group_notes import (
    get_volunteer_targets_table_and_save_button,
)

from app.frontend.events.volunteer_rota.volunteer_targets_and_group_notes import (
    get_summary_instructor_group_table,
)
from app.frontend.forms.swaps import is_ready_to_swap
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.warnings_table import display_warnings_tables
from app.objects.abstract_objects.abstract_form import Link
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    DetailListOfLines,
    Line,
)
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import Event


def get_preamble_before_table(
    interface: abstractInterface, event: Event
) -> ListOfLines:
    title = Heading("Volunteer rota for event %s" % str(event), centred=True, size=4)
    header_buttons = get_header_buttons_for_rota(interface)
    if is_ready_to_swap(interface):
        return ListOfLines(
            [
                header_buttons,
                title,
                _______________,
                Heading("Swapping: click on swapper or cancel", size=3, centred=True),
            ]
        )

    summary_of_filled_roles = get_summary_table(interface=interface, event=event)
    summary_group_table = get_summary_group_table(interface=interface, event=event)
    summary_instructor_table = get_summary_instructor_group_table(
        interface=interface, event=event
    )
    targets = get_volunteer_targets_table_and_save_button(
        interface=interface, event=event
    )
    warnings = get_volunteer_warning_table(interface)

    return ListOfLines(
        [
            header_buttons,
            title,
            _______________,
            _______________,
            summary_of_filled_roles,
            _______________,
            summary_group_table,
            _______________,
            summary_instructor_table,
            _______________,
            targets,
            _______________,
        ]
        + warnings
        + [
            _______________,
            instructions,
            _______________,
        ]
    )


def get_summary_table(interface: abstractInterface, event: Event):
    summary_of_filled_roles = get_summary_list_of_roles_and_groups_for_event(
        event=event, object_store=interface.object_store
    )
    if len(summary_of_filled_roles) > 0:
        summary_of_filled_roles = DetailListOfLines(
            ListOfLines([summary_of_filled_roles]), name="Summary by role / group"
        )
    else:
        summary_of_filled_roles = ""

    return summary_of_filled_roles


def get_summary_group_table(interface: abstractInterface, event: Event):
    summary_of_filled_roles = get_summary_list_of_teams_and_groups_for_events(
        event=event, object_store=interface.object_store
    )
    if len(summary_of_filled_roles) > 0:
        summary_of_filled_roles = DetailListOfLines(
            ListOfLines([summary_of_filled_roles]), name="Summary by team/ group"
        )
    else:
        summary_of_filled_roles = ""

    return summary_of_filled_roles


link = Link(
    url=WEBLINK_FOR_QUALIFICATIONS,
    string="See qualifications_and_ticks table",
    open_new_window=True,
)
instructions = ListOfLines(
    [
        "CANCEL will cancel any changes you make; any other button will save them",
        Line(
            [
                "Key for buttons: Copy, fill and overwrite existing ",
                COPY_OVERWRITE_SYMBOL,
                " ; Copy and fill any unallocated days ",
                COPY_FILL_SYMBOL,
                " ; Swap ",
                SWAP_SHORTHAND,
                " ; Raincheck - make unavailable: ",
                NOT_AVAILABLE_SHORTHAND,
                " ; Remove role - but keep as available ",
                REMOVE_SHORTHAND,
            ]
        ),
        link,
    ]
).add_Lines()


def get_volunteer_warning_table(
    interface: abstractInterface,
) -> ListOfLines:
    event = get_event_from_state(interface)
    process_all_warnings_for_rota(object_store=interface.object_store, event=event)
    interface.flush_cache_to_store()

    all_warnings = get_all_saved_warnings_for_volunteer_rota(
        object_store=interface.object_store, event=event
    )

    return display_warnings_tables(all_warnings)
