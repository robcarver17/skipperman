from dataclasses import dataclass
from fpdf import FPDF

import numpy as np

from app.backend.reporting import PrintOptions
from app.data_access.configuration.fixed import (
    ALL_PAGESIZE,
    ALL_FONTS,
    UNIT_MM,
    MM_PER_POINT_OF_FONT_SIZE,
    APPROX_WIDTH_TO_HEIGHT_RATIO,
    TITLE_MULTIPLIER,
    LINE_GAP_AS_PERCENTAGE_OF_CHARACTER_HEIGHT,
    MAX_FONT_SIZE,
)
from app.backend.reporting import (
    PageWithColumns,
    MarkedUpString,
)


@dataclass
class PdfLayout:
    print_options: PrintOptions

    def add_page(self, page: PageWithColumns):
        self.setup_page(page)
        add_page_contents_to_pdf_layout(self, page)
        self.clear_page()

    def setup_page(self, page: PageWithColumns):
        self.page = page

        ## set up page in pdf
        pdf = self.pdf
        margin = self.edge_margin_measurement_units
        pdf.set_margins(left=margin, top=margin)
        pdf.set_auto_page_break(0)
        pdf.add_page()

    @property
    def page(self) -> PageWithColumns:
        page = getattr(self, "_page", None)
        if page is None:
            raise Exception("Need to add a page")

        return page

    @page.setter
    def page(self, page: PageWithColumns):
        self._page = page

    def clear_page(self):
        try:
            del self._page
        except:
            pass

    def add_title_to_page(self):
        title_str = self.title_str
        pdf = self.pdf
        pdf.set_font(self.font, "", self._title_font_size())
        margin = self.edge_margin_measurement_units
        pdf.set_xy(x=margin, y=margin)
        pdf.cell(
            w=self._title_area_width_measurement_units(),
            h=self._title_area_height_measurement_units(),
            txt=title_str,
            ln=0,
            align="C",
        )

    def put_text_on_page(
        self, column_number: int, line_number: int, marked_up_text: MarkedUpString
    ):
        x_point = self._x_cordinate_given_column_number(column_number)
        y_point = self._y_cordinate_given_line_number(line_number)

        pdf = self.pdf
        pdf.set_xy(x=x_point, y=y_point)
        style = get_style_for_marked_up_text(marked_up_text)
        pdf.set_font(self.font, style, self._font_size())
        pdf.multi_cell(
            w=self._column_width_for_nth_column_measurement_units(column_number),
            h=self._line_height_measurement_units(),
            txt=marked_up_text.string,
            align="L",
        )

    def output_file(self, path_and_filename: str):
        self.pdf.output(path_and_filename, "F")

    def _y_cordinate_given_line_number(self, line_number) -> float:
        height_required_for_title = (
            self._line_height_measurement_units() * TITLE_MULTIPLIER
        )
        margin = self.edge_margin_measurement_units
        y_cordinate_given_line_number_excluding_title_and_margin = (
            self._y_cordinate_given_line_number_excluding_title(line_number)
        )

        return (
            y_cordinate_given_line_number_excluding_title_and_margin
            + height_required_for_title
            + margin
        )

    def _y_cordinate_given_line_number_excluding_title(self, line_number) -> float:
        return self._line_height_measurement_units() * line_number

    def _x_cordinate_given_column_number(self, column_number) -> float:
        ## columns start at zero
        width_required_for_previous_columns = (
            self._width_required_for_previous_columns_measurement_units(column_number)
        )
        width_required_for_gaps = (
            self._width_required_for_previous_column_gaps_measurement_units(
                column_number
            )
        )
        margin = self.edge_margin_measurement_units

        return width_required_for_gaps + width_required_for_previous_columns + margin

    def _width_required_for_previous_columns_measurement_units(
        self, column_number
    ) -> float:
        previous_number_of_characters = self._number_of_characters_in_previous_columns(
            column_number
        )
        width_per_character = self._width_required_per_character_measurement_units()
        width_required_for_previous_columns = (
            previous_number_of_characters * width_per_character
        )

        return width_required_for_previous_columns

    def _number_of_characters_in_previous_columns(self, column_number: int) -> int:
        if self.equalise_column_width:
            return self._number_of_characters_in_previous_columns_if_equalised(
                column_number
            )
        else:
            return self._number_of_characters_in_previous_columns_if_not_equalised(
                column_number
            )

    def _number_of_characters_in_previous_columns_if_equalised(
        self, column_number: int
    ) -> int:
        max_characters_in_column = self._max_column_width_in_characters()
        return max_characters_in_column * column_number

    def _number_of_characters_in_previous_columns_if_not_equalised(
        self, column_number: int
    ) -> int:
        list_of_column_widths_in_characters = (
            self._list_of_column_widths_in_characters()
        )
        previous_column_widths_in_characters = list_of_column_widths_in_characters[
            :column_number
        ]
        previous_number_of_characters = sum(previous_column_widths_in_characters)

        return previous_number_of_characters

    def _width_required_for_previous_column_gaps_measurement_units(
        self, column_number
    ) -> float:
        if column_number == 0:
            return 0
        number_of_gaps = column_number
        width_required_for_gaps = self.column_gap_measurement_units * number_of_gaps

        return width_required_for_gaps

    def _column_width_for_nth_column_measurement_units(self, column_number):
        if self.equalise_column_width:
            return self._column_width_for_equalised_columns_measurement_units()
        else:
            return self._column_width_for_non_equalised_columns_measurement_units(
                column_number
            )

    def _column_width_for_equalised_columns_measurement_units(self) -> float:
        return (
            self._width_useable_for_columns_measurement_units()
            / self._number_of_columns()
        )

    def _column_width_for_non_equalised_columns_measurement_units(
        self, column_number
    ) -> float:
        list_of_column_widths = self._list_of_column_widths_in_characters()
        column_width_this_column_in_characters = list_of_column_widths[column_number]
        width_per_character = self._width_required_per_character_measurement_units()

        return width_per_character * column_width_this_column_in_characters

    def _list_of_column_widths_in_characters(self) -> list:
        return self.page.list_of_column_widths()

    def _line_height_measurement_units(self) -> float:
        ## different from self._height_required_per_line_measurement_units() as uses exact font size
        character_height_measurement_units = self._character_height_measurement_units()
        height_of_gap_between_lines = (
            LINE_GAP_AS_PERCENTAGE_OF_CHARACTER_HEIGHT
            * character_height_measurement_units
        )

        return character_height_measurement_units + height_of_gap_between_lines

    def _character_height_measurement_units(self) -> float:
        assert self.unit == UNIT_MM
        font_size = self._font_size()

        return font_size * MM_PER_POINT_OF_FONT_SIZE

    def _title_area_width_measurement_units(self):
        return self._useable_page_width_measurement_units()

    def _title_area_height_measurement_units(self):
        return (
            self._character_height_measurement_units()
            * self._lines_required_for_title()
        )

    def _lines_required_for_title(self):
        return TITLE_MULTIPLIER

    def _title_font_size(self):
        return self._font_size() * TITLE_MULTIPLIER

    def _font_size(self) -> int:
        if self.print_options.auto_font_size:
            approx_font_size_from_width = self._approx_font_size_from_width_required()
            approx_font_size_from_height = self._approx_font_size_from_height_required()

            max_possible_approx_font_size = min(
                [approx_font_size_from_width, approx_font_size_from_height]
            )
            font_size = int(np.floor(max_possible_approx_font_size))
            font_size = min([MAX_FONT_SIZE, font_size])

        else:
            return self.print_options.font_size

        return font_size

    def _approx_font_size_from_width_required(self) -> float:
        approx_point_size_from_width_excluding_title = (
            self._approx_font_size_from_width_required_excluding_title()
        )
        approx_point_size_from_title_width = (
            self._approx_font_size_from_width_required_for_title()
        )

        return min(
            [
                approx_point_size_from_width_excluding_title,
                approx_point_size_from_title_width,
            ]
        )

    def _approx_font_size_from_width_required_excluding_title(self) -> float:
        width_per_character = self._width_required_per_character_measurement_units()

        approx_point_size_from_width = self._approx_font_size_from_width_per_character(
            width_per_character
        )

        return approx_point_size_from_width

    def _approx_font_size_from_width_required_for_title(self) -> float:
        characters_in_title = len(self.title_str)
        total_available_width = self._useable_page_width_measurement_units()
        width_required_per_character_in_title = (
            total_available_width / characters_in_title
        )

        approx_point_size_from_width_of_title = (
            self._approx_font_size_from_width_per_character(
                width_required_per_character_in_title
            )
        )

        return approx_point_size_from_width_of_title

    def _approx_font_size_from_width_per_character(
        self, width_per_character: float
    ) -> float:
        approx_height_corresponding_to_width = (
            width_per_character / APPROX_WIDTH_TO_HEIGHT_RATIO
        )
        approx_point_size_from_width = self._approx_font_size_from_height_per_character(
            approx_height_corresponding_to_width
        )

        return approx_point_size_from_width

    def _approx_font_size_from_height_required(self) -> float:
        height_per_character = self._height_required_per_line_measurement_units()
        approx_point_size_from_height = (
            self._approx_font_size_from_height_per_character(height_per_character)
        )

        return approx_point_size_from_height

    def _approx_font_size_from_height_per_character(
        self, height_per_character: float
    ) -> float:
        assert self.unit == UNIT_MM
        approx_point_size_from_height = height_per_character / MM_PER_POINT_OF_FONT_SIZE

        return approx_point_size_from_height

    def _width_required_per_character_measurement_units(self) -> float:
        return (
            self._width_useable_for_columns_measurement_units()
            / self._total_characters_required_across_all_columns()
        )

    def _height_required_per_line_measurement_units(self) -> float:
        return (
            self._useable_page_height_measurement_units()
            / self._lines_required_on_page()
        )

    def _total_characters_required_across_all_columns(self) -> float:
        ## excludes gaps
        return self.page.width_in_characters_excluding_gaps(
            equalise_columns=self.equalise_column_width
        )

    def _lines_required_on_page(self) -> int:
        height_of_title_in_characters = self._lines_required_for_title()
        return self.page.height_in_characters(
            height_of_title_in_characters=height_of_title_in_characters
        )

    def _width_useable_for_columns_measurement_units(self):
        width_required_for_gaps = (
            self._number_of_columns() - 1
        ) * self.column_gap_measurement_units
        return self._useable_page_width_measurement_units() - width_required_for_gaps

    def _useable_page_width_measurement_units(self) -> float:
        return self._page_width_measurement_units() - (
            2 * self.edge_margin_measurement_units
        )

    def _useable_page_height_measurement_units(self) -> float:
        return self._page_height_in_measurement_units() - (
            2 * self.edge_margin_measurement_units
        )

    def _page_width_measurement_units(self) -> float:
        return self.print_options.page_width_measurement_units()

    def _page_height_in_measurement_units(self):
        return self.print_options.page_height_in_measurement_units()

    def _max_column_width_in_characters(self) -> int:
        return self.page.max_column_width()

    def _max_column_height_in_characters_including_gaps(self) -> int:
        return self.page.max_column_height_in_lines_including_gaps()

    def _number_of_columns(self) -> int:
        return self.page.number_of_columns

    @property
    def pdf(self):
        pdf = getattr(self, "_pdf", None)
        if pdf is None:
            pdf = FPDF(
                format=self.page_size, unit=self.unit, orientation=self.orientation
            )
            self._pdf = pdf

        return pdf

    @property
    def title_str(self) -> str:
        title_str_this_page = self.current_page_title_str
        master_title = self.print_options.title_str

        title_str = master_title + " " + title_str_this_page

        return title_str

    @property
    def current_page_title_str(self) -> str:
        title_str_this_page = self.page.title_str
        return title_str_this_page

    @property
    def edge_margin_measurement_units(self):
        return self.print_options.edge_margin_measurement_units

    @property
    def column_gap_measurement_units(self) -> float:
        return self.print_options.column_gap_measurement_units

    @property
    def orientation(self) -> str:
        return self.print_options.orientation

    @property
    def landscape(self) -> bool:
        return self.print_options.landscape

    @property
    def equalise_column_width(self) -> bool:
        return self.print_options.equalise_column_width

    @property
    def page_size(self) -> str:
        page_size = self.print_options.page_size
        assert page_size in ALL_PAGESIZE
        return page_size

    @property
    def font(self) -> str:
        font = self.print_options.font
        assert font in ALL_FONTS
        return font

    @property
    def unit(self) -> str:
        unit = self.print_options.unit
        return unit


def get_style_for_marked_up_text(marked_up_text: MarkedUpString) -> str:
    style = ""
    if marked_up_text.bold:
        style += "B"
    if marked_up_text.italics:
        style += "I"
    if marked_up_text.underline:
        style += "U"

    return style


def add_page_contents_to_pdf_layout(pdf_layout: PdfLayout, page: PageWithColumns):
    pdf_layout.add_title_to_page()

    for column_number, column in enumerate(page):
        line_number = 0
        for group in column:
            for marked_up_text in group:
                pdf_layout.put_text_on_page(
                    column_number=column_number,
                    line_number=line_number,
                    marked_up_text=marked_up_text,
                )
                line_number += 1

            ## end of group, add extra line
            line_number += 1
