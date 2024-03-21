from app.backend.reporting.arrangement.arrange_options import ArrangeGroupsOptions
from app.backend.reporting.arrangement.arrangement_methods import DEFAULT_ARRANGEMENT_NAME, ArrangementMethod
from app.backend.reporting.arrangement.arrangement_order import ArrangementOfColumns
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.constants import ARRANGE_GROUP_LAYOUT_METHOD, ARRANGE_GROUP_LAYOUT_ORDER
from app.objects.constants import missing_data


def get_stored_arrangement(interface: abstractInterface) -> ArrangeGroupsOptions:
    arrangement_method_as_str = interface.get_persistent_value(
        ARRANGE_GROUP_LAYOUT_METHOD
    )
    if arrangement_method_as_str is missing_data:
        arrangement_method_as_str = DEFAULT_ARRANGEMENT_NAME
        interface.set_persistent_value(
            ARRANGE_GROUP_LAYOUT_METHOD, arrangement_method_as_str
        )
    arrangement_method = ArrangementMethod[arrangement_method_as_str]

    arrangement_order_as_list = interface.get_persistent_value(
        ARRANGE_GROUP_LAYOUT_ORDER
    )
    if arrangement_order_as_list is missing_data:
        ## Don't bother storing, happy to pick up empty list next time
        arrangement_order = ArrangementOfColumns()
    else:
        arrangement_order = ArrangementOfColumns(arrangement_order_as_list)

    return ArrangeGroupsOptions(
        arrangement_method=arrangement_method,
        arrangement_of_columns=arrangement_order,
    )


def save_arrangement(
    interface: abstractInterface, arrangement_options: ArrangeGroupsOptions
):
    print("Saving arrangement %s" % str(arrangement_options))
    arrangement_method_as_str = arrangement_options.arrangement_method.name
    interface.set_persistent_value(
        ARRANGE_GROUP_LAYOUT_METHOD, arrangement_method_as_str
    )

    arrangement_order_as_list = list(arrangement_options.arrangement_of_columns)
    interface.set_persistent_value(
        ARRANGE_GROUP_LAYOUT_ORDER, arrangement_order_as_list
    )


def clear_arrangement_in_state(    interface: abstractInterface):
    interface.clear_persistent_value(ARRANGE_GROUP_LAYOUT_METHOD)
    interface.clear_persistent_value(ARRANGE_GROUP_LAYOUT_ORDER)


def modify_arrangement_given_change_in_group_order(interface: abstractInterface, indices_to_swap: tuple):
    ## Need to modify the indices in the matrix layout or that will change when should not
    arrangement_options = get_stored_arrangement(interface)
    arrangement_options.arrangement_of_columns.swap_indices(indices_to_swap)
    save_arrangement(arrangement_options=arrangement_options, interface=interface)


def modify_arrangement_options_given_custom_list(interface: abstractInterface, new_arrangement_of_columns: ArrangementOfColumns):
    arrangement_options = get_stored_arrangement(interface)
    ## will change method to custom
    arrangement_options.add_arrangement_of_columns(new_arrangement_of_columns)
    save_arrangement(arrangement_options=arrangement_options, interface=interface)
