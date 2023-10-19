from dataclasses import dataclass
from typing import List

from data_access.configuration.configuration import APPROX_WIDTH_TO_HEIGHT_RATIO


@dataclass
class MarkedUpString:
    string: str
    italics: bool = False
    bold: bool = False
    underline: bool = False

    @classmethod
    def bodytext(cls, string):
        return cls(string=string, bold=False, italics=False, underline=False)

    @classmethod
    def header(cls, string):
        return cls(string=string, bold=True, italics=False, underline=True)

    @classmethod
    def keyvalue(cls, string):
        return cls(string=string, bold=True, italics=False, underline=False)

    @property
    def width(self) -> int:
        return len(self.string)


class GroupOfMarkedUpString(List[MarkedUpString]):
    def max_width(self) -> int:
        line_widths = [marked_up_string.width for marked_up_string in self]
        return max(line_widths)


class ListOfGroupsOfMarkedUpStrings(List[GroupOfMarkedUpString]):
    pass


class Column(ListOfGroupsOfMarkedUpStrings):
    def number_of_lines_including_gaps(self) -> int:
        number_of_lines = sum([len(group) for group in self])
        number_of_gaps = len(self) - 1

        return number_of_lines + number_of_gaps

    def max_width(self) -> int:
        group_widths = [group.max_width() for group in self]

        return max(group_widths)


class ListtOfColumns(List[Column]):
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


def _create_columns_from_list_of_groups_of_marked_up_str_with_passed_list(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    order_list_of_indices: List[List[int]],
) -> ListtOfColumns:
    ## is passed list list of str?
    list_of_columns = ListtOfColumns(
        [
            _create_single_column_from_list_of_groups_of_marked_up_str_given_order(
                list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
                order_list_of_index_for_column=order_list_of_index_for_column,
            )
            for order_list_of_index_for_column in order_list_of_indices
        ]
    )

    return list_of_columns


def _create_single_column_from_list_of_groups_of_marked_up_str_given_order(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    order_list_of_index_for_column: List[int],
) -> Column:
    return Column(
        [
            list_of_groups_of_marked_up_str[index]
            for index in order_list_of_index_for_column
        ]
    )
