from app.backend.administration_and_utilities.notes import (
    get_list_of_notes_with_volunteers,
)
from app.backend.security.logged_in_user import get_loggged_in_volunteer
from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers
from app.frontend.utilities.notes.render_notes import (
    quick_note_text,
    get_input_name_for_note,
    VOLUNTEER_ASSIGNED,
    PRIORITY,
    COMPLETED,
    TEXT,
    sort_by_author,
    sort_by_date,
    sort_by_assigned,
    sort_by_priority,
    update_sort_name,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.notes_with_volunteers import (
    NoteWithVolunteer,
    SORT_BY_ASSIGNED,
    SORT_BY_AUTHOR,
    SORT_BY_PRIORITY,
    SORT_BY_DATE,
)
from app.objects.utilities.exceptions import MISSING_FROM_FORM, arg_not_passed
from app.backend.administration_and_utilities.notes import (
    add_quick_note,
    update_note_with_new_data,
)


def save_all_notes(interface: abstractInterface):
    
    save_quick_note(interface)
    update_all_existing_notes(interface)
    interface.flush_and_clear()


def save_quick_note(interface: abstractInterface):
    text = interface.value_from_form(quick_note_text, default=MISSING_FROM_FORM)
    if text is MISSING_FROM_FORM:
        interface.log_error("Problem with quick note form")
        return

    if len(text) == 0:
        return

    volunteer_author = get_loggged_in_volunteer(interface)
    add_quick_note(
        object_store=interface.object_store,
        text=text,
        volunteer_author=volunteer_author,
    )


def update_all_existing_notes(interface: abstractInterface):
    list_of_notes = get_list_of_notes_with_volunteers(
        object_store=interface.object_store
    )
    for note in list_of_notes:
        update_existing_note(interface=interface, note=note)


def update_existing_note(interface: abstractInterface, note: NoteWithVolunteer):
    assigned_volunteer = get_assigned_volunteer_from_form(
        interface=interface, note=note
    )
    completed = is_completed(interface=interface, note=note)
    priority = interface.value_from_form(
        get_input_name_for_note(note, PRIORITY), default=note.priority
    )
    text = interface.value_from_form(
        get_input_name_for_note(note, TEXT), default=note.text
    )

    update_note_with_new_data(
        interface.object_store,
        note_id=note.id,
        priority=priority,
        assigned_volunteer=assigned_volunteer,
        completed=completed,
        text=text,
    )


def get_assigned_volunteer_from_form(
    interface: abstractInterface, note: NoteWithVolunteer
):
    assigned_volunteer_id = interface.value_from_form(
        get_input_name_for_note(note, VOLUNTEER_ASSIGNED), default=MISSING_FROM_FORM
    )
    if (
        assigned_volunteer_id is MISSING_FROM_FORM
        or assigned_volunteer_id is arg_not_passed
    ):
        return note.assigned_volunteer

    list_of_volunteers = get_list_of_volunteers(interface.object_store)

    return list_of_volunteers.volunteer_with_id(assigned_volunteer_id)


def is_completed(interface: abstractInterface, note: NoteWithVolunteer):
    selected = interface.value_of_multiple_options_from_form(
        get_input_name_for_note(note, COMPLETED), default=MISSING_FROM_FORM
    )
    if selected is MISSING_FROM_FORM:
        return note.completed

    return COMPLETED in selected


def update_sort_status(interface: abstractInterface):
    pressed = interface.last_button_pressed()
    if sort_by_author.pressed(pressed):
        update_sort_name(interface, SORT_BY_AUTHOR)
    elif sort_by_date.pressed(pressed):
        update_sort_name(interface, SORT_BY_DATE)
    elif sort_by_assigned.pressed(pressed):
        update_sort_name(interface, SORT_BY_ASSIGNED)
    elif sort_by_priority.pressed(pressed):
        update_sort_name(interface, SORT_BY_PRIORITY)

    else:
        raise Exception("Button %s not known" % str(pressed))
