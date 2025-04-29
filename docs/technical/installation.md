Most users won't need to install Skipperman, they can just access it from [the website: https://bsccadetskipper.pythonanywhere.com](https://bsccadetskipper.pythonanywhere.com/)

# Installation - local

Once all installed you can run a local instance with (assuming a Linux command line): 

```
cd skipperman
export FLASK_APP=flask_app.py
flask run
```

Then go to `http://127.0.0.1:5000/` on your chrome browser and you should see the skipperman home page.

# Installation and updating code - existing cloud provider

Log into https://www.pythonanywhere.com/user/bsccadetskipper/

Select consoles in the menu. Launch / open a bash console

```
cd skipperman
git pull
```

Select 'Web' in the menu. Click on 'reload' and 'run until 3 months from now'

Navigate to `https://bsccadetskipper.pythonanywhere.com/`


# Usernames and log in fresh install

The username and login for Skipperman is specific to each installation, will not be affected by data download/upload, and will be set up from scratch on a fresh install. On a fresh install with no users setup the default username / password is `default` and `default`. [**Add a new user or change the password immediately**](/docs/list_of_users_help.md)


►
▼
`