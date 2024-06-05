from dataclasses import dataclass

from app.data_access.configuration.fixed import A4_PAGESIZE, UNIT_MM, WIDTH, HEIGHT, PAGESIZE_MM, TITLE_MULTIPLIER, \
    EDGE_MARGIN_MM, COLUMN_GAP_MM
from app.objects.events import Event
from app.objects.generic import GenericSkipperManObject


@dataclass
class PrintOptions(GenericSkipperManObject):
    filename: str = ""
    output_pdf: bool = True
    title_str: str = ""
    page_size: str = A4_PAGESIZE
    font: str = "Arial"
    unit: str = UNIT_MM  ## DO NOT CHANGE OR ALL HELL WILL BREAK LOOSE
    include_group_as_header: bool = True
    first_value_in_group_is_key: bool = False
    prepend_group_name: bool = False
    equalise_column_width: bool = True
    landscape: bool = True
    publish_to_public: bool = False
    include_size_of_group_if_header: bool = False
    
    @property
    def filename_with_extension(self):
        if self.output_pdf:
            return self.filename+".pdf"
        else:
            return self.filename+".xlsx"

    @classmethod
    def create_empty(cls):
        return cls()

    @property
    def height_of_title_in_characters(self) -> int:
        title_str = self.title_str
        if len(title_str) == 0:
            return 0
        else:
            return TITLE_MULTIPLIER

    def ratio_of_width_to_height(self) -> float:
        return (
            self.page_width_measurement_units()
            / self.page_height_in_measurement_units()
        )

    def page_width_measurement_units(self) -> float:
        page_sizes_dict = self._page_sizes_dict()
        if self.landscape:
            return page_sizes_dict[HEIGHT]
        else:
            return page_sizes_dict[WIDTH]

    def page_height_in_measurement_units(self):
        page_sizes_dict = self._page_sizes_dict()
        if self.landscape:
            return page_sizes_dict[WIDTH]
        else:
            return page_sizes_dict[HEIGHT]

    def _page_sizes_dict(self) -> dict:
        page_size = self.page_size
        assert self.unit == UNIT_MM
        page_sizes_dict = PAGESIZE_MM[page_size]

        return page_sizes_dict

    @property
    def edge_margin_measurement_units(self):
        assert self.unit == UNIT_MM
        return EDGE_MARGIN_MM

    @property
    def column_gap_measurement_units(self) -> float:
        assert self.unit == UNIT_MM
        return COLUMN_GAP_MM

    @property
    def orientation(self) -> str:
        if self.landscape:
            orientation = "L"
        else:
            orientation = "P"

        return orientation


def default_report_title_and_filename(event: Event, report_type: str) -> str:
    return "%s: %s" % (report_type, event.event_name)


def get_default_filename_for_report(default_title: str) -> str:
    default_file_name = default_title.replace(" ", "_")
    default_file_name = default_file_name.replace(":", "_")

    return default_file_name


