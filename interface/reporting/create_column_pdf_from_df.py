from typing import List
import pandas as pd
from objects.constants import arg_not_passed

entry_columns = ["Cadet"]
group_by_column = "group"


def create_column_pdf_from_df(
    df: pd.DataFrame,
    entry_columns: List[str],
    title: str = arg_not_passed,
    group_by_column: str = arg_not_passed,
    include_group_as_header: bool = True,
    prepend_group_name: bool = False,
    first_value_in_group_is_key: bool = False,
    force_group_order: list = arg_not_passed,
):
    ## The two main reports I envisage doing are:
    ##     - an allocation report, grouped by groups
    ##     - a volunteer report, grouped by role
    ## In both cases we have the group underlined, then a list of items relating to that group underneath
    ## We want to fit everything on to one page of A4, adjusting # of columns and
    ##   font size as required to achieve that
    ## For volunteers we could also make the first name in each group bold
    ## return pdf filename
    ##
    pass
