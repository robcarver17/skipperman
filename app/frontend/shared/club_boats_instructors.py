from typing import Tuple, List

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id
from app.backend.volunteers.volunteers_at_event import (
    get_list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies,
    allocate_club_dinghy_to_volunteer_on_day,
    remove_club_dinghy_from_volunteer_on_day,
    get_list_of_volunteers_on_day_currently_allocated_to_club_dinghy,
    copy_club_dinghy_for_instructor_across_all_days,
)
from app.backend.club_boats.list_of_club_dinghies import (
    get_club_dinghy_from_id,
    get_list_of_visible_club_dinghies,
)
from app.data_access.configuration.fixed import COPY_OVERWRITE_SYMBOL
from app.data_access.store.object_store import ObjectStore
from app.frontend.shared.buttons import (
    get_button_value_given_type_and_attributes,
    is_button_of_type,
    get_attributes_from_button_pressed_of_known_type,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    DetailListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.club_dinghies import ClubDinghy
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.abstract_objects.abstract_form import dropDownInput
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.utilities.exceptions import MISSING_FROM_FORM
from app.objects.volunteers import Volunteer


def get_club_dinghies_detail_instructors(interface: abstractInterface, event: Event):
    return DetailListOfLines(
        ListOfLines(
            [
                info_line,
                _______________,
                get_club_dinghies_instructors_form(interface=interface, event=event),
            ]
        ),
        name="Club boats - allocate to instructors",
    )


info_line = Line(
    [
        "Allocate club dinghies to instructors (will appear in table above). Use ",
        COPY_OVERWRITE_SYMBOL,
        " to copy and overwrite boats allocated.",
    ]
)


def get_club_dinghies_instructors_form(
    interface: abstractInterface, event: Event
) -> Table:
    object_store = interface.object_store
    visible_dinghies = get_list_of_visible_club_dinghies(object_store)
    top_row = get_top_row_in_club_dinghy_instructors_form(event)

    rows_in_table = [
        get_row_in_club_dinghy_instructors_form(
            object_store=object_store,
            event=event,
            club_dinghy=club_dinghy,
        )
        for club_dinghy in visible_dinghies
    ]

    table = Table(
        [top_row] + rows_in_table,
        has_column_headings=True,
        has_row_headings=True,
    )

    return table


def get_top_row_in_club_dinghy_instructors_form(event: Event) -> RowInTable:
    list_of_days = [day.name for day in event.days_in_event()]

    return RowInTable(
        ["Club boat"] + list_of_days,
        is_heading_row=True,
    )


def get_row_in_club_dinghy_instructors_form(
    object_store: ObjectStore,
    event: Event,
    club_dinghy: ClubDinghy,
) -> RowInTable:
    day_cells = [
        get_day_row_in_club_dinghy_instructors_form(
            object_store=object_store,
            event=event,
            club_dinghy=club_dinghy,
            day=day,
        )
        for day in event.days_in_event()
    ]
    return RowInTable([club_dinghy.name] + day_cells)


def get_day_row_in_club_dinghy_instructors_form(
    object_store: ObjectStore,
    event: Event,
    day: Day,
    club_dinghy: ClubDinghy,
) -> ListOfLines:
    existing = get_existing_lines_in_club_dinghy_instructors_form(
        object_store, event=event, day=day, club_dinghy=club_dinghy
    )

    add_new = get_add_new_item_in_club_dinghy_instructors_form(
        object_store, event=event, day=day, club_dinghy=club_dinghy
    )
    return ListOfLines(existing + [add_new])


def get_existing_lines_in_club_dinghy_instructors_form(
    object_store: ObjectStore,
    event: Event,
    club_dinghy: ClubDinghy,
    day: Day,
) -> List[Line]:
    list_of_volunteers = (
        get_list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
            object_store=object_store, event=event, club_dinghy=club_dinghy, day=day
        )
    )

    lines = [
        line_and_delete_button_for_existing_volunteer_with_club_dinghy(
            volunteer=volunteer, day=day, club_dinghy=club_dinghy
        )
        for volunteer in list_of_volunteers
    ]

    return lines


