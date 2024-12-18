from typing import Union

from app.backend.groups.group_allocation_info import get_group_allocation_info, GroupAllocationInfo
from app.backend.groups.previous_groups import get_list_of_previous_groups_as_str, DictOfEventAllocations, \
    get_dict_of_event_allocations_for_last_N_events_for_list_of_cadets
from app.backend.qualifications_and_ticks.progress import (
    get_qualification_status_for_single_cadet_as_list_of_str,
)
from app.backend.qualifications_and_ticks.qualifications_for_cadet import highest_qualification_for_cadet
from app.frontend.forms.reorder_form import reorder_table
from app.frontend.shared.cadet_state import get_cadet_from_state
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets

from app.objects.exceptions import missing_data


from app.frontend.events.group_allocation.input_fields import (
    get_notes_field,
    get_days_attending_field,
    get_input_fields_for_cadet,
    button_name_for_add_partner,
    RESET_DAY_BUTTON_LABEL,
    make_cadet_available_button_name,
)
from app.frontend.events.group_allocation.store_state import (
    no_day_set_in_state,
    get_day_from_state_or_none,
)

from app.backend.boat_classes.summary import summarise_class_attendance_for_event
from app.backend.club_boats.summary import summarise_club_boat_allocations_for_event
from app.backend.groups.sorting import sorted_active_cadets
from app.backend.events.summarys import summarise_allocations_for_event

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    save_menu_button,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    DetailListOfLines,
    Line,
    make_long_thing_detail_box,
)
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.cadets import Cadet
from app.objects.events import (
    Event,
)


def display_form_allocate_cadets_at_event(
    interface: abstractInterface, event: Event, sort_order: list
) -> Union[Form, NewForm]:

    allocations_and_class_summary = get_allocations_and_classes_detail(
        event=event, interface=interface
    )
    day_dropdown = get_day_buttons(interface)
    inner_form = get_inner_form_for_cadet_allocation(
        interface=interface, event=event, sort_order=sort_order
    )
    sort_button_table = sort_buttons_for_allocation_table(sort_order)
    nav_bar = ButtonBar([cancel_menu_button, save_menu_button])

    sort_order_line = DetailListOfLines(
        ListOfLines(
            [
                _______________,
                "Specify order that table is sorted in:",
                sort_button_table,
            ]
        ),
        "Sort order",
        open=False,
    )

    return Form(
        ListOfLines(
            [
                nav_bar,
                Heading("Cadets in %s " % str(event), size=4),
                _______________,
                _______________,
                allocations_and_class_summary,
                sort_order_line,
                _______________,
                day_dropdown,
                Line("Click on a cadet name to show all previous events"),
                inner_form,
                _______________,
                nav_bar,
            ]
        )
    )


def get_day_buttons(interface: abstractInterface) -> Line:
    if no_day_set_in_state(interface):
        event = get_event_from_state(interface)
        event_weekdays = event.weekdays_in_event()
        weekday_buttons = [Button(day.name) for day in event_weekdays]
        return Line(
            [
                "  Choose day to edit (if you want to allocate cadets to different groups, boats or partners on specific days): "
            ]
            + weekday_buttons
        )
    else:
        day = get_day_from_state_or_none(interface)
        return Line(
            ["Currently editing %s: " % day.name, reset_day_button]
        )

reset_day_button = Button(RESET_DAY_BUTTON_LABEL)

def list_of_all_day_button_names(interface: abstractInterface):
    event = get_event_from_state(interface)
    event_weekdays = event.weekdays_in_event()
    weekday_buttons = [day.name for day in event_weekdays]
    weekday_buttons.append(RESET_DAY_BUTTON_LABEL)

    return weekday_buttons


def get_allocations_and_classes_detail(
    interface: abstractInterface, event: Event
) -> DetailListOfLines:
    allocations = summarise_allocations_for_event(object_store=interface.object_store, event=event)

    club_dinghies = summarise_club_boat_allocations_for_event(
        event=event, object_store=interface.object_store
    )
    classes = summarise_class_attendance_for_event(event=event, object_store=interface.object_store)
    return DetailListOfLines(
        ListOfLines(
            [
                _______________,
                allocations,
                _______________,
                "Allocated club dinghies:",
                club_dinghies,
                _______________,
                "Classes",
                classes,
                _______________,
            ]
        ),
        "Summary",
        open=False,
    )


def sort_buttons_for_allocation_table(sort_order: list) -> Table:
    return reorder_table(sort_order)

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets

def get_inner_form_for_cadet_allocation(
    interface: abstractInterface, event: Event, sort_order: list
) -> Table:
    dict_of_all_event_data =get_dict_of_all_event_info_for_cadets(object_store=interface.object_store, event=event, active_only=True)

    day_or_none = get_day_from_state_or_none(interface)
    list_of_cadets = sorted_active_cadets(
        object_store = interface.object_store,
        dict_of_all_event_data=dict_of_all_event_data, sort_order=sort_order, day_or_none=day_or_none
    )
    previous_groups_for_cadets = get_dict_of_event_allocations_for_last_N_events_for_list_of_cadets(
        object_store=interface.object_store,
        list_of_cadets=list_of_cadets,
        remove_unallocated=False,
        N_events=NUMBER_OF_PREVIOUS_EVENTS,
        excluding_event=event
    )
    group_allocation_info = get_group_allocation_info(dict_of_all_event_data)

    return Table(
        [get_top_row(previous_groups_for_cadets=previous_groups_for_cadets,
                     group_allocation_info=group_allocation_info, interface=interface)]
        + [
            get_row_for_cadet(
                interface=interface,
                previous_groups_for_cadets=previous_groups_for_cadets,
                group_allocation_info=group_allocation_info,
                dict_of_all_event_data = dict_of_all_event_data,
                cadet=cadet
            )
            for cadet in list_of_cadets
        ],
        has_column_headings=True,
        has_row_headings=True,
    )


