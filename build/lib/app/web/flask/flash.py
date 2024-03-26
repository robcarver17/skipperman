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


def get_html_of_flashed_messages() -> Html:
    all_errors_html = get_html_block_for_flash("error", html_error)
    all_logs_html = get_html_block_for_flash("log", html_log)

    return html_joined_list_as_lines([all_errors_html, all_logs_html])


def get_html_block_for_flash(category_filter: str, html_transorm):
    all_items_as_str = get_flashed_messages(category_filter=[category_filter])
    all_items_as_html = [html_transorm(html_str) for html_str in all_items_as_str]

    if len(all_items_as_html) == 0:
        return Html("")
    else:
        return html_joined_list_as_lines(
            [
                horizontal_line,
                html_joined_list_as_lines(all_items_as_html),
                horizontal_line,
            ]
        )


html_error_wraparound = HtmlWrapper('<h2 class="error">%s</h2>')  ## FIXME ADD CSS


def html_error(html_str: str):
    return html_error_wraparound.wrap_around(Html(html_str))


def html_log(html_str: str):
    return Html(html_str)
