import datetime

from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import     get_health_notes_for_cadet_at_event
from app.backend.cadets_at_event.instructor_marked_attendance import (
    get_attendance_on_day_for_cadets_in_group,
    are_all_cadets_in_group_marked_in_registration_as_present_absent_or_late,
    mark_unknown_cadets_as_not_attending_or_unregistered,
)
from app.frontend.shared.buttons import (
    get_button_value_given_type_and_attributes,
    is_button_of_type,
    get_attributes_from_button_pressed_of_known_type,
    get_button_value_for_cadet_selection,
)
from app.frontend.shared.cadet_state import is_cadet_set_in_state, get_cadet_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.attendance import (
    Attendance,
    not_attending,
    present,
    absent,
    temporary_absence,
    registration_not_taken,
    returned,
    will_be_late,
)
from app.objects.cadets import Cadet
from app.objects.composed.attendance import AttendanceOnDay
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group


def get_table_to_mark_attendance(
    interface: abstractInterface, event: Event, group: Group, day: Day
) -> Table:
    mark_unknown_cadets_as_not_attending_or_unregistered(interface=interface,
                                                         event=event,group=group,day=day)
    current_attendance = get_attendance_on_day_for_cadets_in_group(
        interface.object_store, event=event, group=group, day=day
    )

    not_initial_registration_phase = is_not_initial_registration(
        interface, event, group, day
    )

    body_of_table = [
        get_row_in_table_for_attendance(
            interface=interface,
            event=event,
            cadet=cadet,
            attendance_on_day=attendance_on_day,
            not_initial_registration_phase=not_initial_registration_phase,
        )
        for cadet, attendance_on_day in current_attendance.items()
    ]
    max_width = max([len(row) for row in body_of_table])
    padding = [""] * (max_width - 2)
    top_row = RowInTable(["Cadet - click to see history", "Health"] + padding)

    return Table([top_row] + body_of_table, has_column_headings=True)


def is_not_initial_registration(
    interface: abstractInterface, event: Event, group: Group, day: Day
) -> bool:
    not_initial_registration_phase = (
        are_all_cadets_in_group_marked_in_registration_as_present_absent_or_late(
            object_store=interface.object_store, event=event, group=group, day=day
        )
    )

    return not_initial_registration_phase


def get_row_in_table_for_attendance(
    interface: abstractInterface,
    cadet: Cadet,
        event: Event,
    attendance_on_day: AttendanceOnDay,
    not_initial_registration_phase: bool,
) -> RowInTable:
    attendance_columns = get_attendance_fields_given_current_attendance(
        cadet,
        attendance_on_day.current_attendance,
        not_initial_registration_phase=not_initial_registration_phase,
    )

    cadet_cell = get_cadet_cell(
        interface,
        attendance_on_day,
        cadet,
        not_initial_registration_phase=not_initial_registration_phase,
    )

    health_cell = health_for_cadet(interface=interface, event=event, cadet=cadet)

    return RowInTable(
        [
            cadet_cell,
                health_cell,
        ]
        + attendance_columns
    )


def get_cadet_cell(
    interface: abstractInterface,
    attendance_on_day: AttendanceOnDay,
    cadet: Cadet,
    not_initial_registration_phase: bool,
):
    if not not_initial_registration_phase:
        return name_and_age_of_cadet(cadet)

    history = []
    include_attendance_on_button = True
    if is_cadet_set_in_state(interface):
        current_cadet = get_cadet_from_state(interface)
        if current_cadet == cadet:
            history = attendance_on_day.history_of_attendance.as_list_of_str()
            include_attendance_on_button = False  ## to avoid showing twice

    return ListOfLines(
        [
            select_cadet_button(
                cadet=cadet,
                attendance_on_day=attendance_on_day,
                include_attendance=include_attendance_on_button,
            )
        ]
        + history
    ).add_Lines()


def select_cadet_button(
    cadet: Cadet, attendance_on_day: AttendanceOnDay, include_attendance: bool
):
    button_label = name_and_age_of_cadet(cadet)
    if include_attendance:
        button_label += " %s" % attendance_on_day.current_attendance.name

    return Button(label=button_label, value=get_button_value_for_cadet_selection(cadet))


def name_and_age_of_cadet(cadet: Cadet):
    return "%s (%dyrs)" % (cadet.name, int(cadet.approx_age_years()))

def health_for_cadet(interface: abstractInterface, event: Event, cadet: Cadet):
    return get_health_notes_for_cadet_at_event(object_store=interface.object_store, event=event, cadet=cadet)

