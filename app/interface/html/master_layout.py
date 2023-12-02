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

style=""""
    <style type=")text/css" media="screen">

table{
border-collapse:collapse;
border:1px solid #FF0000;
}

table td{
border:1px solid #FF0000;
}
</style>
"""

master_wrapper = html_doc_wrapper(
    Html(
        """
    <title>Skipperman</title>
    %s
    """ % style
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
