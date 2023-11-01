## my functions for easy construction of html

class Html(str):
    def prefix_with(self, prefix: 'Html'):
        return Html(prefix+self)

    def suffix_with(self, suffix: 'Html'):
        return Html(self+suffix)

class ListOfHtml(list):

    def join_as_paragraphs(self):
        self_as_paragraphs = ListOfHtml([html_paragraph_line_wrapper.wrap_around(html) for html in self])
        return self_as_paragraphs.join()

    def join_as_lines(self):
        self_as_lines = ListOfHtml([html_line_wrapper.wrap_around(html) for html in self])
        return self_as_lines.join()

    def join(self):
        return Html("".join(self))


class HtmlWrapper(Html):
    ## must contain single %s
    def wrap_around(self, other_html: Html) -> Html:
        return Html(self % other_html)

empty_html = Html("")
html_unordered_list_wrapper= HtmlWrapper("<ul>%s</ul>")
html_list_item_wrapper= HtmlWrapper("<li>%s</li>")
html_bold_wrapper = HtmlWrapper("<b>%s</b>")

def html_bold(some_text:str):
    return html_bold_wrapper.wrap_around(Html(some_text))

## FIX ME COULD DO COLOURS OR SIZE OR SOMETHING - CSS
def html_error(error_str):
    return Html(error_str)

def html_link(string: str, url: str):
    return Html('<a href="%s">%s</a>' % (url, string))

def html_link_in_list_item(string: str, url: str):
    return html_list_item_wrapper.wrap_around(html_link(string=string, url=url))

def html_link_with_nested_list(string: str, url: str, nested_list_to_wrap: Html):
    html_for_link = html_link(string=string, url=url)
    nested_list_html = html_unordered_list_wrapper.wrap_around(nested_list_to_wrap)
    html_link_and_nested_link = ListOfHtml([html_for_link, nested_list_html]).join()

    return html_list_item_wrapper.wrap_around(html_link_and_nested_link)

menu_layout_html_wrapper=HtmlWrapper(
    '''
      <div class="container">
        <strong><nav>
          <ul class="menu">
          %s
          </ul>
        </nav></strong>
      </div>
''')

html_paragraph_line_wrapper = HtmlWrapper('<p>%s</p>')

html_line_wrapper = HtmlWrapper('%s<br />')
