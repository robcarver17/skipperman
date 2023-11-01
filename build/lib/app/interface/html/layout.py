from app.interface.html.html import Html, HtmlWrapper

## applies to all pages
## FIXME: Does CSS even work?
master_layout_html = HtmlWrapper(
    '''
<!DOCTYPE html>
<html>
  <head>
    <title>Skipperman</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
  </head>
  <body>
    <header>
      <div class="container">
        <h1 class="logo">Skipperman: BSC Cadet Skipper Management System</h1>
      </div>
    </header>
    %s
  </body>
</html>
''')


## FIXME could be a nice button
go_home_html = Html('''
      <div class="container">
        <strong><nav>
          <ul class="menu">
          <a href="/">CANCEL: Back to home menu</a>\n
          </ul>
        </nav></strong>
      </div>
''')