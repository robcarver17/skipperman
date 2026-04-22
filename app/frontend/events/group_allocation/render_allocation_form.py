from typing import Union, List

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)
from app.backend.groups.group_allocation_info import (
    get_group_allocation_info,
)
from app.backend.groups.previous_groups import (
    get_list_of_previous_groups_as_str,
    get_dict_of_event_allocations_given_list_of_events_from_persistent_data,
)

from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    ListOfBoatGroupings,
)
from app.objects.composed.cadets_at_event_with_groups import (
    DictOfEventAllocations,
    GroupAllocationInfo,
)
from app.backend.qualifications_and_ticks.progress import (
    get_qualification_status_for_single_cadet_as_list_of_str,
)
from app.backend.qualifications_and_ticks.qualifications_for_cadet import (
    name_of_highest_qualification_for_cadet,
)
from app.data_access.configuration.fixed import ADD_KEYBOARD_SHORTCUT
from app.frontend.events.group_allocation.buttons import (
    get_day_buttons,
    button_to_click_on_cadet,
    button_to_click_on_cadet_when_already_selected,
)
from app.frontend.shared.check_security import is_admin_or_skipper
from app.frontend.shared.club_dinghies import get_club_dinghies_detail
from app.frontend.events.group_allocation.previous_events import (
    get_previous_event_selection_form,
    get_prior_events_to_show,
)
from app.frontend.shared.cadet_state import get_cadet_from_state
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets

from app.objects.utilities.exceptions import MissingData

from app.frontend.events.group_allocation.input_fields import (
    get_notes_field,
    get_days_attending_field,
    get_input_fields_for_cadet,
    guess_boat_button,
)
from app.frontend.events.group_allocation.store_state import (
    no_day_set_in_state,
    get_day_from_state_or_none,
)

from app.backend.boat_classes.summary import summarise_class_attendance_for_event
from app.backend.groups.sorting import sorted_active_cadets, SortOrderGroups
from app.backend.events.summarys import summarise_allocations_for_event

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    save_menu_button,
    HelpButton,
    save_and_back_menu_button,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    DetailListOfLines,
    Line,
    make_long_thing_detail_box,
    MainMenuBar,
)
from app.objects.abstract_objects.abstract_tables import (
    Table,
    RowInTable,
    PandasDFTable,
)
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.events import (
    Event,
)
from app.objects.utilities.utils import SimpleTimer


def display_form_allocate_cadets_at_event(
    interface: abstractInterface, event: Event, sort_order: SortOrderGroups
) -> Union[Form, NewForm]:
    st = SimpleTimer()
    allocations_and_class_summary = get_allocations_and_classes_detail(
        event=event, interface=interface
    )
    st.elapsed("1: display allocations")
    clicker_line = (
        Line(
            "Click on another cadet name to show history / Click on cadet with history showing to hide"
        )
        if any_cadet_clicked_on(interface)
        else Line("Click on a cadet name to show history and qualifications")
    )
    day_buttons = get_day_buttons(interface)
    sort_line = get_sort_line(sort_order)
    inner_form = get_inner_form_for_cadet_allocation(
        interface=interface, event=event, sort_order=sort_order
    )
    st.elapsed("1: inner form")
    return Form(
        ListOfLines(
            [
                MainMenuBar("Events"),
                _______________,
                get_nav_bar_top(interface),
                Heading(
                    "Cadets in %s: Allocate groups, boats and sailing partners"
                    % str(event),
                    size=3,
                ),
                _______________,
                _______________,
                allocations_and_class_summary,
                _______________,
                _______________,
                sort_line,
                _______________,
                day_buttons,
                _______________,
                clicker_line,
                _______________,
                inner_form,
                _______________,
                get_nav_bar_bottom(interface),
            ]
        )
    )


help_button = HelpButton("group_allocation_help")
add_button = Button(
    "Add unregistered sailor", nav_button=True, shortcut=ADD_KEYBOARD_SHORTCUT
)
quick_group_report_button = Button("Quick group report", nav_button=True)
quick_spotters_report_button = Button("Quick spotters report", nav_button=True)
update_group_names_button = Button("Update past groups for cadets", nav_button=True)


def get_nav_bar_top(interface: abstractInterface):
    if is_admin_or_skipper(interface):
        return ButtonBar(
            [
                cancel_menu_button,
                save_menu_button,
                save_and_back_menu_button,
                guess_boat_button,
                add_button,
                quick_group_report_button,
                quick_spotters_report_button,
                update_group_names_button,
                help_button,
            ]
        )
    else:
        return ButtonBar(
            [
                cancel_menu_button,
                save_menu_button,
                save_and_back_menu_button,
                quick_spotters_report_button,
                help_button,
            ]
        )


