from app.interface.html.html import (
    Html,
    HtmlWrapper,
    html_doc_wrapper,
    html_header_wrapper,
    html_h1_logo_wrapper,
    html_container_wrapper,
    html_joined_list_as_paragraphs,
)

## applies to all pages
## FIXME: Does CSS even work?

master_wrapper = html_doc_wrapper(
    Html(
        """
    <title>Skipperman</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">"""
    )
)

master_layout_html = HtmlWrapper(
    master_wrapper.wrap_around(
        html_joined_list_as_paragraphs(
            [
                html_header_wrapper.wrap_around(
                    html_container_wrapper.wrap_around(
                        html_h1_logo_wrapper.wrap_around(
                            Html("Skipperman: BSC Cadet Skipper Management System")
                        )
                    )
                ),
                Html("%s"),  ## body
            ]
        )
    )
)