def line_and_delete_button_for_existing_volunteer_with_club_dinghy(
    volunteer: Volunteer, day: Day, club_dinghy: ClubDinghy
) -> Line:
    delete_button = Button(
        "Remove allocation",
        value=button_name_for_deleting_row_of_club_dinghy_instructor(
            day=day, volunteer=volunteer
        ),
    )
    copy_button = Button(
        COPY_OVERWRITE_SYMBOL,
        value=button_name_for_copying_row_club_dinghy_instructor(
            day=day, volunteer=volunteer, club_dinghy=club_dinghy
        ),
    )

    return Line([volunteer.name, " ", copy_button, " ", delete_button])


def get_add_new_item_in_club_dinghy_instructors_form(
    object_store: ObjectStore,
    event: Event,
    club_dinghy: ClubDinghy,
    day: Day,
) -> Line:
    dict_of_volunteers = get_dict_of_volunteer_names_for_dropdown(
        object_store=object_store, event=event, day=day
    )

    name_drop = dropDownInput(
        input_name=name_of_dropdown_for_club_dinghy_instructors_row(
            day=day, club_dinghy=club_dinghy
        ),
        dict_of_options=dict_of_volunteers,
        input_label="",
        default_label=dict_of_volunteers[no_volunteer_to_allocate.name],
    )

    add_button = Button(
        value=button_name_for_adding_new_row_to_club_dinghy_instructor(
            day, club_dinghy
        ),
        label="Allocate dinghy",
    )
    return Line([name_drop, add_button])


def get_dict_of_volunteer_names_for_dropdown(
    object_store: ObjectStore,
    event: Event,
    day: Day,
):
    list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies = (
        get_list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies(
            object_store=object_store, event=event, day=day
        )
    )
    list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies.insert(
        0, no_volunteer_to_allocate
    )
    dict_of_volunteers = dict(
        [
            (volunteer.name, volunteer.id)
            for volunteer in list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies
        ]
    )

    return dict_of_volunteers


no_volunteer_to_allocate = Volunteer("", "", id="-99999")


def name_of_dropdown_for_club_dinghy_instructors_row(day: Day, club_dinghy: ClubDinghy):
    return "add_clubdinghyinstructor_instructor_name_56_%s_%s" % (
        day.name,
        club_dinghy.id,
    )


def get_volunteer_from_dropdown_on_day(
    interface: abstractInterface, day: Day, club_dinghy: ClubDinghy
):
    key = name_of_dropdown_for_club_dinghy_instructors_row(
        day=day, club_dinghy=club_dinghy
    )
    volunteer_id = interface.value_from_form(key, default=MISSING_FROM_FORM)
    if volunteer_id is MISSING_FROM_FORM or volunteer_id == no_volunteer_to_allocate.id:
        return no_volunteer_to_allocate

    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id
    )

    return volunteer


def button_name_for_adding_new_row_to_club_dinghy_instructor(
    day: Day, club_dinghy: ClubDinghy
):
    return get_button_value_given_type_and_attributes(
        ADD_CLUB_DINGHY_BUTTON_TYPE, day.name, club_dinghy.id
    )


def get_day_and_club_dinghy_from_add_club_boat_button_pressed(
    interface: abstractInterface,
) -> Tuple[Day, ClubDinghy]:
    day_name, club_dinghy_id = get_attributes_from_button_pressed_of_known_type(
        interface.last_button_pressed(), type_to_check=ADD_CLUB_DINGHY_BUTTON_TYPE
    )
    day = Day[day_name]
    club_dinghy = get_club_dinghy_from_id(
        object_store=interface.object_store, club_dinghy_id=club_dinghy_id
    )

    return day, club_dinghy


def button_name_for_copying_row_club_dinghy_instructor(
    day: Day, club_dinghy: ClubDinghy, volunteer: Volunteer
):
    return get_button_value_given_type_and_attributes(
        COPY_CLUB_DINGHY_BUTTON_TYPE, day.name, club_dinghy.id, volunteer.id
    )


def get_day_and_volunteer_and_club_dinghy_from_copy_overwrite_club_boat_button_pressed(
    interface: abstractInterface,
) -> Tuple[Day, ClubDinghy, Volunteer]:
    (
        day_name,
        club_dinghy_id,
        volunteer_id,
    ) = get_attributes_from_button_pressed_of_known_type(
        interface.last_button_pressed(), type_to_check=COPY_CLUB_DINGHY_BUTTON_TYPE
    )
    day = Day[day_name]
    club_dinghy = get_club_dinghy_from_id(
        object_store=interface.object_store, club_dinghy_id=club_dinghy_id
    )
    volunteer = get_volunteer_from_id(
        volunteer_id=volunteer_id, object_store=interface.object_store
    )

    return day, club_dinghy, volunteer


