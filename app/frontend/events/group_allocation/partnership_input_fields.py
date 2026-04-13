from app.backend.groups.data_for_group_display import *
from app.frontend.events.group_allocation.buttons import (
    button_name_for_delete_partner,
    button_name_for_add_partner,
)
from app.frontend.forms.form_utils import input_name_from_column_name_and_cadet_id
from app.frontend.shared.check_security import is_admin_or_skipper
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.cadets import Cadet
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.day_selectors import Day
from app.objects.partners import (
    no_partnership_given_partner_cadet,
    NoCadetPartner,
    from_no_partner_object_to_str,
    NO_PARTNERSHIP_LIST_OF_STR,
)
from app.objects.utilities.exceptions import missing_data


def get_input_for_partner_allocation_on_day(
    interface: abstractInterface,
    cadet: Cadet,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> ListOfLines:
    partner = get_two_handed_partner_for_cadet_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )
    if not is_admin_or_skipper(interface):
        return get_input_for_partner_allocation_on_day_if_no_edit_rights(
            partner_or_no_partner=partner
        )

    if no_partnership_given_partner_cadet(partner):
        return get_input_for_partner_allocation_on_day_with_no_existing_partner(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            day=day,
            no_partner_object=partner,
        )
    else:
        return get_input_for_partner_allocation_on_day_with_existing_partner(
            cadet=cadet, partner=partner
        )


def get_input_for_partner_allocation_on_day_if_no_edit_rights(
    partner_or_no_partner: Union[Cadet, NoCadetPartner]
):
    if no_partnership_given_partner_cadet(partner_or_no_partner):
        return ListOfLines([from_no_partner_object_to_str(partner_or_no_partner)])
    else:
        return ListOfLines([partner_or_no_partner.name])


def get_input_for_partner_allocation_on_day_with_existing_partner(
    cadet: Cadet, partner: Cadet
):
    return ListOfLines(
        [
            Line(partner.name),
            Button(
                value=button_name_for_delete_partner(cadet), label="Remove partnership"
            ),
        ]
    )


