from typing import List, Callable

from flask import flash, get_flashed_messages
from app.web.html.components import (
    HtmlWrapper,
    Html,
    horizontal_line,
    html_joined_list_as_lines,
)


def flash_error(my_string):
    flash(my_string, "error")


def flash_log(my_string):
    flash(my_string, "log")


def get_html_of_flashed_messages() -> List[Html]:
    all_errors_html = get_html_block_for_flash("error", html_error)
    all_logs_html = get_html_block_for_flash("log", html_log)

    return all_errors_html+all_logs_html


def get_html_block_for_flash(category_filter: str, html_transform: Callable) -> List[Html]:
    all_items_as_str = get_flashed_messages(category_filter=[category_filter])
    all_items_as_html = [html_transform(html_str) for html_str in all_items_as_str]

    return all_items_as_html

html_error_wraparound = HtmlWrapper('<h4 class="error">%s</h4>')


def html_error(html_str: str):
    return html_error_wraparound.wrap_around(Html(html_str))


def html_log(html_str: str):
    return Html(html_str)
