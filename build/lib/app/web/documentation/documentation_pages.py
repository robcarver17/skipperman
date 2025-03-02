import os.path
import markdown

from app.data_access.init_directories import docs_directory
from app.web.html.html_components import (
    Html,
)
from app.web.html.master_layout import get_master_layout


def generate_help_page_html(help_page_name: str) -> Html:
    html_for_help_text = get_help_text_as_html_from_markdown(help_page_name)

    html_page_master_layout = get_master_layout(
        include_read_only_toggle=False, include_title="Help", include_user_options=False,
        include_backup_option=False,
        include_support_email=True
    )
    html_page_master_layout.body.append(html_for_help_text)

    return html_page_master_layout.as_html()



documentation_directory = "docs"
md = markdown.Markdown(extensions=["toc", "tables"])


def get_help_text_as_html_from_markdown(help_page_name: str) -> str:
    helper_file_name = "%s.md" % help_page_name
    if helper_file_name is None:
        return "Cannot find help file reference for %s" % help_page_name

    ## IMPORTANT: In the unlikely event we move the config file, this needs changing
    full_helper_file_with_path = os.path.join(docs_directory, helper_file_name)

    try:
        with open(full_helper_file_with_path, "r", encoding="utf-8") as input_file:
            text = input_file.read()
    except FileNotFoundError:
        return "Cannot open help file %s" % full_helper_file_with_path

    try:
        html = md.convert(text)
    except Exception as e:
        return (
            "Error %s when processing markdown help file %s"
            % full_helper_file_with_path
        )

    return html
