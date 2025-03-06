To access and modify the list of users, from the **main menu** select **Administration** and then **Users, passwords and access**

Note: Only admin users are permitted to access this information.

[TOC]

# New installation and storage

Usernames and hashed passwords are stored in `~/skipperman_user_data/secure/userlist.csv`

These are stored seperately from other Skipperman data and are not affected by backup operations. This means that with a new installation of Skipperman, there will be no users set up as there will be no user/password file present. A default user with admin rights (username: admin, password: admin) will be set up so you can log in. After logging in the first thing you should do is add yourself as an admin user, and delete the default (otherwise there will be a security risk). There must always be at least one admin user on Skipperman, the system will not let you delete or change the group if there is only one admin user. 


# Adding new users

To add a new user enter their username, password (twice), select an access group, and then from the dropdown choose the volunteer this user is associated with. If they aren't currently a volunteer, you will need to add them first. Finally click on 'Add a new user'. The group chosen affects which main menu options are visible and accessible to a given user. The user groups are:

- Admin. Can see all menu options
- Skipper. Can see all menu options except 'Administration'. Should be limited to Cadet Skipper and Deputy skipper(s).
- Instructor. Can see only 'Ticksheets and Qualifications' menu
- Public. Cannot see any menu options.


# Modifying existing users

## Change password manually

To change a password just type the new password in both boxes next to the relevant user and click 'Save edits' (do not click 'reset password' button!).

## Reset password

If you want to reset a password to something random, click on 'reset password'. You will see a message pop up which you can copy and paste to send to the user with their new login credentials.

## Change access group or associated volunteer

Choose the new group or volunteer from the dropdown and click 'Save edits'. 

Note: A volunteer can be associated with more than one user. This can be useful if you want to set up a backup admin account.

Note: You can't change the group if a user is the only admin user.

## Delete a user

You can also delete a user by selecting the delete button next to their name. 

Do not delete the account you are currently logged into - you will immediately lose access and unless you have another admin account you will be locked out.

You can't delete a user if they are the only admin user.

# I am locked out of my admin account(s)

If you are locked out of your Skipperman admin account for some reason, then it's possible to recover it by temporarily renaming the username/password file (thus making it invisible to Skipperman), logging in as the default admin user, and then adding yourself as a new admin user. You can then edit the username/password file to remove the original line with your username (you can't just edit the existing user outright to reset your password, since passwords are stored as hashes). All this means you must never lose the credentials to the hosting site for Skipperman (currently pythonanywhere). It goes without saying you should be very careful with sharing the hosting credentials, since someone could use those to modify the password file, steal data or malicously damage the code.
