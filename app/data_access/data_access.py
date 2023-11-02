## In the unlikely event of switching to eg a database change here

from app.data_access.configuration.configuration import DATAPATH
from app.data_access.api.csv_api import CsvDataApi
import os

home_directory = os.path.expanduser('~')
master_data_path = os.path.join(home_directory, DATAPATH)

try:
    os.mkdir(master_data_path)
except:
    pass

data = CsvDataApi(master_data_path)
