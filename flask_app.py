
from flask import Flask, render_template, request


from app.interface.html.menu_page import menu_page_html
from app.interface.html.action import action_html

app = Flask(__name__)

@app.route('/')
def home():
    return menu_page_html('home')

@app.route('/menu/<menu_option>')
def menu(menu_option):
    return menu_page_html(menu_option)

@app.route('/action/<action_option>', methods=["GET", "POST"])
def action(action_option):
    return action_html(action_option)


if __name__ == '__main__':
    app.run(debug=True)

