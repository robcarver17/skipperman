from dataclasses import dataclass
from typing import List, Union, Tuple, Dict

import pandas as pd
from app.backend.reporting.arrangement.arrange_options import (
    ArrangementOptionsAndGroupOrder,
)

from app.data_access.configuration.fixed import APPROX_WIDTH_TO_HEIGHT_RATIO
from app.objects.utilities.exceptions import arg_not_passed


@dataclass
class MarkedUpString:
    string: str
    original_contents_as_series: pd.Series
    italics: bool = False
    bold: bool = False
    underline: bool = False

    @classmethod
    def bodytext(
        cls,
        row: Union[str, pd.Series],
            index: int,
            group: str = arg_not_passed,
        prepend_group_name: bool = False,
            include_row_count: bool = False,
        dict_of_max_length: Dict[str, int] = arg_not_passed,
    ):
        (
            string,
            original_contents_as_series,
        ) = from_row_and_columns_to_string_and_original_contents(
            index=index,
            row=row,
            group=group,
            prepend_group_name=prepend_group_name,
            include_row_count=include_row_count,
            dict_of_max_length=dict_of_max_length,
        )
        return cls(
            string=string,
            original_contents_as_series=original_contents_as_series,
            bold=False,
            italics=False,
            underline=False,
        )

    @classmethod
    def header(
        cls,
        row: Union[str, pd.Series],
        group: str = arg_not_passed,
        prepend_group_name: bool = False,
        dict_of_max_length: Dict[str, int] = arg_not_passed,
    ):
        (
            string,
            original_contents_as_series,
        ) = from_row_and_columns_to_string_and_original_contents(
            row=row,
            group=group,
            prepend_group_name=prepend_group_name,
            dict_of_max_length=dict_of_max_length,
        )
        return cls(
            string=string,
            bold=True,
            italics=False,
            underline=True,
            original_contents_as_series=original_contents_as_series,
        )

    @classmethod
    def keyvalue(
        cls,
            index: int,
        row: Union[str, pd.Series],
        group: str = arg_not_passed,
        prepend_group_name: bool = False,
            include_row_count: bool = False,
            dict_of_max_length: Dict[str, int] = arg_not_passed,
    ):
        (
            string,
            original_contents_as_series,
        ) = from_row_and_columns_to_string_and_original_contents(
            index=index,
            row=row,
            group=group,
            prepend_group_name=prepend_group_name,
            dict_of_max_length=dict_of_max_length,
            include_row_count=include_row_count
        )
        return cls(
            string=string,
            bold=True,
            italics=False,
            underline=False,
            original_contents_as_series=original_contents_as_series,
        )

    @property
    def width(self) -> int:
        return len(self.string)


def from_row_and_columns_to_string_and_original_contents(
    row: Union[str, pd.Series],
    group: str = arg_not_passed,
    prepend_group_name: bool = False,
        include_row_count: bool= False,
    dict_of_max_length: Dict[str, int] = arg_not_passed,
        index = arg_not_passed
) -> Tuple[str, pd.Series]:
    if type(row) is str:
        string = row
        return string, pd.Series(dict(text=string))

    original_contents_as_dict=row.to_dict()

    original_contents_as_dict = reformat_to_max_length_padding(
        original_contents_as_dict=original_contents_as_dict,
        dict_of_max_length=dict_of_max_length,
    )
    if include_row_count and index is not arg_not_passed:
        contents_as_dict = {'': str(index+1)}
        contents_as_dict.update(original_contents_as_dict)
    else:
        contents_as_dict = original_contents_as_dict

    original_contents_as_series = pd.Series(contents_as_dict)

    original_contents_as_list = original_contents_as_series.to_list()
    string = " ".join(original_contents_as_list)
    if prepend_group_name:
        string = "%s: %s" % (group, string)

    return string, original_contents_as_series


def reformat_to_max_length_padding(
    original_contents_as_dict: Dict[str, str],
    dict_of_max_length: Dict[str, int] = arg_not_passed,
) -> Dict[str, str]:
    if dict_of_max_length is arg_not_passed:
        return original_contents_as_dict

    for key in original_contents_as_dict.keys():
        original_string = original_contents_as_dict[key]
        original_length = dict_of_max_length[key]

        original_contents_as_dict[key] = original_string.ljust(original_length)

    return original_contents_as_dict


class GroupOfMarkedUpString(List[MarkedUpString]):
    def max_width(self) -> int:
        line_widths = [marked_up_string.width for marked_up_string in self]
        if len(self) == 0:
            return 0

        return max(line_widths)


EMPTY_GROUP = GroupOfMarkedUpString([])


class ListOfGroupsOfMarkedUpStrings(List[GroupOfMarkedUpString]):
    pass


class Page(List[GroupOfMarkedUpString]):
    def __init__(
        self, list_of_marked_up_string: List[GroupOfMarkedUpString], title_str: str = ""
    ):
        super().__init__(list_of_marked_up_string)
        self.title_str = title_str

    @property
    def group_names(self):
        return getattr(self, "_group_names", [])

    @group_names.setter
    def group_names(self, group_names: List[str]):
        self._group_names = group_names


