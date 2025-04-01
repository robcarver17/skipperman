import datetime

from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.backend.cadets_at_event.instructor_marked_attendance import get_current_attendance_on_day_for_cadets_in_group
from app.frontend.shared.buttons import get_button_value_given_type_and_attributes, is_button_of_type, \
    get_attributes_from_button_pressed_of_known_type, get_button_value_for_cadet_selection, is_button_cadet_selection, cadet_from_button_pressed
from app.frontend.shared.cadet_state import is_cadet_set_in_state, get_cadet_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.attendance import Attendance, not_attending, present, absent, temporary_absence, \
    registration_not_taken, returned, will_be_late
from app.objects.cadets import Cadet
from app.objects.composed.attendance import AttendanceOnDay
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group


def get_table_to_mark_attendance(interface: abstractInterface, event: Event, group: Group, day: Day) -> Table:
    current_attendance = get_current_attendance_on_day_for_cadets_in_group(interface.object_store,
                                                                           event=event,group=group, day=day)


    body_of_table =         [
            get_row_in_table_for_attendance(interface=interface, cadet=cadet, attendance_on_day=attendance_on_day)
            for cadet, attendance_on_day in current_attendance.items()
        ]
    max_width = max([len(row) for row in body_of_table])
    padding = [""]*(max_width-2)
    top_row = RowInTable(['Cadet - click to see history', 'Current status', 'Actions']+padding)

    return Table(
        [top_row]+body_of_table,
        has_column_headings=True
    )


def get_row_in_table_for_attendance(interface: abstractInterface,
        cadet: Cadet, attendance_on_day: AttendanceOnDay) -> RowInTable:
    attendance_columns = get_attendance_fields_given_current_attendance(cadet, attendance_on_day.current_attendance)
    cadet_cell = get_cadet_cell(interface, attendance_on_day, cadet)
    return RowInTable([cadet_cell,
                       attendance_on_day.current_attendance.name
                       ]+attendance_columns)

def get_cadet_cell(interface: abstractInterface, attendance_on_day: AttendanceOnDay, cadet: Cadet):
    history = []
    if is_cadet_set_in_state(interface):
        current_cadet = get_cadet_from_state(interface)
        if current_cadet == cadet:
            history = attendance_on_day.history_of_attendance.as_list_of_str()

    return ListOfLines([select_cadet_button(cadet)]+history).add_Lines()

def select_cadet_button(cadet: Cadet):
    return Button(label=name_and_age_of_cadet(cadet),
                  value=get_button_value_for_cadet_selection(cadet))

def name_and_age_of_cadet(cadet: Cadet):
    return "%s (%dyrs)" % (cadet.name, int(cadet.approx_age_years()))


def get_attendance_fields_given_current_attendance(cadet: Cadet, attendance_on_day: Attendance) -> list:
    func_to_call = func_dict[attendance_on_day]
    return func_to_call(cadet)


def get_attendance_fields_for_attendance_not_yet_registered(cadet: Cadet):
    return [checkboxInput(
        input_name=check_value_to_mark_present(cadet),
        input_label = "Mark present",
        dict_of_labels={PRESENT: ''},
        dict_of_checked={PRESENT: False}
    ),
        Button(label = "Present", value = button_value_to_mark_arrived(cadet)),
        Button(label = "Absent", value = button_value_to_mark_accident_registration(cadet)),
        Button(label="Going to be late",
               value=button_value_to_mark_going_to_be_late(cadet))
        ]

def cadet_has_tick_for_present(interface: abstractInterface, cadet: Cadet):
    is_ticked_as_list = interface.value_of_multiple_options_from_form(check_value_to_mark_present(cadet), default=[])
    return PRESENT in is_ticked_as_list


def get_attendance_fields_for_attendance_not_attending(cadet: Cadet):
    return [Button(
        value=button_value_to_mark_not_present_as_attending(
            cadet
        ),
        label="Not registered for today - click if coming now and has arrived"
    )]


def get_attendance_fields_if_marked_present(cadet: Cadet):
    return [Button(
        value=button_value_to_mark_accident_registration(
            cadet
        ),
        label="Accidentally marked as present - actually absent"
    ),
        Button(
        value=button_value_to_mark_temporary_absence(
            cadet
        ),
        label="Taking temporary absence from group"
    ),
    Button(
        value=button_value_to_mark_returned(cadet),
        label = message_for_returning(cadet)
    )]


def get_attendance_fields_if_marked_absent(cadet: Cadet):
    return [Button(
        value=button_value_to_mark_arrived(
            cadet
        ),
        label="Was marked absent but arrived unexpectedly"
    )]


