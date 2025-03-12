Skipperman will attempt to identify all the sailors at an event in imported registration data. If the cadet isn't *identical* to one that is already in the data (EXACTLY the same name, and date of birth), then Skipperman will ask you to add the cadet to it's data. You will see a screen like this:

[TOC]

# Importing registration data

***
***
![add_select_cadet.png](/static/add_select_cadet.png)
***
***

The data about the cadet pulled in from the registration data is displayed. The date of birth will default to 1st January 1970 if this information is missing from the registration data (which is usual for racing events). The membership status will show as 'unconfirmed member'.
You will then see some warnings about the cadet: if the name shown appears too short, the date of birth does not look correct (i.e. the sailor is of cadet age)

Finally, you will see some option buttons.

## If this is not a new cadet

You will probably see a warning saying that the Cadet is very similar to an existing cadet. At the bottom of the page you will see buttons with existing cadet(s) on them. Click to choose the cadet you want. If you can't see the cadet you want, click on 'See all cadets'. You can also go back to just seeing the most similar cadets by clicking 'See similar cadets only'.

## If this is actually a new cadet

 **It's really important that you don't add duplicate cadets to the Skipperman data**

But if you are sure this is a new cadet: check the name and date of birth (making any corrections in the relevant input fields), and membership status. 

Date of birth: For racing events you won't usually have the date of birth. If they are a visitor don't worry about including this, leave it on the default date. If they are a member that is new to Skipperman, and you aren't sure of their date of birth or it hasn't been included in the registration form, then you can [edit the date of birth later](view_and_edit_individual_cadet_help.md). 

For membership status:

- if you are sure they are a paid up member, select 'Member'
- if you are sure they are a non member (visitor), select 'None member'
- if you aren't sure, select 'Unconfirmed member'

Membership or otherwise can be confirmed by [importing a list of club members](import_membership_list_help). 

Remember it is possible to edit the cadet details, and these can also be updated by importing a list of club members from Wild Apricot, so don't worry too much if these aren't precisely right.

## If this is a test entry

Sometimes when testing the registration system (eg Wild Apricot) it's useful to create test entries, which don't have real cadets (of course you can also use real cadets but this can cause confusion). If this is a test entry, click on "Skip: this is a test entry" button. 

# Duplicate registrations

After identifying each cadet, Skipperman will add the registration data for each sailor in the event. You might get this error:

```
ACTION REQUIRED: Cadet John Smith appears more than once in WA file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!
```

As it says, this means the cadet has been registered multiple times, but the duplicate registrations have not been cancelled. Any registrations found in the file after the first one that is loaded in will be ignored.

To avoid this, strongly discourage parents from re-registering cadets if they have made a mistake (something they are typically going to do because Wild Apricot doesn't allow you to edit a registration, with good reason). Instead:

- if the change will modify the amount to be paid (eg number of days attending), make the change yourself in Wild Apricot
- if the change won't affect payment, make the change in Skipperman itself.


# Updating registration data

If you subsequently reimport an updated registration file, you may need to identify any cadets with new registrations, but any existing registrations with identified sailors will be remembered.

