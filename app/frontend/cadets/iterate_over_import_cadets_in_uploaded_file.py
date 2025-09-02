from typing import Union

from app.backend.cadets.add_edit_cadet import (
    add_new_verified_cadet,
    modify_cadet_date_of_birth,
)

from app.backend.cadets.iterate_over_membership_list import (
    set_all_current_members_to_temporary_unconfirmed,
    confirm_cadet_is_member,
    set_all_temporary_unconfirmed_members_to_lapsed_and_return_list,
    set_all_user_unconfirmed_members_to_non_members_and_return_list,
)
from app.backend.cadets.import_membership_list import (
    remove_temp_file_with_list_of_cadet_members,
    get_temp_cadet_file_list_of_memberships,
)
from app.backend.cadets.list_of_cadets import (
    are_there_no_similar_cadets,
    get_matching_cadet,
)
from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME_ON_MATCHING_MEMBERSHIP_LIST,
)


from app.frontend.shared.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
    ParametersForGetOrSelectCadetForm,
    generic_post_response_to_add_or_select_cadet,
    skip_button,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    ProgressBar,
    HorizontalLine,
)

from app.objects.cadets import Cadet
from app.objects.membership_status import (
    current_member,
    system_unconfirmed_member,
    describe_status,
)
from app.objects.utilities.exceptions import NoMoreData, MissingData
from app.objects.utilities.utils import percentage_of_x_in_y


def begin_iteration_over_rows_in_temp_cadet_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    set_all_current_members_to_temporary_unconfirmed(
        object_store=interface.object_store
    )
    first_cadet = reset_temp_cadet_file_counter_to_first_value(interface)

    return process_current_cadet_in_temp_file(
        interface=interface, current_cadet=first_cadet
    )


def process_current_cadet_in_temp_file(
    interface: abstractInterface, current_cadet: Cadet
) -> Union[Form, NewForm]:
    object_store = interface.object_store
    try:
        cadet_in_data = get_matching_cadet(
            object_store=object_store, cadet=current_cadet
        )
        print(
            "Identical cadet to %s already exists - marking as confirmed member"
            % str(cadet_in_data)
        )
        mark_existing_cadet_as_member_and_log(interface=interface, cadet=cadet_in_data)

        return next_iteration_over_rows_in_temp_cadet_file(interface)

    except MissingData:
        print("No exact matching cadet found for %s" % current_cadet)
        return process_current_cadet_in_temp_file_when_no_exact_match(
            interface=interface, current_cadet=current_cadet
        )


def process_current_cadet_in_temp_file_when_no_exact_match(
    interface: abstractInterface, current_cadet: Cadet
) -> Union[Form, NewForm]:
    no_similar_cadets = are_there_no_similar_cadets(
        object_store=interface.object_store,
        cadet=current_cadet,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME_ON_MATCHING_MEMBERSHIP_LIST,
    )

    if no_similar_cadets:
        ##### add cadet
        print("No similar cadets to %s adding automatically" % str(current_cadet))
        current_cadet.membership_status = (
            current_member  ## should be set already, but just in case
        )
        return process_when_cadet_is_in_membership_list_and_not_in_system(
            interface=interface, cadet=current_cadet
        )

    ### display form to choose between similar cadets
    return interface.get_new_form_given_function(
        display_verify_adding_cadet_from_list_form
    )


def mark_existing_cadet_as_member_and_log(interface: abstractInterface, cadet: Cadet):
    if cadet.membership_status == system_unconfirmed_member:
        ## don't log, too much spam otherwise
        print("Cadet %s was member, still member" % str(cadet))
    else:
        ## genuine change in state
        interface.log_error(
            "Cadet %s was %s, confirming as member"
            % (cadet.name, describe_status(cadet.membership_status))
        )

    interface.lock_cache()
    confirm_cadet_is_member(object_store=interface.object_store, cadet=cadet)
    interface.save_changes_in_cached_data_to_disk()


def next_iteration_over_rows_in_temp_cadet_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        next_cadet = get_next_cadet_and_store(interface)
    except NoMoreData:
        return finishing_processing_file(interface)

    return process_current_cadet_in_temp_file(
        interface=interface, current_cadet=next_cadet
    )


from app.objects.cadets import is_cadet_age_surprising


