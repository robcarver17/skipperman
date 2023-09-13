import sys
from data_access.api.csv_api import CsvDataApi
from interface.api.web_api import WebInterfaceApi
from launcher.generic_launcher import GenericLauncher

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) < 2:
        raise Exception("Need to pass master_data_path as argument (this is where .csv files are stored)")

    master_data_path = arguments[1]
    launcher = GenericLauncher(
        data=CsvDataApi(master_data_path=master_data_path), interface=WebInterfaceApi()
    )
    launcher.run()
