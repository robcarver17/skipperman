from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.backend.reporting.arrangement.arrange_options import ArrangeGroupsOptions, ArrangementOptionsAndGroupOrder


class DataListOfPrintOptions(object):
    def read_for_report(self, report_name: str) -> PrintOptions:
        raise NotImplemented

    def write_for_report(self, report_name: str, print_options: PrintOptions):
        raise NotImplemented


class DataListOfArrangementAndGroupOrderOptions(object):
    def read_for_report(self, report_name: str) -> ArrangementOptionsAndGroupOrder:
        raise NotImplemented

    def write_for_report(self, report_name: str, arrange_options: ArrangementOptionsAndGroupOrder):
        raise NotImplemented

