from app.objects.reporting_options import PrintOptions


class DataListOfPrintOptions(object):
    def read_for_report(self, report_name: str) -> PrintOptions:
        raise NotImplemented

    def write_for_report(self, report_name:str, print_options:PrintOptions):
        raise NotImplemented
