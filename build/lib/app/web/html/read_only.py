
from app.data_access.data import data_api
from app.web.flask.flask_interface import flaskInterface
from app.web.html.url import TOGGLE_READ_ONLY

PSEUDO_ACTION_NAME_FOR_MENU = 'Menu'

menu_interface = flaskInterface(data=data_api, action_name=PSEUDO_ACTION_NAME_FOR_MENU)


def toggle_read_only():
    print("Read only was %s, %s"% (str(menu_interface.read_only), str(read_only())))
    print("Store %s" % str(menu_interface.persistent_store))
    menu_interface.toggle_read_only()
    print("Read only now %s, %s"% (str(menu_interface.read_only), str(read_only())))
    print("Store %s" % str(menu_interface.persistent_store))

def read_only_or_not_html():
    if read_only():
        inner_text = 'Read only: Click to change'
    else:
        inner_text = 'Click for read only'

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (TOGGLE_READ_ONLY, inner_text)


def read_only():
    return menu_interface.read_only
