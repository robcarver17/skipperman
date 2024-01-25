from dataclasses import dataclass
from typing import Union, List

import pandas as pd

from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line


class PandasDFTable(pd.DataFrame):
    pass


@dataclass
class ElementsInTable:
    contents: Union[Line, Button, str, float]
    heading: bool = False


class RowInTable(list):
    def __init__(
        self, contents, has_column_headings: bool = False, is_heading_row: bool = False
    ):
        super().__init__(contents)
        self.has_column_headings = has_column_headings
        self.is_heading_row = is_heading_row

    def __repr__(self):
        return "Row: contents %s\n" % super().__repr__()

    def get_elements(self) -> List[ElementsInTable]:
        elements = []
        for idx, element in enumerate(self):
            is_heading = (idx == 0 and self.has_column_headings) or self.is_heading_row
            element = ElementsInTable(element, heading=is_heading)
            elements.append(element)

        return elements


class Table(list):
    def __init__(
        self,
        contents: list,
        has_column_headings: bool = False,
        has_row_headings: bool = False,
    ):
        super().__init__(contents)
        self.has_column_headings = has_column_headings
        self.has_row_headings = has_row_headings

    def __repr__(self):
        return "Table: contents %s\n" % super().__repr__()

    def get_rows(self) -> List[RowInTable]:
        rows = []
        for idx, row in enumerate(self):
            is_heading_row = idx == 0 and self.has_row_headings
            rows.append(
                RowInTable(
                    row,
                    has_column_headings=self.has_column_headings,
                    is_heading_row=is_heading_row,
                )
            )

        return rows
