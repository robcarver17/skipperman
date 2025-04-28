To access and modify the list of users, from the **main menu** select **Administration** and then **Users, passwords and access**
___

Note: Only users in the admin group are permitted to access this information.

[TOC]

# New installation and storage

Usernames and hashed passwords are stored in `~/skipperman_user_data/secure/userlist.csv`

These are stored seperately from other Skipperman data and are not affected by backup operations. This means that with a new installation of Skipperman, there will be no users set up as there will be no user/password file present. A default user with admin rights (username: default, password: default) will be set up so you can log in. After logging in the first thing you should do is add yourself as an admin user, and delete the default (otherwise there will be a security risk). There must always be at least one admin user on Skipperman, the system will not let you delete or change the group if there is only one admin user. 


# Adding new users

To add a new user enter their username, password (twice), select an access group, and then from the dropdown choose the volunteer this user is associated with. If they aren't currently a volunteer, you will need to add them first. Finally click on `Add a new user`. The group chosen affects which main menu options are visible and accessible to a given user. The user groups are:

- Admin. Can see all menu options
- Skipper. Can see all menu options except `Administration`. Should be limited to Cadet Skipper and Deputy skipper(s).
- Instructor. Can see only `Instructors` menu. Instructors with the skill 'SI' can see additional options in that menu.
- Public. Cannot see any menu options.


# Modifying existing users

## Change password manually

To change a password just type the new password in both boxes next to the relevant user and click `Save edits` (**do not click the `Reset password to random value` button!**). Note that pressing `Add a new user` will also save changes to passwords.

## Reset password

If you want to reset a password to something random, click on `Reset password to random value`. You will see a message pop up which you can copy and paste to send to the user with their new login credentials.

## Change access group or associated volunteer

Choose the new group or volunteer from the dropdown and click `Save edits`. Note that pressing any `Reset password` button, or `Add a new user` will also save changes.

Note: A volunteer can be associated with more than one user. This can be useful if you want to set up a backup admin account.

Note: You can't change the access group if the relevant user is the only admin user.

## Delete a user

You can also delete a user by selecting the delete button next to their name. 

**Do not delete the account you are currently logged into - you will immediately lose access and unless you have another admin account you will be locked out**

You can't delete a user if they are the only admin user.

# ADVANCED: I am locked out of my admin account(s)

If you are locked out of your Skipperman admin account for some reason, and you only have one admin account or have forgotten the passwords to all of them, then assuming you have access to the cloud service running Skipperman, it's possible to recover it by:

- temporarily rename the username/password file (thus making it invisible to Skipperman): from the home directory `cd /skipperman_user_data/secure/; mv userlist.csv userlist_backup.csv` 
- delete the entire line in that renamed file starting with your username
- go to the Skipperman home page, and log in as the default admin user, username: default, password: default
- You will get the warning **USING DEFAULT ADMIN USER BECAUSE NO SECURITY FILE CREATED YET - ADD A PROPER ADMIN USER ASAP!! (Use Administration Menu)**
- Add yourself as a new admin user. This will create a new username/password file with the original name `/skipperman_user_data/secure/userlist.csv`
- The new file will have three users: look for the line starting with your username
- Copy that line from the new username/password file into the `/skipperman_user_data/secure/userlist_backup.csv` file. It doesn't matter where in the file it goes.
- Delete newly created password file, and rename the backup file back to it's original name `rm userlist.csv; mv userlist_backup.csv userlist.csv`
 
Note that you can't just edit the existing username file outright to reset your password, since passwords are stored as hashes. All this means you must never lose the credentials to the hosting site for Skipperman (currently pythonanywhere). It goes without saying you should be very careful with sharing the hosting credentials, since someone could use those to modify the password file, as well as steal data or malicously damage the code.