class ListOfPages(List[Page]):
    def unique_list_of_groups_across_all_pages(self):
        list_of_groups = []
        for page in self:
            list_of_groups += page.group_names

        return list(set(list_of_groups))


class Column(ListOfGroupsOfMarkedUpStrings):
    def number_of_lines_including_gaps(self) -> int:
        number_of_lines = sum([len(group) for group in self])
        number_of_gaps = len(self) - 1

        return number_of_lines + number_of_gaps

    def max_width(self) -> int:
        group_widths = [group.max_width() for group in self]
        if len(group_widths) == 0:
            return 0

        return max(group_widths)


class PageWithColumns(List[Column]):
    def __init__(self, list_of_columns: List[Column], title_str: str = ""):
        super().__init__(list_of_columns)
        self.title_str = title_str

    @property
    def has_title(self):
        return len(self.title_str) > 0

    def list_of_column_widths(self) -> List[int]:
        widths_of_each_column = [list_of_groups.max_width() for list_of_groups in self]
        return widths_of_each_column

    def total_character_width_across_all_columns(self) -> int:
        widths_of_each_column = self.list_of_column_widths()
        return sum(widths_of_each_column)

    def max_column_width(self) -> int:
        widths_of_each_column = [list_of_groups.max_width() for list_of_groups in self]
        return max(widths_of_each_column)

    def max_column_height_in_lines_including_gaps(self):
        column_heights = [
            list_of_groups.number_of_lines_including_gaps() for list_of_groups in self
        ]
        return max(column_heights)

    def ratio_of_required_width_to_height(
        self, equalise_columns: bool = True, height_of_title_in_characters: int = 0
    ) -> float:
        width_in_characters = self.width_in_characters_including_gaps(
            equalise_columns=equalise_columns
        )
        height_in_characters = self.height_in_characters(
            height_of_title_in_characters=height_of_title_in_characters
        )
        ratio_in_character_terms = float(width_in_characters) / float(
            height_in_characters
        )
        corrected_ratio = ratio_in_character_terms * APPROX_WIDTH_TO_HEIGHT_RATIO

        return corrected_ratio

    def width_in_characters_including_gaps(self, equalise_columns: bool = True) -> int:
        width_excluding_gaps = self.width_in_characters_excluding_gaps(
            equalise_columns=equalise_columns
        )
        gaps = max([self.number_of_columns - 1, 0])

        return width_excluding_gaps + gaps

    def width_in_characters_excluding_gaps(self, equalise_columns: bool = True) -> int:
        if equalise_columns:
            width = self.total_character_width_across_all_columns()
        else:
            width = self.max_column_width() * len(self)

        return width

    def height_in_characters(self, height_of_title_in_characters: int = 0) -> int:
        return (
            self.max_column_height_in_lines_including_gaps()
            + height_of_title_in_characters
        )

    @property
    def number_of_columns(self) -> int:
        return len(self)


class ListOfPagesWithColumns(List[PageWithColumns]):
    pass


def create_list_of_pages_with_columns_from_list_of_pages_and_arrangement_options(
    list_of_pages: ListOfPages,
    arrangement_options_and_group_order: ArrangementOptionsAndGroupOrder,
) -> ListOfPagesWithColumns:
    list_of_pages_with_columns = [
        create_columns_from_page(
            page=page,
            arrangement_options_and_group_order=arrangement_options_and_group_order,
        )
        for page in list_of_pages
    ]

    return ListOfPagesWithColumns(list_of_pages_with_columns)


def create_columns_from_page(
    page: Page,
    arrangement_options_and_group_order: ArrangementOptionsAndGroupOrder,
) -> PageWithColumns:
    ## is passed list list of str?
    master_group_order = arrangement_options_and_group_order.group_order
    arrangement_of_columns = (
        arrangement_options_and_group_order.arrangement_options.arrangement_of_columns
    )

    list_of_columns = []
    for order_list_of_index_for_column in arrangement_of_columns:
        single_column = (
            _create_single_column_from_list_of_groups_of_marked_up_str_given_order(
                page=page,
                order_list_of_index_for_column=order_list_of_index_for_column,
                master_group_order=master_group_order,
            )
        )
        if len(single_column) == 0:
            continue
        else:
            list_of_columns.append(single_column)

    return PageWithColumns(list_of_columns, title_str=page.title_str)


def _create_single_column_from_list_of_groups_of_marked_up_str_given_order(
    page: Page, order_list_of_index_for_column: List[int], master_group_order: List[str]
) -> Column:
    column_as_list = []
    groups_in_page = page.group_names
    for index in order_list_of_index_for_column:
        group_name = master_group_order[index]
        try:
            index_of_group_in_page = groups_in_page.index(group_name)
            relevant_group_in_page = page[index_of_group_in_page]
            column_as_list.append(relevant_group_in_page)
        except:
            ## missing from this page that's fine
            continue

    return Column(column_as_list)