def get_nav_bar_bottom(interface: abstractInterface):
    if is_admin_or_skipper(interface):
        return ButtonBar(
            [
                cancel_menu_button,
                save_menu_button,
                save_and_back_menu_button,
                add_button,
                help_button,
            ]
        )
    else:
        return ButtonBar(
            [
                cancel_menu_button,
                save_and_back_menu_button,
                save_menu_button,
                help_button,
            ]
        )


def get_allocations_and_classes_detail(
    interface: abstractInterface, event: Event
) -> ListOfLines:
    allocations = get_allocations_detail(interface=interface, event=event)
    club_dinghies = get_club_dinghies_detail(interface=interface, event=event)
    classes = get_classes_detail(interface=interface, event=event)
    previous_event_selection_form = get_previous_event_selection_detail(
        interface=interface, event=event
    )

    return ListOfLines(
        [
            _______________,
            allocations,
            _______________,
            club_dinghies,
            _______________,
            classes,
            _______________,
            previous_event_selection_form,
        ]
    )


def get_allocations_detail(interface: abstractInterface, event: Event):
    allocations = PandasDFTable(
        summarise_allocations_for_event(
            object_store=interface.object_store, event=event
        )
    )
    if len(allocations) == 0:
        allocations = "No group allocations made"
    else:
        allocations = DetailListOfLines(
            ListOfLines([allocations]), name="Groups allocated"
        )

    return allocations


def get_classes_detail(interface: abstractInterface, event: Event):
    classes = PandasDFTable(
        summarise_class_attendance_for_event(
            event=event, object_store=interface.object_store
        )
    )
    if len(classes) == 0:
        classes = "No boat classes allocated"
    else:
        classes = DetailListOfLines(ListOfLines([classes]), name="Boat classes")

    return classes


def get_previous_event_selection_detail(interface: abstractInterface, event: Event):
    if is_admin_or_skipper(interface):
        return DetailListOfLines(
            get_previous_event_selection_form(interface=interface, event=event),
            name="Select previous events to show",
        )
    else:
        return ""


def get_sort_line(sort_order: SortOrderGroups):
    current_sort_order = ", ".join(sort_order.sort_order_as_list)
    keep_groups_together = (
        "(Keep helm/crew pairs together)" if sort_order.keep_pairs_together else ""
    )
    sort_line = Line(
        [
            "Current sort order: %s %s" % (current_sort_order, keep_groups_together),
            "    ",
            sort_order_change_button,
        ]
    )

    return sort_line


sort_order_change_button = Button("Change sort order")


def get_inner_form_for_cadet_allocation(
    interface: abstractInterface, event: Event, sort_order: SortOrderGroups
) -> Table:
    st = SimpleTimer()
    object_store = interface.object_store
    dict_of_all_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event
    )
    st.elapsed("2: all cadet data")

    day_or_none = get_day_from_state_or_none(interface)
    list_of_cadets = sorted_active_cadets(
        object_store=object_store,
        dict_of_all_event_data=dict_of_all_event_data,
        sort_order=sort_order,
        day_or_none=day_or_none,
    )
    st.elapsed("2: sorted active cadets")
    prior_events = get_prior_events_to_show(interface=interface, event=event)
    previous_groups_for_cadets = (
        get_dict_of_event_allocations_given_list_of_events_from_persistent_data(
            object_store=object_store,
            list_of_cadets=list_of_cadets,
            list_of_events=prior_events,
        )
    )
    st.elapsed("2: previous groups")

    group_allocation_info = get_group_allocation_info(dict_of_all_event_data)
    st.elapsed("3: group allocation dict")

    top_row = get_top_row(
        previous_groups_for_cadets=previous_groups_for_cadets,
        group_allocation_info=group_allocation_info,
        interface=interface,
    )
    body = get_body_of_table_for_cadet_allocation(
        previous_groups_for_cadets=previous_groups_for_cadets,
        group_allocation_info=group_allocation_info,
        list_of_cadets=list_of_cadets,
        interface=interface,
        dict_of_all_event_data=dict_of_all_event_data,
    )
    st.elapsed("3: body of table")
    return Table(
        [top_row] + body,
        has_column_headings=True,
        has_row_headings=True,
    )


NUMBER_OF_PREVIOUS_EVENTS = 3


