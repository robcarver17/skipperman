from app.web.html.html import html_container_wrapper, html_link
from app.web.html.url import LOGIN_URL,LOGOUT_URL

login_link_html_code=html_container_wrapper.wrap_around(html_link('Login', '/%s' % LOGIN_URL))
logout_link_html_code=html_container_wrapper.wrap_around(html_link('Logout', '/%s' % LOGOUT_URL))

