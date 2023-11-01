from flask import Flask
from app.interface.menu_pages import generate_menu_page_html
from app.interface.action_pages import generate_action_page_html
from app.interface.html.url import INDEX_URL, ACTION_PREFIX, MENU_PREFIX
from app.data_access.configuration.configuration import SECRET_KEY

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

@app.route(INDEX_URL)
def home():
    return generate_menu_page_html()

@app.route('/%s/<menu_option>' % MENU_PREFIX)
def menu(menu_option):
    return generate_menu_page_html(menu_option)

@app.route('/%s/<action_option>' % ACTION_PREFIX, methods=["GET", "POST"])
def action(action_option):
    return generate_action_page_html(action_option)


if __name__ == '__main__':
    app.run(debug=True)