def get_top_row(
    interface: abstractInterface,
    previous_groups_for_cadets: DictOfEventAllocations,
    group_allocation_info: GroupAllocationInfo,
) -> RowInTable:
    previous_event_names_in_list = (
        previous_groups_for_cadets.list_of_events.list_of_names()
    )
    info_field_names = group_allocation_info.visible_field_names()

    input_field_names_over_days = get_daily_input_field_headings(interface=interface)

    if is_admin_or_skipper(interface):
        return RowInTable(
            ["", "Set Availability"]  ## cadet name
            + previous_event_names_in_list
            + info_field_names
            + ["Official qualification", "Notes"]
            + input_field_names_over_days
        )
    else:
        return RowInTable([""] + input_field_names_over_days)  ## cadet name


def get_daily_input_field_headings(interface: abstractInterface) -> list:
    if no_day_set_in_state(interface):
        return get_input_field_headings_for_day("All days")
    else:
        day = get_day_from_state_or_none(interface)
        return get_input_field_headings_for_day(day.name)


def get_input_field_headings_for_day(day_name: str) -> list:
    input_field_names = [
        "Allocate: group (%s)" % day_name,
        "Allocate: Club boat(%s)" % day_name,
        "Allocate: Class of boat (%s)" % (day_name),
        "Edit: Sail number (%s)" % (day_name),
        "Allocate: Two handed partner (%s) *=schedule conflict" % day_name,
    ]

    return input_field_names


def get_body_of_table_for_cadet_allocation(
    interface: abstractInterface,
    group_allocation_info: GroupAllocationInfo,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    previous_groups_for_cadets: DictOfEventAllocations,
    list_of_cadets: ListOfCadets,
) -> List[RowInTable]:
    list_of_boat_groupings = ListOfBoatGroupings(
        dict_of_all_event_data.dict_of_cadets_and_boat_class_and_partners
    )
    table_rows = [
        get_row_for_cadet(
            interface=interface,
            previous_groups_for_cadets=previous_groups_for_cadets,
            group_allocation_info=group_allocation_info,
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            list_of_boat_groupings=list_of_boat_groupings,
        )
        for cadet in list_of_cadets
    ]
    return table_rows


def get_row_for_cadet(
    interface: abstractInterface,
    previous_groups_for_cadets: DictOfEventAllocations,
    group_allocation_info: GroupAllocationInfo,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_boat_groupings: ListOfBoatGroupings,
    cadet: Cadet,
) -> RowInTable:
    cell_for_cadet = get_cell_for_cadet(
        interface=interface,
        event=dict_of_all_event_data.event,
        cadet=cadet,
    )
    previous_groups_as_list = (
        previous_groups_for_cadets.previous_group_names_for_cadet_as_list(cadet)
    )
    group_info = group_allocation_info.group_info_dict_for_cadet_as_ordered_list(cadet)
    group_info = [make_long_thing_detail_box(field) for field in group_info]
    qualification = str(
        name_of_highest_qualification_for_cadet(
            object_store=interface.object_store, cadet=cadet
        )
    )
    notes_field = get_notes_field(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    days_attending_field = get_days_attending_field(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    input_fields = get_input_fields_for_cadet(
        interface=interface,
        cadet=cadet,
        dict_of_all_event_data=dict_of_all_event_data,
        list_of_boat_groupings=list_of_boat_groupings,
    )
    if is_admin_or_skipper(interface):
        return RowInTable(
            [cell_for_cadet, days_attending_field]
            + previous_groups_as_list
            + group_info
            + [qualification, notes_field]
            + input_fields
        )
    else:
        return RowInTable([str(cadet)] + input_fields)


MAX_EVENTS_TO_SHOW = 10


def get_cell_for_cadet(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> Union[ListOfLines, Button]:
    if this_cadet_has_been_clicked_on_already(interface=interface, cadet=cadet):
        return get_cell_for_cadet_that_is_clicked_on(
            interface=interface, event=event, cadet=cadet
        )
    else:
        return button_to_click_on_cadet(cadet)


def get_cell_for_cadet_that_is_clicked_on(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> ListOfLines:
    list_of_groups_as_str = get_list_of_previous_groups_as_str(
        object_store=interface.object_store,
        event_to_exclude=event,
        cadet=cadet,
    )
    list_of_qualifications_as_str = (
        get_qualification_status_for_single_cadet_as_list_of_str(
            object_store=interface.object_store, cadet=cadet
        )
    )

    return ListOfLines(
        [button_to_click_on_cadet_when_already_selected(cadet), "Previous groups:-"]
        + list_of_groups_as_str
        + ["Qualifications:-"]
        + list_of_qualifications_as_str
    ).add_Lines()


def this_cadet_has_been_clicked_on_already(interface: abstractInterface, cadet: Cadet):
    try:
        selected_cadet = get_cadet_from_state(interface)
    except MissingData:
        return False

    return selected_cadet == cadet


def any_cadet_clicked_on(interface: abstractInterface):
    try:
        get_cadet_from_state(interface)
        return True
    except MissingData:
        return False