def get_attendance_fields_given_current_attendance(
    cadet: Cadet, attendance_on_day: Attendance, not_initial_registration_phase: bool
) -> list:
    func_to_call = func_dict[attendance_on_day]
    return func_to_call(
        cadet, not_initial_registration_phase=not_initial_registration_phase
    )


### BUTTONS DEPENDS ON CURRENT ATTENDANCE
def get_attendance_fields_for_attendance_not_yet_registered(
    cadet: Cadet, not_initial_registration_phase: bool
):
    if not_initial_registration_phase:
        raise Exception("Shouldn't be possible")
    else:
        return [mark_present_checkbox(cadet), mark_late_checkbox(cadet)]


def get_attendance_fields_for_attendance_not_attending(
    cadet: Cadet, not_initial_registration_phase: bool
):
    if not_initial_registration_phase:
        return [
            "",
            "",
            Button(
                value=button_value_to_mark_not_present_as_attending(cadet),
                label="Not registered for today - click if coming now and has arrived",
            ),
        ]
    else:
        return [
            "Not registered for today - tick if coming now and has arrived",
            mark_present_checkbox(cadet),
        ]


def get_attendance_fields_if_marked_present(
    cadet: Cadet, not_initial_registration_phase: bool
):
    if not_initial_registration_phase:
        return [
            mark_returned_checkbox(cadet),
            Button(
                value=button_value_to_mark_temporary_absence(cadet),
                label="Taking temporary absence from group",
            ),
            Button(
                value=button_value_to_mark_accident_registration(cadet),
                label="Accidentally marked as present - actually absent",
            ),
        ]
    else:
        return [
            mark_present_checkbox(cadet, checked=True),
            mark_late_checkbox(cadet),
        ]


def get_attendance_fields_if_marked_absent(
    cadet: Cadet, not_initial_registration_phase: bool
):
    if not_initial_registration_phase:
        return [
            "",
            "",
            Button(
                value=button_value_to_mark_arrived(cadet),
                label="Was marked absent but arrived unexpectedly",
            ),
        ]
    else:
        return [
            mark_present_checkbox(cadet),
            mark_late_checkbox(cadet),
        ]


def get_attendance_fields_if_marked_will_be_late(
    cadet: Cadet, not_initial_registration_phase: bool
):
    if not_initial_registration_phase:
        return [
            "",
            Button(
                value=button_value_to_mark_arrived(cadet),
                label="Late but has now arrived",
            ),
            "",
            "",
        ]
    else:
        return [
            mark_present_checkbox(cadet),
            mark_late_checkbox(cadet, checked=True),
        ]


def get_attendance_fields_if_marked_temporary_absence(
    cadet: Cadet, not_initial_registration_phase: bool
):
    if not_initial_registration_phase:
        return [
            Button(
                value=button_value_to_mark_arrived(cadet),
                label="Back after temporary absence",
            ),
            "",
            "",
            "",
        ]
    else:
        raise Exception("Should not be possible")


def get_attendance_fields_if_marked_return(
    cadet: Cadet, not_initial_registration_phase: bool
):
    ## to remove warnings, doesn't matter
    print(cadet)
    print(not_initial_registration_phase)
    return ["", "", ""]


func_dict = {
    not_attending: get_attendance_fields_for_attendance_not_attending,
    present: get_attendance_fields_if_marked_present,
    absent: get_attendance_fields_if_marked_absent,
    temporary_absence: get_attendance_fields_if_marked_temporary_absence,
    registration_not_taken: get_attendance_fields_for_attendance_not_yet_registered,
    returned: get_attendance_fields_if_marked_return,
    will_be_late: get_attendance_fields_if_marked_will_be_late,
}


def mark_late_checkbox(cadet: Cadet, checked: bool = False):
    return checkboxInput(
        input_name=check_value_to_mark_late(cadet),
        input_label="Mark late",
        dict_of_labels={LATE: ""},
        dict_of_checked={LATE: checked},
    )


def mark_present_checkbox(cadet: Cadet, checked: bool = False):
    return checkboxInput(
        input_name=check_value_to_mark_present(cadet),
        input_label="Mark present",
        dict_of_labels={PRESENT: ""},
        dict_of_checked={PRESENT: checked},
    )


def mark_returned_checkbox(cadet: Cadet):
    return checkboxInput(
        input_name=check_value_to_mark_returned(cadet),
        input_label=message_for_returning(cadet),
        dict_of_labels={RETURNED: ""},
        dict_of_checked={RETURNED: False},
    )


def cadet_has_tick_for_present(interface: abstractInterface, cadet: Cadet):
    is_ticked_as_list = interface.value_of_multiple_options_from_form(
        check_value_to_mark_present(cadet), default=[]
    )
    return PRESENT in is_ticked_as_list