def get_attendance_fields_if_marked_will_be_late(cadet: Cadet):
    return [Button(
        value=button_value_to_mark_arrived(
            cadet
        ),
        label="Late and has now arrived"
    )
    ]


def get_attendance_fields_if_marked_temporary_absence(cadet: Cadet):
    return [Button(
        value=button_value_to_mark_arrived(
            cadet
        ),
        label="Returned to group from temporary absence"
    ),
        "",
    Button(
        value=button_value_to_mark_returned(cadet),
        label = message_for_returning(cadet)
    )]


def message_for_returning(cadet: Cadet):
    if cadet.approx_age_years()<11:
        return "Returned to parents (primary age)"
    else:
        return "Left group and in club precinct (secondary age)"


def get_attendance_fields_if_marked_return(cadet: Cadet):
    return []


func_dict = {
    not_attending:get_attendance_fields_for_attendance_not_attending,
    present:get_attendance_fields_if_marked_present,
    absent:get_attendance_fields_if_marked_absent,
    temporary_absence:get_attendance_fields_if_marked_temporary_absence,
    registration_not_taken: get_attendance_fields_for_attendance_not_yet_registered,
    returned:get_attendance_fields_if_marked_return,
    will_be_late:get_attendance_fields_if_marked_will_be_late}


def day_given_current_day_and_event(interface: abstractInterface, event: Event, warn: bool = False) -> Day:
    days_in_event = event.days_in_event()
    current_date = datetime.date.today()
    if current_date<event.start_date:
        if warn:
            interface.log_error("Event does not start until %s - doing registration for first day" % event.start_date)
        return days_in_event[0]
    elif current_date>event.end_date:
        if warn:
            interface.log_error("Event finished on %s - doing registration for final day" % event.end_date)
        return days_in_event[-1]
    else:
        return day_given_event_is_currently_on(event)


def day_given_event_is_currently_on( event: Event) -> Day:
    days_in_event = event.days_in_event()
    dates_in_event = event.dates_in_event()
    current_date = datetime.date.today()
    idx_in_event = dates_in_event.index(current_date)

    return days_in_event[idx_in_event]


PRESENT="Present"


def check_value_to_mark_present(cadet: Cadet):
    return "Present_%s" % cadet.id


button_type_going_to_be_late = "goingToBeLate"


def button_value_to_mark_going_to_be_late(cadet: Cadet):
    return get_button_value_given_type_and_attributes(button_type_going_to_be_late, cadet.id)

def is_late_button(button_pressed:str):
    return is_button_of_type(button_pressed, type_to_check=button_type_going_to_be_late)

button_type_not_present_now_attending = "notPresentMarkAttending"


def button_value_to_mark_not_present_as_attending(cadet: Cadet):
    return get_button_value_given_type_and_attributes(button_type_not_present_now_attending, cadet.id)

def is_not_present_now_attending_button(button_pressed:str):
    return is_button_of_type(button_pressed, type_to_check=button_type_not_present_now_attending)


button_type_if_returning = "Returning"


def button_value_to_mark_returned(cadet: Cadet):
    return get_button_value_given_type_and_attributes(button_type_if_returning, cadet.id)

def is_returning_to_parent_button(button_pressed:str):
    return is_button_of_type(button_pressed, type_to_check=button_type_if_returning)


button_type_if_temporary_absence="TempAbsence"


def button_value_to_mark_temporary_absence(cadet: Cadet):
    return get_button_value_given_type_and_attributes(button_type_if_temporary_absence, cadet.id)

def is_temporary_absence_button(button_pressed:str):
    return is_button_of_type(button_pressed, type_to_check=button_type_if_temporary_absence)



button_type_if_has_arrived = "Arrived"


def button_value_to_mark_arrived(cadet: Cadet):
    return get_button_value_given_type_and_attributes(button_type_if_has_arrived, cadet.id)

def is_has_arrived_button(button_pressed:str):
    return is_button_of_type(button_pressed, type_to_check=button_type_if_has_arrived)


button_type_if_accidentially_registered = "AccidentallyRegistered"


def button_value_to_mark_accident_registration(cadet: Cadet):
    return get_button_value_given_type_and_attributes(button_type_if_accidentially_registered, cadet.id)

def is_reverse_accidental_registration_button(button_pressed:str):
    return is_button_of_type(button_pressed, type_to_check=button_type_if_accidentially_registered)


####
def get_cadet_given_button_pressed(interface: abstractInterface, button_value: str, button_type:str) -> Cadet:
    cadet_id = get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button_value,
                                                     type_to_check=button_type)

    return get_cadet_from_id(object_store=interface.object_store, cadet_id=cadet_id)