from typing import Union

from app.frontend.shared.add_edit_or_choose_volunteer_form import (
    skills_form_entries,
    get_and_save_volunteer_skills_from_form,
)
from app.frontend.shared.volunteer_state import (
    get_volunteer_from_state,
    update_state_with_volunteer_id,
    clear_volunteer_id_in_state,
)
from app.backend.volunteers.list_of_volunteers import get_volunteer_with_matching_name
from app.backend.volunteers.refresh_skills_from_csv_import import (
    load_skills_refresh_file,
    get_volunteer_from_row,
    delete_skills_refresh_file,
    compare_skills_for_volunteer_with_passed_and_return_warning,
)
from app.frontend.shared.add_or_select_volunteer import (
    get_add_or_select_existing_volunteer_form,
    ParametersForGetOrSelectVolunteerForm,
    generic_post_response_to_add_or_select_volunteer,
)
from app.objects.abstract_objects.abstract_buttons import (
    save_menu_button,
    cancel_menu_button,
    HelpButton,
    Button,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    ProgressBar,
    HorizontalLine,
    _______________,
)
from app.objects.skill_import import RowInImportedSkillsFile
from app.objects.utilities.exceptions import NoMoreData, missing_data
from app.objects.utilities.utils import percentage_of_x_in_y
from app.objects.volunteers import Volunteer


def begin_iteration_over_rows_in_temp_volunteer_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    reset_temp_volunteer_file_counter_to_first_value(interface)

    return process_current_volunteer_row_in_temp_file(interface=interface)


def process_current_volunteer_row_in_temp_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    volunteer_from_form = get_volunteer_from_current_row(interface)
    volunteer = get_volunteer_with_matching_name(
        object_store=interface.object_store,
        volunteer=volunteer_from_form,
        default=missing_data,
    )

    if volunteer is missing_data:
        return interface.get_new_form_given_function(
            display_volunteer_selection_in_skill_import_form
        )

    else:
        return process_row_when_volunteer_has_been_identified(
            interface=interface, volunteer=volunteer
        )


def display_volunteer_selection_in_skill_import_form(interface: abstractInterface):
    volunteer = get_volunteer_from_current_row(interface)
    parameters = get_form_parameters(interface)
    return get_add_or_select_existing_volunteer_form(
        interface=interface, volunteer=volunteer, parameters=parameters
    )


def get_form_parameters(
    interface: abstractInterface,
) -> ParametersForGetOrSelectVolunteerForm:
    header_text = get_header_text_for_volunteer_selection_form(interface)
    parameters_for_form = ParametersForGetOrSelectVolunteerForm(
        header_text=header_text,
        help_string="refresh_skills_with_import_help",
        extra_buttons=[skip_button],
    )
    return parameters_for_form


skip_button = Button("Skip")


def get_header_text_for_volunteer_selection_form(
    interface: abstractInterface,
) -> ListOfLines:
    # Custom header text
    progress_bar = ProgressBar(
        "Refreshing skills data",
        percentage_of_volunteer_ids_done_in_skills_file(interface),
    )
    return ListOfLines(
        [
            progress_bar,
            HorizontalLine(),
            "Cannot find volunteer exactly matching that in .csv in Skipperman data. Add as a new volunteer, choose the correct volunteer, or skip to ignore.",
        ]
    )


def post_volunteer_selection_in_skill_import_form(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    parameters = get_form_parameters(interface)

    result = generic_post_response_to_add_or_select_volunteer(
        interface=interface, parameters=parameters
    )
    if result.is_button:
        if result.button_pressed == skip_button:
            return next_volunteer_in_temporary_file(interface)
        else:
            interface.log_error(
                "Button %s not recognised, skipping volunteer in row"
                % result.button_pressed
            )
            return next_volunteer_in_temporary_file(interface)

    elif result.is_form:
        return result.form

    elif result.is_volunteer:
        volunteer = result.volunteer
        return process_row_when_volunteer_has_been_identified(
            interface=interface, volunteer=volunteer
        )
    else:
        raise Exception("Can't hanlde result %s" % str(result))


def process_row_when_volunteer_has_been_identified(
    interface: abstractInterface, volunteer: Volunteer
) -> Union[Form, NewForm]:
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)
    current_row = get_volunteer_row_from_temp_file_and_state(interface)

    warnings = compare_skills_for_volunteer_with_passed_and_return_warning(
        object_store=interface.object_store,
        volunteer=volunteer,
        current_row=current_row,
    )

    """
    try:

        warnings = compare_skills_for_volunteer_with_passed_and_return_warning(object_store=interface.object_store,
                                                                               volunteer=volunteer,
                                                                               current_row=current_row)
        
    except Exception as e:
        interface.log_error("Error %s when processing imported file" % str(e))
        warnings = []
    """

    if len(warnings) == 0:
        return next_volunteer_in_temporary_file(interface)
    else:
        return interface.get_new_form_given_function(
            display_skills_editing_form_when_mismatch
        )


