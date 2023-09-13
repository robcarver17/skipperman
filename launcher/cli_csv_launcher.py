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
        data=CsvDataApi(master_data_path=master_data_path), interface=CliInterfaceApi()
    )
    launcher.run()
