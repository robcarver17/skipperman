from typing import Dict

import pandas as pd
from dataclasses import dataclass
from app.OLD_backend.reporting.arrangement.arrange_options import (
    ArrangeGroupsOptions,
    ArrangementOptionsAndGroupOrder,
)
from app.OLD_backend.reporting.arrangement.group_order import (
    GroupOrder,
    get_group_order_from_dict_of_df_given_report_parameters,
)
from app.OLD_backend.reporting.options_and_parameters.print_options import PrintOptions
from app.OLD_backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.OLD_backend.reporting.options_and_parameters.marked_up_list_from_df_parameters import (
    MarkedUpListFromDfParametersWithActualGroupOrder,
)


@dataclass
class ReportingOptions:
    print_options: PrintOptions
    specific_parameters: SpecificParametersForTypeOfReport
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder
    dict_of_df: Dict[str, pd.DataFrame]
    arrange_options_and_group_order: ArrangementOptionsAndGroupOrder

    @property
    def arrangement(self) -> ArrangeGroupsOptions:
        return self.arrange_options_and_group_order.arrangement_options

    @property
    def group_order(self) -> GroupOrder:
        return self.arrange_options_and_group_order.group_order

    def filter_arrangement_options_in_place_to_remove_non_existent_groups(self):
        group_order_from_df = get_group_order_from_dict_of_df_given_report_parameters(
            dict_of_df=self.dict_of_df,
            specific_parameters_for_type_of_report=self.specific_parameters,
        )

        self.arrange_options_and_group_order.subset_if_in_other_group_order(
            group_order_from_df
        )