def cadet_has_tick_for_late(interface: abstractInterface, cadet: Cadet):
    is_ticked_as_list = interface.value_of_multiple_options_from_form(
        check_value_to_mark_late(cadet), default=[]
    )
    return LATE in is_ticked_as_list


def cadet_has_tick_for_returned(interface: abstractInterface, cadet: Cadet):
    is_ticked_as_list = interface.value_of_multiple_options_from_form(
        check_value_to_mark_returned(cadet), default=[]
    )
    return RETURNED in is_ticked_as_list


def message_for_returning(cadet: Cadet):
    if cadet.approx_age_years() < 11:
        return "Returned to parents (primary age)"
    else:
        return "Returned to club precinct (secondary age)"


def day_given_current_day_and_event(
    interface: abstractInterface, event: Event, warn: bool = False
) -> Day:
    days_in_event = event.days_in_event()
    current_date = datetime.date.today()
    if current_date < event.start_date:
        if warn:
            interface.log_error(
                "Event does not start until %s - doing registration for first day"
                % event.start_date
            )
        return days_in_event[0]
    elif current_date > event.end_date:
        if warn:
            interface.log_error(
                "Event finished on %s - doing registration for final day"
                % event.end_date
            )
        return days_in_event[-1]
    else:
        return day_given_event_is_currently_on(event)


def day_given_event_is_currently_on(event: Event) -> Day:
    days_in_event = event.days_in_event()
    dates_in_event = event.dates_in_event()
    current_date = datetime.date.today()
    idx_in_event = dates_in_event.index(current_date)

    return days_in_event[idx_in_event]


PRESENT = "Present"
LATE = "Late"
RETURNED = "Returned"


def check_value_to_mark_present(cadet: Cadet):
    return "Present_%s" % cadet.id


def check_value_to_mark_late(cadet: Cadet):
    return "Late_%s" % cadet.id


def check_value_to_mark_returned(cadet: Cadet):
    return "Returned_%s" % cadet.id


button_type_going_to_be_late = "goingToBeLate"


def button_value_to_mark_going_to_be_late(cadet: Cadet):
    return get_button_value_given_type_and_attributes(
        button_type_going_to_be_late, cadet.id
    )


def is_late_button(button_pressed: str):
    return is_button_of_type(button_pressed, type_to_check=button_type_going_to_be_late)


button_type_not_present_now_attending = "notPresentMarkAttending"


def button_value_to_mark_not_present_as_attending(cadet: Cadet):
    return get_button_value_given_type_and_attributes(
        button_type_not_present_now_attending, cadet.id
    )


def is_not_present_now_attending_button(button_pressed: str):
    return is_button_of_type(
        button_pressed, type_to_check=button_type_not_present_now_attending
    )


button_type_if_returning = "Returning"


def button_value_to_mark_returned(cadet: Cadet):
    return get_button_value_given_type_and_attributes(
        button_type_if_returning, cadet.id
    )


def is_returning_to_parent_button(button_pressed: str):
    return is_button_of_type(button_pressed, type_to_check=button_type_if_returning)


button_type_if_temporary_absence = "TempAbsence"


def button_value_to_mark_temporary_absence(cadet: Cadet):
    return get_button_value_given_type_and_attributes(
        button_type_if_temporary_absence, cadet.id
    )


def is_temporary_absence_button(button_pressed: str):
    return is_button_of_type(
        button_pressed, type_to_check=button_type_if_temporary_absence
    )


button_type_if_has_arrived = "Arrived"


def button_value_to_mark_arrived(cadet: Cadet):
    return get_button_value_given_type_and_attributes(
        button_type_if_has_arrived, cadet.id
    )


def is_has_arrived_button(button_pressed: str):
    return is_button_of_type(button_pressed, type_to_check=button_type_if_has_arrived)


button_type_if_accidentially_registered = "AccidentallyRegistered"


def button_value_to_mark_accident_registration(cadet: Cadet):
    return get_button_value_given_type_and_attributes(
        button_type_if_accidentially_registered, cadet.id
    )


def is_reverse_accidental_registration_button(button_pressed: str):
    return is_button_of_type(
        button_pressed, type_to_check=button_type_if_accidentially_registered
    )


####
def get_cadet_given_button_pressed(
    interface: abstractInterface, button_value: str, button_type: str
) -> Cadet:
    cadet_id = get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_value, type_to_check=button_type
    )

    return get_cadet_from_id(object_store=interface.object_store, cadet_id=cadet_id)