NUMBER_OF_PREVIOUS_EVENTS = 3


def get_top_row(
    interface: abstractInterface,
        previous_groups_for_cadets: DictOfEventAllocations,
        group_allocation_info: GroupAllocationInfo
) -> RowInTable:
    previous_event_names_in_list = previous_groups_for_cadets.list_of_events

    info_field_names = group_allocation_info.visible_field_names

    input_field_names_over_days = get_daily_input_field_headings(
         interface=interface
    )

    return RowInTable(
        ["", "Set Availability"]  ## cadet name
        + previous_event_names_in_list
        + info_field_names
        + ["Official qualification", "Notes"]
        + input_field_names_over_days
    )


def get_daily_input_field_headings(
    interface: abstractInterface
) -> list:

    if no_day_set_in_state(interface):
        return get_input_field_headings_for_day(
            "All days"
        )
    else:
        day = get_day_from_state_or_none(interface)
        return get_input_field_headings_for_day(
            day.name
        )


def get_input_field_headings_for_day(
    day_name: str
) -> list:

    input_field_names = [
        "Allocate: group (%s)" % day_name,
        "Allocate: Club boat(%s)" % day_name,
        "Allocate: Class of boat (%s)" % ( day_name),
        "Edit: Sail number (%s)" % ( day_name),
        "Allocate: Two handed partner (%s)" % day_name,
    ]

    return input_field_names


def get_row_for_cadet(interface: abstractInterface,
                      previous_groups_for_cadets: DictOfEventAllocations,
group_allocation_info: GroupAllocationInfo,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
                      cadet: Cadet
) -> RowInTable:
    cell_for_cadet = get_cell_for_cadet(interface=interface, event=dict_of_all_event_data.event, cadet=cadet)
    previous_groups_as_list = previous_groups_for_cadets.previous_groups_for_cadet_as_list(cadet)
    previous_group_info = group_allocation_info.group_info_dict_for_cadet_as_ordered_list(cadet)
    previous_group_info = [
        make_long_thing_detail_box(field) for field in previous_group_info
    ]
    input_fields = get_input_fields_for_cadet(
        interface=interface, cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
    )
    qualification = str(highest_qualification_for_cadet(object_store=interface.object_store, cadet=cadet))
    notes_field = get_notes_field(dict_of_all_event_data=dict_of_all_event_data, cadet=cadet)
    days_attending_field = get_days_attending_field(dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet
    )

    return RowInTable(
        [cell_for_cadet, days_attending_field]
        + previous_groups_as_list
        + previous_group_info
        + [qualification, notes_field]
        + input_fields
    )



MAX_EVENTS_TO_SHOW = 10


def get_cell_for_cadet(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> Union[ListOfLines, Button]:
    if this_cadet_has_been_clicked_on_already(interface=interface, cadet=cadet):
        return get_cell_for_cadet_that_is_clicked_on(interface=interface, event=event, cadet=cadet)
    else:
        return Button(str(cadet), value=get_button_id_for_cadet(cadet.id))


def get_cell_for_cadet_that_is_clicked_on(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> ListOfLines:
    list_of_groups_as_str = get_list_of_previous_groups_as_str(
        object_store=interface.object_store, event_to_exclude=event,  cadet=cadet
    )
    list_of_qualifications_as_str = (
        get_qualification_status_for_single_cadet_as_list_of_str(
            object_store=interface.object_store, cadet=cadet
        )
    )

    return ListOfLines(
        [str(cadet), "Previous groups:-"]
        + list_of_groups_as_str
        + ["Qualifications:-"]
        + list_of_qualifications_as_str
    ).add_Lines()


def this_cadet_has_been_clicked_on_already(interface: abstractInterface, cadet: Cadet):
    cadet_id = get_cadet_from_state(interface)
    if cadet_id is missing_data:
        return False
    return cadet_id == cadet.id


def get_button_id_for_cadet(id: str) -> str:
    return "cadet_%s" % id


def get_list_of_all_cadet_buttons(interface: abstractInterface):
    list_of_cadets = get_list_of_all_cadets_with_event_data(interface)
    return [get_button_id_for_cadet(id) for id in list_of_cadets.list_of_ids]


def cadet_id_from_cadet_button(button_str):
    return button_str.split("_")[1]


def get_list_of_all_add_partner_buttons(interface: abstractInterface):
    list_of_cadets = get_list_of_all_cadets_with_event_data(interface)
    return [
        button_name_for_add_partner(cadet_id=id) for id in list_of_cadets.list_of_ids
    ]


def get_list_of_all_add_cadet_availability_buttons(interface: abstractInterface):
    list_of_cadets = get_list_of_all_cadets_with_event_data(interface)

    return [make_cadet_available_button_name(cadet) for cadet in list_of_cadets]


def get_list_of_all_cadets_with_event_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    dict_of_all_event_data =get_dict_of_all_event_info_for_cadets(object_store=interface.object_store, event=event,
                                                                  active_only=True)
    list_of_cadets = dict_of_all_event_data.list_of_cadets

    return list_of_cadets
