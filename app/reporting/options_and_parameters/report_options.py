import pandas as pd
from dataclasses import dataclass
from app.reporting.arrangement.arrange_options import ArrangeGroupsOptions
from app.reporting.arrangement.group_order import GroupOrder
from app.reporting.options_and_parameters.print_options import PrintOptions
from app.reporting.options_and_parameters.report_type_specific_parameters import SpecificParametersForTypeOfReport
from app.reporting.options_and_parameters.marked_up_list_from_df_parameters import MarkedUpListFromDfParametersWithActualGroupOrder


@dataclass
class ReportingOptions:
    print_options: PrintOptions
    group_order: GroupOrder
    specific_parameters: SpecificParametersForTypeOfReport
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder
    arrangement: ArrangeGroupsOptions
    df: pd.DataFrame


