from app.interface.html.layout import layout_html
from app.interface.menu_define import menu_definition

HOME = 'home'

### Returns HTML for a menu page
def menu_page_html(menu_option: str = HOME) -> str:
    html_code_for_menu = menu_html(menu_option)
    return layout_html(html_code_for_menu)

def menu_html(menu_option:str = HOME) -> str:
    inner_html_menu_code = menu_inner(menu_option)

    return menu_layout_html(inner_html_menu_code)

def menu_layout_html(menu_html_code: str) -> str:
    return '''
      <div class="container">
        <strong><nav>
          <ul class="menu">
          %s
          </ul>
        </nav></strong>
      </div>
    </div>
''' % menu_html_code


def menu_inner(menu_option:str) -> str:
    return parse_menu_option(menu_option, menu_definition)

LEVEL_SEPERATOR = "-"
def parse_menu_option(menu_option: str, current_menu_definition: dict,
                      breadcrumbs: str = "",
                      levels=0):

    ## it's a dict
    menu_option_as_list =menu_option.split(LEVEL_SEPERATOR)
    first_part_of_menu_option = menu_option_as_list[0]
    if levels==0:
        ## include home
        html_to_return = '<li><a href="/menu/%s">%s</a></li>\n' % (HOME, "Home")
    else:
        html_to_return = ""
    prepend_str = "- "*levels
    for name_of_option, contents_of_option in current_menu_definition.items():
        if type(contents_of_option) is str:
            ## return a non menu link
            full_name_of_option = prepend_str+name_of_option
            this_option = '<li><a href="/action/%s">%s</a></li>\n' % (contents_of_option,full_name_of_option)
        else:
            option_with_underscores = name_of_option.replace(" ", "_")
            link_this_menu = "/menu/%s" % breadcrumbs+option_with_underscores
            full_name_of_option = prepend_str+name_of_option
            this_option = '<li><a href="%s">%s</a></li>\n' % (link_this_menu, full_name_of_option)

            if first_part_of_menu_option==option_with_underscores:
                sub_menu_as_list = menu_option_as_list[1:]
                sub_menu_option = LEVEL_SEPERATOR.join(sub_menu_as_list)
                sub_menu = parse_menu_option(
                    menu_option=sub_menu_option,
                    current_menu_definition=current_menu_definition[name_of_option],
                    breadcrumbs=breadcrumbs+option_with_underscores+LEVEL_SEPERATOR,
                    levels=levels+1
                )
                this_option=this_option+sub_menu

        html_to_return = html_to_return + this_option

    return html_to_return