def display_skills_editing_form_when_mismatch(interface: abstractInterface):
    progress_bar = ProgressBar(
        "Refreshing skills data",
        percentage_of_volunteer_ids_done_in_skills_file(interface),
    )
    volunteer = get_volunteer_from_state(interface)
    current_row = get_volunteer_row_from_temp_file_and_state(interface)
    warnings = compare_skills_for_volunteer_with_passed_and_return_warning(
        object_store=interface.object_store,
        volunteer=volunteer,
        current_row=current_row,
    )
    for warning in warnings:
        interface.log_error(warning)

    skills_entries = skills_form_entries(interface=interface, volunteer=volunteer)

    return Form(
        ListOfLines(
            [
                progress_bar,
                _______________,
                "Edit Skipperman skills for %s to mark any changes, and save. Or just hit save to keep existing skills. Or cancel to abandon the import - all changes saved so far will be kept."
                % volunteer.name,
                skills_entries,
                _______________,
                [save_menu_button, cancel_menu_button, help_button],
            ]
        ).add_Lines()
    )


help_button = HelpButton(
    "refresh_skills_with_import_help#reconciling-and-editing-skills"
)


def post_skills_editing_form_when_mismatch(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button):
        return return_to_calling_function(interface)
    else:
        volunteer = get_volunteer_from_state(interface)
        get_and_save_volunteer_skills_from_form(
            interface=interface, volunteer=volunteer
        )
        interface.flush_cache_to_store()

    clear_volunteer_id_in_state(interface)

    return next_volunteer_in_temporary_file(interface)


def next_volunteer_in_temporary_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        get_next_volunteer_row_and_store(interface)
    except NoMoreData:
        return return_to_calling_function(interface)

    return process_current_volunteer_row_in_temp_file(interface=interface)


def return_to_calling_function(interface: abstractInterface):
    interface.log_error("Finished refreshing skills")

    clear_state_for_specific_volunteer_id_in_temporary_file(interface)
    clear_volunteer_id_in_state(interface)
    delete_skills_refresh_file()

    interface.flush_cache_to_store()

    return interface.get_new_display_form_for_parent_of_function(
        display_volunteer_selection_in_skill_import_form
    )


### STATE


def get_volunteer_from_current_row(interface: abstractInterface) -> Volunteer:
    current_row = get_volunteer_row_from_temp_file_and_state(interface)
    volunteer_from_form = get_volunteer_from_row(current_row=current_row)

    return volunteer_from_form


def percentage_of_volunteer_ids_done_in_skills_file(
    interface: abstractInterface,
) -> int:
    list_of_volunteers_with_skills = load_skills_refresh_file()
    current_volunteer_idx = get_volunteer_idx_in_temporary_file_from_state(
        interface=interface
    )

    return percentage_of_x_in_y(current_volunteer_idx, list_of_volunteers_with_skills)


def reset_temp_volunteer_file_counter_to_first_value(
    interface: abstractInterface,
) -> RowInImportedSkillsFile:
    list_of_volunteers_with_skills = load_skills_refresh_file()
    first_row = list_of_volunteers_with_skills[0]

    ## We have to use underlying ID code, since we aren't dealing with the master list of volunteers
    update_state_for_specific_volunteer_id_in_temporary_file(interface=interface, idx=0)

    return first_row


def get_next_volunteer_row_and_store(
    interface: abstractInterface,
) -> RowInImportedSkillsFile:
    list_of_volunteers_with_skills = load_skills_refresh_file()
    current_volunteer_idx = get_volunteer_idx_in_temporary_file_from_state(
        interface=interface
    )

    next_idx = current_volunteer_idx + 1

    try:
        next_row = list_of_volunteers_with_skills[next_idx]
    except IndexError:
        raise NoMoreData

    update_state_for_specific_volunteer_id_in_temporary_file(
        interface=interface, idx=next_idx
    )

    return next_row


def get_volunteer_idx_in_temporary_file_from_state(interface: abstractInterface):
    return int(interface.get_persistent_value(TEMP_VOLUNTEER_ID))


def update_state_for_specific_volunteer_id_in_temporary_file(
    interface: abstractInterface, idx: int
):
    interface.set_persistent_value(key=TEMP_VOLUNTEER_ID, value=idx)


def clear_state_for_specific_volunteer_id_in_temporary_file(
    interface: abstractInterface,
):
    interface.clear_persistent_value(TEMP_VOLUNTEER_ID)


def get_volunteer_row_from_temp_file_and_state(
    interface: abstractInterface,
) -> RowInImportedSkillsFile:
    list_of_volunteer_skills = load_skills_refresh_file()
    current_volunteer_idx = get_volunteer_idx_in_temporary_file_from_state(interface)

    return list_of_volunteer_skills[current_volunteer_idx]


TEMP_VOLUNTEER_ID = "temp_volunteer_id"
