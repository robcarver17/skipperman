from app.frontend.shared.cadet_state import (
    update_state_for_specific_cadet,
    clear_cadet_state,
)
from app.backend.cadets_at_event.instructor_marked_attendance import (
    get_attendance_across_events_for_cadets_in_group_at_event,
    update_attendance_across_events_for_list_of_cadets,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.instructors.attendance_table import *

from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.qualification_and_tick_state_storage import (
    get_group_from_state,
)
from app.frontend.shared.buttons import (
    is_button_cadet_selection,
    cadet_from_button_pressed,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    main_menu_button,
    HelpButton,
    ButtonBar,
    SAVE_KEYBOARD_SHORTCUT,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_text import Heading, bold
from app.objects.composed.attendance import DictOfAttendanceAcrossEvents


def display_instructor_attendance(interface: abstractInterface):
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    day = day_given_current_day_and_event(interface=interface, event=event, warn=True)

    heading = Heading("%s at %s on %s" % (group.name, str(event), day.name), size=2)
    instructions = bold(
        "Use tick boxes and save if cadets are present, otherwise use buttons"
    )

    try:
        table = get_table_to_mark_attendance(
            interface, event=event, group=group, day=day
        )
    except Exception as e:
        table = "error %s" % str(e)
    save_buttons = get_save_buttons(interface, event=event, group=group, day=day)
    return Form(
        ListOfLines(
            [
                nav_bar,
                _______________,
                _______________,
                heading,
                _______________,
                instructions,
                _______________,
                table,
                _______________,
                save_buttons,
            ]
        )
    )


nav_bar = ButtonBar(
    [main_menu_button, cancel_menu_button, HelpButton("mark_attendance_help")]
)


def get_save_buttons(
    interface: abstractInterface, event: Event, group: Group, day: Day
):
    not_initial_registration = is_not_initial_registration(interface, event, group, day)
    if not_initial_registration:
        list_of_buttons = [save_returned_ticks_button]
    else:
        list_of_buttons = [
            initial_mark_all_as_attending_or_absence_button,
            mark_all_as_attending_button,
        ]

    return Line(list_of_buttons)


save_returned_ticks_button = Button("Save changes", shortcut=SAVE_KEYBOARD_SHORTCUT)

initial_mark_all_as_attending_or_absence_button = Button(
    "Save changes - anyone not ticked will be marked as absent",
    shortcut=SAVE_KEYBOARD_SHORTCUT,
)
mark_all_as_attending_button = Button(
    "Mark all registered for today as attending (unless late)"
)


def post_instructor_attendance(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    event = get_event_from_state(interface)
    day = day_given_current_day_and_event(interface=interface, event=event)
    group = get_group_from_state(interface)
    initial_registration = not is_not_initial_registration(interface, event, group, day)

    if cancel_menu_button.pressed(last_button):
        return return_to_parent(interface)

    if initial_registration:
        return post_instructor_attendance_if_button_pressed_and_is_initial_registration(
            interface, last_button
        )
    else:
        return (
            post_instructor_attendance_if_button_pressed_and_not_initial_registration(
                interface, last_button
            )
        )


def post_instructor_attendance_if_button_pressed_and_is_initial_registration(
    interface: abstractInterface, last_button: str
):
    interface.lock_cache()
    if initial_mark_all_as_attending_or_absence_button.pressed(last_button):
        final_save_of_initial_registration(interface)

    elif mark_all_as_attending_button.pressed(last_button):
        save_any_changes_to_ticks(
            interface=interface, force_mark_to_present=True, initial_stage=True
        )
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_changes_in_cached_data_to_disk()

    return interface.get_new_form_given_function(display_instructor_attendance)


def post_instructor_attendance_if_button_pressed_and_not_initial_registration(
    interface: abstractInterface, last_button: str
):
    interface.lock_cache()
    if is_button_cadet_selection(last_button):
        cadet_button_pressed(interface, last_button)

    elif is_reverse_accidental_registration_button(last_button):
        update_attendance_for_cadet_given_button(
            interface=interface,
            value_of_button=last_button,
            type_of_button=button_type_if_accidentially_registered,
            new_attendance=absent,
        )

    elif is_late_button(last_button):
        update_attendance_for_cadet_given_button(
            interface=interface,
            value_of_button=last_button,
            type_of_button=button_type_going_to_be_late,
            new_attendance=will_be_late,
        )

    elif is_not_present_now_attending_button(last_button):
        update_attendance_for_cadet_given_button(
            interface=interface,
            value_of_button=last_button,
            type_of_button=button_type_not_present_now_attending,
            new_attendance=present,
        )

    elif is_temporary_absence_button(last_button):
        update_attendance_for_cadet_given_button(
            interface=interface,
            value_of_button=last_button,
            type_of_button=button_type_if_temporary_absence,
            new_attendance=temporary_absence,
        )

    elif is_has_arrived_button(last_button):
        update_attendance_for_cadet_given_button(
            interface=interface,
            value_of_button=last_button,
            type_of_button=button_type_if_has_arrived,
            new_attendance=present,
        )

    elif is_returning_to_parent_button(last_button):
        update_attendance_for_cadet_given_button(
            interface=interface,
            value_of_button=last_button,
            type_of_button=button_type_if_returning,
            new_attendance=returned,
        )
    elif save_returned_ticks_button.pressed(last_button):
        pass  ## will be saved

    else:
        return button_error_and_back_to_initial_state_form(interface)

    ## Now save any changes to ticks
    save_any_changes_to_ticks(interface, initial_stage=False)

    interface.save_changes_in_cached_data_to_disk()

    return interface.get_new_form_given_function(display_instructor_attendance)


def cadet_button_pressed(interface: abstractInterface, last_button: str):
    cadet = cadet_from_button_pressed(
        object_store=interface.object_store, value_of_button_pressed=last_button
    )
    if is_cadet_set_in_state(interface):
        current_cadet = get_cadet_from_state(interface)
        if current_cadet == cadet:
            clear_cadet_state(interface)
            return

    update_state_for_specific_cadet(cadet=cadet, interface=interface)


def save_any_changes_to_ticks(
    interface: abstractInterface,
    initial_stage: bool,
    force_mark_to_present: bool = False,
):
    event = get_event_from_state(interface)
    day = day_given_current_day_and_event(interface=interface, event=event)
    attendance_across_events = get_attendance_across_events_from_state(interface)

    save_any_changes_to_ticks_passing_information(
        interface=interface,
        attendance_across_events=attendance_across_events,
        event=event,
        day=day,
        initial_stage=initial_stage,
        force_mark_to_present=force_mark_to_present,
    )

    update_attendance_across_events_for_list_of_cadets(
        object_store=interface.object_store,
        dict_of_attendance_across_events_for_list_of_cadets=attendance_across_events,
        list_of_cadets=attendance_across_events.list_of_cadets,
    )


def save_any_changes_to_ticks_passing_information(
    interface: abstractInterface,
    attendance_across_events: DictOfAttendanceAcrossEvents,
    event: Event,
    day: Day,
    initial_stage: bool,
    force_mark_to_present: bool,
):
    for cadet in attendance_across_events.list_of_cadets:
        save_ticks_for_cadet(
            interface=interface,
            event=event,
            day=day,
            cadet=cadet,
            attendance_across_events=attendance_across_events,
            initial_stage=initial_stage,
            force_mark_to_present=force_mark_to_present,
        )


def save_ticks_for_cadet(
    interface: abstractInterface,
    attendance_across_events: DictOfAttendanceAcrossEvents,
    event: Event,
    day: Day,
    cadet: Cadet,
    initial_stage: bool,
    force_mark_to_present: bool,
):
    if initial_stage:
        save_ticks_for_cadet_in_initial_stage(
            interface=interface,
            attendance_across_events=attendance_across_events,
            event=event,
            day=day,
            cadet=cadet,
            force_mark_to_present=force_mark_to_present,
        )
    else:
        save_ticks_for_cadet_after_initial_stage(
            interface=interface,
            attendance_across_events=attendance_across_events,
            event=event,
            day=day,
            cadet=cadet,
        )


def save_ticks_for_cadet_in_initial_stage(
    interface: abstractInterface,
    attendance_across_events: DictOfAttendanceAcrossEvents,
    event: Event,
    day: Day,
    cadet: Cadet,
    force_mark_to_present: bool = False,
):
    if should_we_tick_cadet_as_present(
        interface=interface,
        attendance_across_events=attendance_across_events,
        event=event,
        day=day,
        cadet=cadet,
        force_mark_to_present=force_mark_to_present,
    ):
        attendance_across_events.update_attendance_for_cadet_on_day_at_event(
            event=event, cadet=cadet, day=day, new_attendance=present
        )

    if cadet_has_tick_for_late(interface=interface, cadet=cadet):
        attendance_across_events.update_attendance_for_cadet_on_day_at_event(
            event=event, cadet=cadet, day=day, new_attendance=will_be_late
        )


def save_ticks_for_cadet_after_initial_stage(
    interface: abstractInterface,
    attendance_across_events: DictOfAttendanceAcrossEvents,
    event: Event,
    day: Day,
    cadet: Cadet,
):
    if cadet_has_tick_for_returned(interface=interface, cadet=cadet):
        attendance_across_events.update_attendance_for_cadet_on_day_at_event(
            event=event, cadet=cadet, day=day, new_attendance=returned
        )


def should_we_tick_cadet_as_present(
    interface: abstractInterface,
    attendance_across_events: DictOfAttendanceAcrossEvents,
    event: Event,
    day: Day,
    cadet: Cadet,
    force_mark_to_present: bool = False,
):
    if force_mark_to_present:
        current_attendance = (
            attendance_across_events.attendance_for_cadet_across_days_and_events(cadet)
            .attendance_for_cadet_at_event(event)
            .attendance_on_day(day)
            .current_attendance
        )
        if current_attendance == registration_not_taken:
            return True

    hastick_for_present = cadet_has_tick_for_present(interface=interface, cadet=cadet)
    hastick_for_late = cadet_has_tick_for_late(interface=interface, cadet=cadet)

    if hastick_for_present:
        if hastick_for_late:
            interface.log_error(
                "You ticked present AND late for %s - just tick one please. Assuming cadet will be late."
                % cadet.name
            )
            return False

        return True

    return False


def update_attendance_for_cadet_given_button(
    interface: abstractInterface,
    value_of_button: str,
    type_of_button: str,
    new_attendance: Attendance,
):
    cadet = get_cadet_given_button_pressed(
        button_value=value_of_button, button_type=type_of_button, interface=interface
    )
    event = get_event_from_state(interface)
    day = day_given_current_day_and_event(interface=interface, event=event)
    attendance_across_events = get_attendance_across_events_from_state(interface)

    attendance_across_events.update_attendance_for_cadet_on_day_at_event(
        event=event, cadet=cadet, day=day, new_attendance=new_attendance
    )

    update_attendance_across_events_for_list_of_cadets(
        object_store=interface.object_store,
        dict_of_attendance_across_events_for_list_of_cadets=attendance_across_events,
        list_of_cadets=attendance_across_events.list_of_cadets,
    )


def final_save_of_initial_registration(interface: abstractInterface):
    event = get_event_from_state(interface)
    day = day_given_current_day_and_event(interface=interface, event=event)
    attendance_across_events = get_attendance_across_events_from_state(interface)

    save_any_changes_to_ticks_passing_information(
        interface=interface,
        attendance_across_events=attendance_across_events,
        event=event,
        day=day,
        initial_stage=True,
        force_mark_to_present=False,
    )

    attendance_across_events.mark_all_unregistered_cadets_as_absent(
        day=day, event=event
    )

    update_attendance_across_events_for_list_of_cadets(
        object_store=interface.object_store,
        dict_of_attendance_across_events_for_list_of_cadets=attendance_across_events,
        list_of_cadets=attendance_across_events.list_of_cadets,
    )


def get_attendance_across_events_from_state(interface: abstractInterface):
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)

    return get_attendance_across_events_for_cadets_in_group_at_event(
        object_store=interface.object_store, event=event, group=group
    )


def return_to_parent(interface: abstractInterface) -> NewForm:
    clear_cadet_state(interface)
    return interface.get_new_display_form_for_parent_of_function(
        display_instructor_attendance
    )
