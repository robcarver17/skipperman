import sys
from data_access.api.csv_api import CsvDataApi
from interface.api.web_api import WebInterfaceApi
from launcher.generic_launcher import GenericLauncher
from logic.api import LogicApi

from flask import Flask, render_template
app = Flask(__name__)

master_data_path = "/home/rob/skipperman_data/"
data=CsvDataApi(master_data_path=master_data_path)
interface=WebInterfaceApi()
logic_api = LogicApi(data=data, interface=interface)
data_and_interface = logic_api.data_and_interface

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cadets/')
def cadets():
    return render_template('cadets.html')


from logic.cadets.load_and_save_master_list_of_cadets import load_master_list_of_cadets
df = load_master_list_of_cadets(data_and_interface=data_and_interface).to_df_of_str()

@app.route('/view_cadets/')
def view_cadets():
    return render_template('view_cadets.html', column_names=df.columns.values, row_data=list(df.values.tolist()),
                           zip=zip)

@app.route('/events/')
def events():
    return render_template('events.html')

@app.route('/reports/')
def reports():
    return render_template('reports.html')


@app.route('/reports_group_allocation/')
def reports_group_allocation():
    return render_template('reports_group_allocation.html')


if __name__ == '__main__':
    app.run(debug=True)

