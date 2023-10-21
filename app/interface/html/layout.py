
def layout_html(html_inside: str) -> str:
    return '''
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
''' % html_inside


go_home_html = '''
      <div class="container">
        <strong><nav>
          <ul class="menu">
          <li><a href="/">Back to menu</a></li>\n
          </ul>
        </nav></strong>
      </div>
'''