def process_when_cadet_is_in_membership_list_and_not_in_system(
    interface: abstractInterface, cadet: Cadet
) -> Form:
    if is_cadet_age_surprising(cadet):
        ## ignoring, probably not a cadet
        print("Ignoring the import of %s as too old or young to be a cadet")
        return next_iteration_over_rows_in_temp_cadet_file(interface)

    return process_when_cadet_to_be_added_from_membership_list(
        interface=interface, cadet=cadet
    )


def process_when_cadet_to_be_added_from_membership_list(
    interface: abstractInterface, cadet: Cadet
) -> Form:
    interface.lock_cache()
    add_new_verified_cadet(object_store=interface.object_store, cadet=cadet)
    interface.log_error(
        "Automatically added new cadet from membership list %s" % str(cadet)
    )
    interface.save_changes_in_cached_data_to_disk()

    return next_iteration_over_rows_in_temp_cadet_file(interface)


def process_when_cadet_already_added_from_form(
    interface: abstractInterface, cadet: Cadet
) -> Form:
    interface.log_error("Added new cadet  %s" % str(cadet))

    return next_iteration_over_rows_in_temp_cadet_file(interface)


def display_verify_adding_cadet_from_list_form(interface: abstractInterface) -> Form:
    current_cadet = get_cadet_from_temp_file_and_state(interface)

    edit_or_add_form_parameters = get_form_parameters(interface)

    return get_add_or_select_existing_cadet_form(
        cadet=current_cadet, interface=interface, parameters=edit_or_add_form_parameters
    )


def get_form_parameters(interface: abstractInterface):
    return ParametersForGetOrSelectCadetForm(
        header_text=get_header_text(interface),
        help_string="import_membership_list_help",
        similarity_name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME_ON_MATCHING_MEMBERSHIP_LIST,
        extra_buttons=[skip_button],
    )


def get_header_text(interface: abstractInterface):
    progress_bar = ProgressBar(
        "Importing cadets from membership list: ",
        percentage_of_cadet_ids_done_in_registration_file(interface),
    )
    provided_header_text = ListOfLines(
        [
            progress_bar,
            HorizontalLine(),
            "Looks like a potentially new cadet in the membership list - or could just be an existing member with slightly different details.',"
            " Click on the existing cadet that matches this one (this will verify they are a member), or add cadet if really a new member, or skip if not a cadet or junior member",
        ]
    )
    return provided_header_text


