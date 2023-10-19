import sys
from data_access.api.csv_api import CsvDataApi
from interface.api.cli_api import CliInterfaceApi
from launcher.generic_launcher import GenericLauncher

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) < 2:
        raise Exception("Need to pass master_data_path as argument")

    master_data_path = arguments[1]
    launcher = GenericLauncher(
        data=CsvDataApi(master_data_path=master_data_path),
        interface=CliInterfaceApi(starting_directory_for_up_download=master_data_path),
    )
    launcher.run()

"""
from data_access.api.csv_api import CsvDataApi
from interface.api.cli_api import CliInterfaceApi
from launcher.generic_launcher import GenericLauncher

master_data_path = "/home/rob/skipperman_data/"
launcher = GenericLauncher(
    data=CsvDataApi(master_data_path=master_data_path),
    interface=CliInterfaceApi(starting_directory_for_up_download=master_data_path),
)
data_and_interface = launcher.logic.data_and_interface
"""