def button_name_for_deleting_row_of_club_dinghy_instructor(
    day: Day, volunteer: Volunteer
):
    return get_button_value_given_type_and_attributes(
        DELETE_CLUB_DINGHY_BUTTON_TYPE, day.name, volunteer.id
    )


def get_day_and_volunteer_from_delete_club_boat_button_pressed(
    interface: abstractInterface,
) -> Tuple[Day, Volunteer]:
    day_name, volunteer_id = get_attributes_from_button_pressed_of_known_type(
        interface.last_button_pressed(), type_to_check=DELETE_CLUB_DINGHY_BUTTON_TYPE
    )
    day = Day[day_name]
    volunteer = get_volunteer_from_id(
        volunteer_id=volunteer_id, object_store=interface.object_store
    )

    return day, volunteer


ADD_CLUB_DINGHY_BUTTON_TYPE = "add_club_dinghy"
DELETE_CLUB_DINGHY_BUTTON_TYPE = "delete_club_dinghy"
COPY_CLUB_DINGHY_BUTTON_TYPE = "copy_overwrite_club_dinghy"


def is_club_dinghy_instructor_button(button_name):
    return (
        is_add_club_dinghy_for_instructor(button_name)
        or is_delete_club_dinghy_for_instructor(button_name)
        or is_copy_club_dinghy_for_instructor(button_name)
    )


def is_add_club_dinghy_for_instructor(button_name):
    return is_button_of_type(button_name, type_to_check=ADD_CLUB_DINGHY_BUTTON_TYPE)


def is_delete_club_dinghy_for_instructor(button_name):
    return is_button_of_type(button_name, type_to_check=DELETE_CLUB_DINGHY_BUTTON_TYPE)


def is_copy_club_dinghy_for_instructor(button_name):
    return is_button_of_type(button_name, type_to_check=COPY_CLUB_DINGHY_BUTTON_TYPE)


def handle_club_dinghy_instructor_allocation_button_pressed(
    interface: abstractInterface,
):
    button_pressed = interface.last_button_pressed()
    if is_add_club_dinghy_for_instructor(button_pressed):
        add_club_dinghy_for_instructor(interface)
    elif is_delete_club_dinghy_for_instructor(button_pressed):
        delete_club_dinghy_for_instructor(interface)
    elif is_copy_club_dinghy_for_instructor(button_pressed):
        copy_club_dinghy_for_instructor(interface)
    else:
        raise Exception("Not add or delete")


def add_club_dinghy_for_instructor(interface: abstractInterface):
    day, club_dinghy = get_day_and_club_dinghy_from_add_club_boat_button_pressed(
        interface
    )
    volunteer = get_volunteer_from_dropdown_on_day(
        interface=interface, day=day, club_dinghy=club_dinghy
    )
    if volunteer is no_volunteer_to_allocate:
        return

    event = get_event_from_state(interface)
    allocate_club_dinghy_to_volunteer_on_day(
        object_store=interface.object_store,
        day=day,
        event=event,
        club_dinghy=club_dinghy,
        volunteer=volunteer,
    )


def delete_club_dinghy_for_instructor(interface: abstractInterface):
    day, volunteer = get_day_and_volunteer_from_delete_club_boat_button_pressed(
        interface
    )
    event = get_event_from_state(interface)
    remove_club_dinghy_from_volunteer_on_day(
        object_store=interface.object_store, event=event, day=day, volunteer=volunteer
    )


def copy_club_dinghy_for_instructor(interface: abstractInterface):
    (
        day,
        club_dinghy,
        volunteer,
    ) = get_day_and_volunteer_and_club_dinghy_from_copy_overwrite_club_boat_button_pressed(
        interface
    )
    event = get_event_from_state(interface)
    copy_club_dinghy_for_instructor_across_all_days(
        object_store=interface.object_store,
        event=event,
        day=day,
        volunteer=volunteer,
        club_dinghy=club_dinghy,
    )
