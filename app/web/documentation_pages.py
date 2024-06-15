from app.web.html.components import (
    Html,
)
from app.web.html.master_layout import get_master_layout
from app.data_access.primitives import get_relative_pathname_from_list


def generate_help_page_html(help_page_name: str) -> Html:
    html_for_help_text =get_help_text_as_html_from_markdown(help_page_name)

    html_page_master_layout= get_master_layout(include_read_only_toggle=False, include_title='Help', include_user_options=False)
    html_page_master_layout.body.append(html_for_help_text)

    return html_page_master_layout.as_html()


import markdown
documentation_directory = "docs"

def get_help_text_as_html_from_markdown(help_page_name: str) -> str:
    helper_file_name = dict_of_helper_functions.get(help_page_name, None)
    if helper_file_name is None:
        return 'Cannot find help file reference for %s' % help_page_name

    ## IMPORTANT: In the unlikely event we move the config file, this needs changing
    full_helper_file_with_path = get_relative_pathname_from_list(
        [documentation_directory, helper_file_name]
    )

    try:
        with open(full_helper_file_with_path, "r", encoding="utf-8") as input_file:
            text = input_file.read()
    except FileNotFoundError:
        return 'Cannot open help file %s' % full_helper_file_with_path

    try:
        html = markdown.markdown(text)
    except Exception as e:
        return 'Error %s when processing markdown help file %s' % full_helper_file_with_path

    return html

dict_of_helper_functions = {
    'events_volunteer_rota': 'volunteer_rota_help.md'
}