def get_input_for_partner_allocation_on_day_with_no_existing_partner(
    cadet: Cadet,
    no_partner_object: NoCadetPartner,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> ListOfLines:
    potential_partner_to_be_added_or_missing_data = (
        get_potential_partner_to_be_added_or_missing_data(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
        )
    )
    if potential_partner_to_be_added_or_missing_data is missing_data:
        return get_input_for_partner_allocation_on_day_with_no_existing_partner_when_no_potential_partner_available(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            day=day,
            no_partner_object=no_partner_object,
        )
    else:
        return get_input_for_partner_allocation_on_day_with_no_existing_partner_when_potential_partner_available(
            dict_of_all_event_data=dict_of_all_event_data,
            potential_partner=potential_partner_to_be_added_or_missing_data,
            existing_no_partner_object=no_partner_object,
            cadet=cadet,
            day=day,
        )


def get_input_for_partner_allocation_on_day_with_no_existing_partner_when_potential_partner_available(
    cadet: Cadet,
    day: Day,
    potential_partner: str,
    existing_no_partner_object: NoCadetPartner,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> ListOfLines:
    # current_partner_name = get_two_handed_partner_as_str_for_dropdown_cadet_on_day(
    #    dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    # )
    drop_down_input_field = get_dropdown_field_when_no_existing_partner(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        day=day,
        no_partner_object=existing_no_partner_object,
    )

    add_cadet_button = Button(
        value=button_name_for_add_partner(cadet),
        label="Add %s as new cadet" % potential_partner,
    )

    return ListOfLines([drop_down_input_field, add_cadet_button])


def get_input_for_partner_allocation_on_day_with_no_existing_partner_when_no_potential_partner_available(
    day: Day,
    cadet: Cadet,
    no_partner_object: NoCadetPartner,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> ListOfLines:
    return ListOfLines(
        [
            get_dropdown_field_when_no_existing_partner(
                day=day,
                cadet=cadet,
                no_partner_object=no_partner_object,
                dict_of_all_event_data=dict_of_all_event_data,
            )
        ]
    )


def get_dropdown_field_when_no_existing_partner(
    cadet: Cadet,
    no_partner_object: NoCadetPartner,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    day: Day = arg_not_passed,
) -> dropDownInput:
    list_of_other_cadets = get_list_of_available_cadet_names_including_asterix_marks_at_event_with_matching_schedules_excluding_this_cadet(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        available_on_specific_day=day,
    )

    drop_down_input_field = get_dropdown_field_for_partner_allocation(
        list_of_other_cadets=list_of_other_cadets,
        current_partner_name=from_no_partner_object_to_str(no_partner_object),
        cadet=cadet,
    )

    return drop_down_input_field


def get_dropdown_field_for_partner_allocation(
    cadet: Cadet,
    list_of_other_cadets: List[str],
    current_partner_name: str,
) -> dropDownInput:
    dict_of_all_possible_cadets = dict(
        [(cadet_name, cadet_name) for cadet_name in list_of_other_cadets]
    )

    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(PARTNER, cadet_id=cadet.id),
        input_label="",
        default_label=current_partner_name,
        dict_of_options=dict_of_all_possible_cadets,
    )

    return drop_down_input_field


PARTNER = "partner"


def get_input_for_partner_allocation_across_days(
    interface: abstractInterface,
    cadet: Cadet,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> ListOfLines:
    current_partner_name = (
        get_two_handed_partner_name_for_cadet_across_days_or_none_if_different(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    )
    if current_partner_name is None:
        return get_string_describing_two_handed_partner_name_across_days(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )

    if is_admin_or_skipper(interface):
        return get_input_for_partner_allocation_across_days_when_consistent(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
        )
    else:
        return ListOfLines([current_partner_name])


def get_input_for_partner_allocation_across_days_when_consistent(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> ListOfLines:
    partner = dict_of_all_event_data.dict_of_cadets_and_boat_class_and_partners.boat_classes_and_partner_for_cadet(
        cadet
    ).most_common_partner()

    if no_partnership_given_partner_cadet(partner):
        return get_input_for_partner_allocation_across_days_and_no_existing_partnership(
            cadet=cadet,
            dict_of_all_event_data=dict_of_all_event_data,
            no_partner_object=partner,
        )
    else:
        return get_input_for_partner_allocation_across_days_and_existing_partnership(
            partner=partner, cadet=cadet
        )


def get_input_for_partner_allocation_across_days_and_existing_partnership(
    partner: Cadet, cadet: Cadet
):
    return ListOfLines(
        [
            Line(partner.name),
            Button(
                value=button_name_for_delete_partner(cadet), label="Remove partnership"
            ),
        ]
    )


def get_input_for_partner_allocation_across_days_and_no_existing_partnership(
    cadet: Cadet,
    no_partner_object: NoCadetPartner,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
):
    potential_partner_to_be_added_or_missing_data = (
        get_potential_partner_to_be_added_or_missing_data(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
        )
    )
    if potential_partner_to_be_added_or_missing_data is missing_data:
        return get_input_for_partner_allocation_across_days_with_no_existing_partner_when_no_potential_partner_available(
            no_partner_object=no_partner_object,
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
        )
    else:
        return get_input_for_partner_allocation_across_days_with_no_existing_partner_when_potential_partner_available(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            no_partner_object=no_partner_object,
            potential_partner=potential_partner_to_be_added_or_missing_data,
        )


def get_input_for_partner_allocation_across_days_with_no_existing_partner_when_potential_partner_available(
    cadet: Cadet,
    no_partner_object: NoCadetPartner,
    potential_partner: str,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
):
    drop_down_input_field = get_dropdown_field_when_no_existing_partner(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        day=arg_not_passed,
        no_partner_object=no_partner_object,
    )

    add_cadet_button = Button(
        value=button_name_for_add_partner(cadet),
        label="Add %s as new cadet" % potential_partner,
    )

    return ListOfLines([drop_down_input_field, add_cadet_button])


def get_input_for_partner_allocation_across_days_with_no_existing_partner_when_no_potential_partner_available(
    cadet: Cadet,
    no_partner_object: NoCadetPartner,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
):
    return ListOfLines(
        [
            get_dropdown_field_when_no_existing_partner(
                day=arg_not_passed,  ## no specific match required
                cadet=cadet,
                no_partner_object=no_partner_object,
                dict_of_all_event_data=dict_of_all_event_data,
            )
        ]
    )
