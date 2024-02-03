from app.backend.wa_import.update_master_event_data import get_dict_of_diffs_where_significant_values_changed, \
    get_list_of_field_names_from_dict_of_dict_diffs
from app.objects.abstract_objects.abstract_form import construct_form_field_given_field_name
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.master_event import RowInMasterEvent
from app.objects.utils import SingleDiff


def get_lines_in_form_for_other_differences(
    new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
    existing_row_in_master_event: RowInMasterEvent,
) -> ListOfLines:
    dict_of_dict_diffs = get_dict_of_diffs_where_significant_values_changed(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event,
    )
    print(dict_of_dict_diffs)
    list_of_field_names = get_list_of_field_names_from_dict_of_dict_diffs(
        dict_of_dict_diffs
    )
    print(list_of_field_names)
    list_of_form_fields = [
        form_field_for_item_with_difference(
            field_name=field_name, diff=dict_of_dict_diffs[field_name]
        )
        for field_name in list_of_field_names
    ]

    return ListOfLines(list_of_form_fields)


def form_field_for_item_with_difference(field_name: str, diff: SingleDiff) -> Line:
    form_field = construct_form_field_given_field_name(
        field_name=field_name,
        input_label="Field %s, was %s now %s: "
        % (field_name, diff.old_value, diff.new_value),
        input_name=field_name,
        value=diff.new_value,
    )

    return Line(form_field)