def post_verify_adding_cadet_from_list_form(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    edit_or_add_form_parameters = get_form_parameters(interface)

    result = generic_post_response_to_add_or_select_cadet(
        interface=interface, parameters=edit_or_add_form_parameters
    )

    if result.is_form:
        return result.form

    elif result.is_button:
        if result.button_pressed == skip_button:
            return next_iteration_over_rows_in_temp_cadet_file(interface)
        else:
            interface.log_error(
                "Button %s not recognised - contact support - skipping cadet in file"
                % str(result.button_pressed)
            )
            return next_iteration_over_rows_in_temp_cadet_file(interface)

    elif result.is_cadet:
        assert type(result.cadet) is Cadet
        if result.cadet_was_added:
            return process_when_cadet_already_added_from_form(
                interface=interface, cadet=result.cadet
            )
        else:
            return confirm_selected_cadet_is_member(
                interface=interface, existing_cadet=result.cadet
            )
    else:
        raise Exception("Return result %s cannot handle" % str(result))


def confirm_selected_cadet_is_member(
    interface: abstractInterface, existing_cadet: Cadet
):

    cadet_in_file = get_cadet_from_temp_file_and_state(interface)
    change_or_warn_on_discrepancy(
        interface=interface, cadet_in_file=cadet_in_file, existing_cadet=existing_cadet
    )
    mark_existing_cadet_as_member_and_log(interface=interface, cadet=existing_cadet)

    return next_iteration_over_rows_in_temp_cadet_file(interface)


def change_or_warn_on_discrepancy(
    interface: abstractInterface, existing_cadet: Cadet, cadet_in_file: Cadet
):
    if existing_cadet.name != cadet_in_file.name:
        interface.log_error(
            "Uploaded membership list has name %s, existing Skipperman data has name %s - not changing; but consider if Skipperman is correct (fine if a nickname)"
            % (existing_cadet.name, cadet_in_file.name)
        )

    if existing_cadet.date_of_birth != cadet_in_file.date_of_birth:
        if existing_cadet.has_default_date_of_birth:
            new_date_of_birth = cadet_in_file.date_of_birth
            interface.log_error(
                "Existing skipperman data has no date of birth for %s, updating to DOB in membership file of %s"
                % (existing_cadet.name, new_date_of_birth)
            )
            modify_cadet_date_of_birth(
                object_store=interface.object_store,
                existing_cadet=existing_cadet,
                new_date_of_birth=new_date_of_birth,
            )
        else:
            interface.log_error(
                "Discrepancy in dates of birth for %s between Skipperman data %s and DOB in membership file %s - find out what is correct and edit Skipperman if required"
                % (
                    existing_cadet.name,
                    str(existing_cadet.date_of_birth),
                    str(cadet_in_file.date_of_birth),
                )
            )


### STATE


def percentage_of_cadet_ids_done_in_registration_file(
    interface: abstractInterface,
) -> int:
    list_of_cadets = get_temp_cadet_file_list_of_memberships()
    current_cadet_id = get_cadet_id_in_temporary_file_from_state(interface=interface)

    current_idx = list_of_cadets.index_of_id(current_cadet_id)

    return percentage_of_x_in_y(current_idx, list_of_cadets)


def reset_temp_cadet_file_counter_to_first_value(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file_list_of_memberships()
    first_cadet = list_of_cadets[0]

    ## We have to use underlying ID code, since we aren't dealing with the master list of cadets
    update_state_for_specific_cadet_id_in_temporary_file(
        interface=interface, cadet_id=first_cadet.id
    )

    return first_cadet


def get_next_cadet_and_store(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file_list_of_memberships()
    current_cadet_id = get_cadet_id_in_temporary_file_from_state(interface=interface)

    current_idx = list_of_cadets.index_of_id(current_cadet_id)
    next_idx = current_idx + 1

    try:
        next_cadet = list_of_cadets[next_idx]
    except IndexError:
        raise NoMoreData

    update_state_for_specific_cadet_id_in_temporary_file(
        interface=interface, cadet_id=next_cadet.id
    )

    return next_cadet


def get_cadet_id_in_temporary_file_from_state(interface: abstractInterface):
    return interface.get_persistent_value(TEMP_CADET_ID)


def update_state_for_specific_cadet_id_in_temporary_file(
    interface: abstractInterface, cadet_id: str
):
    interface.set_persistent_value(key=TEMP_CADET_ID, value=cadet_id)


def clear_state_for_specific_cadet_id_in_temporary_file(interface: abstractInterface):
    interface.clear_persistent_value(TEMP_CADET_ID)


def get_cadet_from_temp_file_and_state(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file_list_of_memberships()
    current_cadet_id = get_cadet_id_in_temporary_file_from_state(interface=interface)
    current_idx = list_of_cadets.index_of_id(current_cadet_id)

    return list_of_cadets[current_idx]


TEMP_CADET_ID = "temp_cadet_id"

## FINISHED


def finishing_processing_file(interface: abstractInterface) -> NewForm:
    remove_temp_file_with_list_of_cadet_members()
    set_all_unconfirmed_members_to_lapsed_and_log(interface)
    clear_state_for_specific_cadet_id_in_temporary_file(interface)

    return interface.get_new_display_form_for_parent_of_function(
        display_verify_adding_cadet_from_list_form
    )


def set_all_unconfirmed_members_to_lapsed_and_log(interface: abstractInterface):
    interface.lock_cache()
    lapsed_members = set_all_temporary_unconfirmed_members_to_lapsed_and_return_list(
        object_store=interface.object_store
    )
    for cadet in lapsed_members:
        interface.log_error(
            "Existing sailor %s who was a member is not in membership list and has been marked as lapsed: no longer a member: CHECK!"
            % cadet
        )

    not_members = set_all_user_unconfirmed_members_to_non_members_and_return_list(
        object_store=interface.object_store
    )
    interface.save_changes_in_cached_data_to_disk()

    for cadet in not_members:
        interface.log_error(
            "Unconfirmed sailor %s is not in membership list and has been marked as a non member"
            % cadet
        )
