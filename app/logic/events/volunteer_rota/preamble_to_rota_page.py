from app.OLD_backend.rota.volunteer_rota_summary import get_summary_list_of_roles_and_groups_for_events, \
    get_summary_list_of_teams_and_groups_for_events
from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS
from app.data_access.configuration.fixed import COPY_OVERWRITE_SYMBOL, COPY_FILL_SYMBOL, SWAP_SHORTHAND, \
    NOT_AVAILABLE_SHORTHAND, REMOVE_SHORTHAND
from app.data_access.data_layer.ad_hoc_cache import AdHocCache

from app.logic.events.volunteer_rota.volunteer_rota_buttons import get_header_buttons_for_rota
from app.logic.events.volunteer_rota.volunteer_targets import get_volunteer_targets_table_and_save_button
from app.logic.events.volunteer_rota.warnings import warn_on_all_volunteers
from app.objects.abstract_objects.abstract_form import Link
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, DetailListOfLines, Line
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import Event


def get_preamble_before_table(interface: abstractInterface, event: Event) -> ListOfLines:

    header_buttons = get_header_buttons_for_rota(interface)
    title = Heading("Volunteer rota for event %s" % str(event), centred=True, size=4)

    cache = interface.cache
    summary_of_filled_roles = get_summary_table(cache=cache, event=event)
    summary_group_table = get_summary_group_table(cache=cache, event=event)
    targets = get_volunteer_targets_table_and_save_button(
        interface=interface, event=event
    )
    warnings = warn_on_all_volunteers(interface)

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
            targets,
            _______________,
            warnings,
            _______________,
            instructions,
            _______________,
        ]
    )


def get_summary_table(cache: AdHocCache, event: Event):
    summary_of_filled_roles = get_summary_list_of_roles_and_groups_for_events(
        event=event, cache=cache
    )
    if len(summary_of_filled_roles) > 0:
        summary_of_filled_roles = DetailListOfLines(
            ListOfLines([summary_of_filled_roles]), name="Summary by role / group"
        )
    else:
        summary_of_filled_roles = ""

    return summary_of_filled_roles


def get_summary_group_table(cache: AdHocCache, event: Event):

    summary_of_filled_roles = get_summary_list_of_teams_and_groups_for_events(
        event=event, cache=cache
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
    string="See qualifications table",
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
