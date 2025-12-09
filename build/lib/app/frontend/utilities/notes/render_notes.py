from app.backend.administration_and_utilities.notes import (
    get_list_of_notes_with_volunteers,
)
from app.backend.security.logged_in_user import get_loggged_in_volunteer
from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers
from app.data_access.configuration.fixed import SAVE_KEYBOARD_SHORTCUT
from app.objects.abstract_objects.abstract_buttons import HelpButton, Button
from app.objects.abstract_objects.abstract_form import (
    textAreaInput,
    checkboxInput,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.composed.notes_with_volunteers import (
    NoteWithVolunteer,
    SORT_BY_DATE,
    ListOfNotesWithVolunteers,
)

from app.objects.notes import LIST_OF_PRIORITIES

quick_note_text = "NEW_NOTE"
help_button = HelpButton("help_notes")


def get_quick_note_form() -> Line:
    return Line(
        [
            "Enter new note here",
            textAreaInput(input_name=quick_note_text, value="", input_label=""),
        ]
    )


save_quick_note_button = Button(
    "Save quick note", nav_button=False, shortcut=SAVE_KEYBOARD_SHORTCUT
)
save_table_entries = Button(
    "Save changes", nav_button=False, shortcut=SAVE_KEYBOARD_SHORTCUT
)


def get_existing_incomplete_notes(
    interface: abstractInterface, list_of_notes: ListOfNotesWithVolunteers
) -> Table:
    list_of_notes = list_of_notes.uncompleted_only()
    list_of_rows = [
        row_for_existing_note(
            existing_note_with_volunteer=existing_note_with_volunteer,
            interface=interface,
        )
        for existing_note_with_volunteer in list_of_notes
    ]

    return Table(
        [top_row_of_incomplete_table()] + list_of_rows, has_column_headings=True
    )


def get_existing_complete_notes(
    interface: abstractInterface, list_of_notes: ListOfNotesWithVolunteers
) -> Table:
    list_of_notes = list_of_notes.completed_only()
    list_of_rows = [
        row_for_existing_note(
            existing_note_with_volunteer=existing_note_with_volunteer,
            interface=interface,
        )
        for existing_note_with_volunteer in list_of_notes
    ]

    return Table([top_row_of_complete_table()] + list_of_rows, has_column_headings=True)


def top_row_of_incomplete_table():
    return [
        sort_by_author,
        sort_by_date,
        "Note",
        sort_by_assigned,
        sort_by_priority,
        "",
    ]


def top_row_of_complete_table():
    return ["Created by", "Date", "Note", "Assigned to", "Priority", ""]


sort_by_author = Button("Created by")
sort_by_date = Button("Date")
sort_by_assigned = Button("Assigned to")
sort_by_priority = Button("Priority")

sort_buttons = [sort_by_priority, sort_by_assigned, sort_by_author, sort_by_date]


def row_for_existing_note(
    interface: abstractInterface, existing_note_with_volunteer: NoteWithVolunteer
) -> RowInTable:
    author_name = existing_note_with_volunteer.author_volunteer.name
    created_date = existing_note_with_volunteer.created_datetime.strftime("%Y-%m-%d")
    text = note_text_box(
        interface, existing_note_with_volunteer=existing_note_with_volunteer
    )
    assigned = assigned_volunteer_dropdown(
        existing_note_with_volunteer=existing_note_with_volunteer, interface=interface
    )
    priority = priority_dropdown(
        interface, existing_note_with_volunteer=existing_note_with_volunteer
    )
    checkbox = completed_checkbox(
        interface, existing_note_with_volunteer=existing_note_with_volunteer
    )

    return RowInTable(
        [
            author_name,
            created_date,
            text,
            assigned,
            priority,
            checkbox,  ## always allow that
        ]
    )


def note_text_box(
    interface: abstractInterface, existing_note_with_volunteer: NoteWithVolunteer
):
    allow_edit = (
        not existing_note_with_volunteer.completed
        and existing_note_with_volunteer.author_volunteer
        == get_loggged_in_volunteer(interface)
    )
    if allow_edit:
        return textAreaInput(
            input_label="",
            input_name=get_input_name_for_note(existing_note_with_volunteer, TEXT),
            value=existing_note_with_volunteer.text,
        )
    else:
        return existing_note_with_volunteer.text


def assigned_volunteer_dropdown(
    interface: abstractInterface, existing_note_with_volunteer: NoteWithVolunteer
):
    allow_edit = (
        not existing_note_with_volunteer.completed
        and existing_note_with_volunteer.author_volunteer
        == get_loggged_in_volunteer(interface)
    )
    if allow_edit:
        return dropDownInput(
            default_label=existing_note_with_volunteer.assigned_volunteer.name,
            dict_of_options=get_dict_of_volunteer_names_and_ids(interface),
            input_label="",
            input_name=get_input_name_for_note(
                existing_note_with_volunteer, VOLUNTEER_ASSIGNED
            ),
        )
    else:
        return existing_note_with_volunteer.assigned_volunteer.name


def get_dict_of_volunteer_names_and_ids(interface: abstractInterface):
    list_of_volunteers = get_list_of_volunteers(interface.object_store)
    list_of_volunteers = list_of_volunteers.sort_by_firstname()
    return dict([(volunteer.name, volunteer.id) for volunteer in list_of_volunteers])


def priority_dropdown(
    interface: abstractInterface, existing_note_with_volunteer: NoteWithVolunteer
):
    allow_edit = (
        not existing_note_with_volunteer.completed
        and existing_note_with_volunteer.author_volunteer
        == get_loggged_in_volunteer(interface)
    )
    if allow_edit:
        return dropDownInput(
            default_label=existing_note_with_volunteer.priority,
            dict_of_options=dict_of_priorities,
            input_label="",
            input_name=get_input_name_for_note(existing_note_with_volunteer, PRIORITY),
        )
    else:
        return existing_note_with_volunteer.priority


def get_input_name_for_note(
    existing_note_with_volunteer: NoteWithVolunteer, attribute: str
):
    return "%s_%s" % (existing_note_with_volunteer.id, attribute)


def completed_checkbox(
    interface: abstractInterface, existing_note_with_volunteer: NoteWithVolunteer
):
    logged_in_volunteer = get_loggged_in_volunteer(interface)
    allow_edit = (
        existing_note_with_volunteer.assigned_volunteer == logged_in_volunteer
        or existing_note_with_volunteer.author_volunteer == logged_in_volunteer
    )
    if allow_edit:
        return checkboxInput(
            input_name=get_input_name_for_note(existing_note_with_volunteer, COMPLETED),
            input_label="",
            dict_of_labels={COMPLETED: COMPLETED},
            dict_of_checked={COMPLETED: existing_note_with_volunteer.completed},
        )
    else:
        completed = (
            "Completed" if existing_note_with_volunteer.completed else "Incomplete"
        )
        return completed


save_button = Button("Save", nav_button=True, shortcut=SAVE_KEYBOARD_SHORTCUT)
dict_of_priorities = dict([(priority, priority) for priority in LIST_OF_PRIORITIES])


def get_sorted_list_of_volunteer_notes(interface: abstractInterface):
    list_of_notes = get_list_of_notes_with_volunteers(
        object_store=interface.object_store
    )
    sort_name = get_sort_name(interface)

    return list_of_notes.sort_by(sort_name)


def get_sort_name(interface: abstractInterface):
    return interface.get_persistent_value(SORTBY, default=SORT_BY_DATE)


def update_sort_name(interface: abstractInterface, sort_by: str):
    return interface.set_persistent_value(SORTBY, sort_by)


VOLUNTEER_ASSIGNED = "volunteer_assigned"
PRIORITY = "priority"
COMPLETED = "completed"
TEXT = "text"
SORTBY = "sortbynotes"
