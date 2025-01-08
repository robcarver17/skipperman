from app.backend.reporting import (
    ArrangementOptionsAndGroupOrder,
)
from app.backend.reporting import PrintOptions
from app.objects.groups import ListOfGroups


class DataListOfGroups(object):
    def read(self) -> ListOfGroups:
        raise NotImplemented

    def write(self, list_of_groups: ListOfGroups):
        raise NotImplemented


class DataListOfPrintOptions(object):
    def read_for_report(self, report_name: str) -> PrintOptions:
        raise NotImplemented

    def write_for_report(self, report_name: str, print_options: PrintOptions):
        raise NotImplemented


class DataListOfArrangementAndGroupOrderOptions(object):
    def read_for_report(self, report_name: str) -> ArrangementOptionsAndGroupOrder:
        raise NotImplemented

    def write_for_report(
        self, report_name: str, arrange_options: ArrangementOptionsAndGroupOrder
    ):
        raise NotImplemented
