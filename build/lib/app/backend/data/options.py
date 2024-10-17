from app.OLD_backend.reporting.arrangement.arrange_options import (
    ArrangeGroupsOptions,
    ArrangementOptionsAndGroupOrder,
)

from app.OLD_backend.reporting.options_and_parameters.print_options import PrintOptions

from app.data_access.store.data_access import DataLayer


class OptionsData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def reset_print_options_to_default(self, report_name: str):
        self.data_api.save_print_options(
            print_options=PrintOptions(), report_name=report_name
        )

    def reset_arrangement_options_to_default(self, report_name: str):
        return self.data_api.save_arrange_group_options(
            report_name=report_name,
            arrange_group_options=ArrangementOptionsAndGroupOrder.create_empty(),
        )

    def get_print_options(self, report_name: str) -> PrintOptions:
        return self.data_api.get_print_options(report_name)

    def save_print_options(self, print_options: PrintOptions, report_name: str):
        self.data_api.save_print_options(
            print_options=print_options, report_name=report_name
        )

    def get_arrange_group_options(
        self, report_name: str
    ) -> ArrangementOptionsAndGroupOrder:
        return self.data_api.get_arrange_group_options(report_name)

    def save_arrange_group_options(
        self, arrange_group_options: ArrangementOptionsAndGroupOrder, report_name: str
    ):
        self.data_api.save_arrange_group_options(
            arrange_group_options=arrange_group_options, report_name=report_name
        )
