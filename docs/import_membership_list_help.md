To import a membership list, from the **main menu** choose **Sailors** and then click on **Import members from a spreadsheet file**.
___

It's useful to know if sailors (who can be member cadets, visiting sailors, or juniors racing in a cadet section run race series) are members or not. For example, only current members are eligible to be on the Cadet Committee. They may also have different fees to pay at racing events. Only members are eligble to take part in cadet training weekends. However Skipperman can't automatically know who is a member of the club. You have to export a membership file from the clubs membership database (currently WildApricot), and then import it here to align the two data sets.

[TOC]

# Different membership status

Sailors can have the following membership status:

- Member. Currently a member.
- Lapsed. This is a sailor that used to be a member,
- None member. Has never been a member.
- Unconfirmed member. Not sure if a member or not; typically used when a new sailor is registered for an event but we are unsure if they are a member or not.


# What happens we import a membership list

Here 'The system' refers to the Skipperman database.

*If a sailor is in the membership list, and an identical sailor is already in the system marked as a current member*
*OR if a sailor is in the system as a lapsed or none member, but doesn't appear in the imported membership list*

We don't have to do anything - the sailor has the correct membership status already.

*If a sailor is in the membership list, and an identical sailor is already in the system marked as an unconfirmed member*

This is likely to happen if a sailor was originally added to the system as part of an event but we didn't know if they were members or not. The sailor is marked in the system as a member.

*If a sailor is in the membership list, and an identical sailor is already in the system marked as a non-member

The sailor has joined the club. We mark them as current members.

*If a sailor is in the membership list, and an identical sailor is already in the system marked as a lapsed member*

Looks like the sailor has rejoined - we mark them as current members.

*If a sailor is in the system as a current member, but doesn't appear in the imported membership list*

This is likely to happen if a sailor doesn't renew their membership, or if the imported list only includes cadet members and the relevant sailor is 'aged out'. The sailor is marked as a lapsed member. Since aged out (junior) members don't do training weekends or cadet weeks, just racing events, this isn't a problem.

*If a sailor is in the system as an unconfirmed member, but doesn't appear in the imported membership list*

This is likely to happen if a sailor was originally added to the system as part of an event but we didn't know if they were members or not. The sailor is confirmed in the system as a none member.

*If a sailor is in the imported membership list, and there are no remotely similar sailors in the system*

This is likely to happen if a sailor has just joined, but hasn't yet done any events. The sailor is added to the system as a new sailor, and marked as a member.

*If a sailor is in the imported membership list, and there broadly similar (but not identical) sailors in the system already*

You will be asked to confirm eithier:

- Which of the similar sailors in the system the imported list is referring to. This happens when the membership list and the database have different names, or dates or birth.  
- To add a new sailor if this is definitely not one of the existing sailors.  

## If it's an existing member

Click on the name of the existing member. You will see one or more warnings:

### Existing member with a different name

> `Uploaded membership list has name John Smith, existing Skipperman data has name Jonny Smith - not changing; but consider if Skipperman is correct (fine if a nickname)`

This could be fine - the precise name sailors prefer to be known by might be different to the official name in the membership list. 

But please encourage parents to use the name in Skipperman when registering and to be consistent, otherwise you will have to keep manually confirming the sailor when importing event data.

Of course if it's a genuine error in the Skipperman data then you should fix it by [editing the sailor](view_and_edit_individual_cadet_help.md).

### Existing member with a default date of birth

> `Existing skipperman data has no date of birth for Jane Smith, updating to DOB in membership file of 2008-01-01`

If we add a sailor to Skipperman in a racing event, then there is no date of birth available. If we then get a date of birth from the membership list, we can update Skipperman accordingly.


### Existing member with a different date of birth

> `Discrepancy in dates of birth for Robert Torrance between Skipperman data 2007-02-02 and DOB in membership file 2007-02-03 - find out what is correct and edit Skipperman if required`

This is more serious - it's important that the date of birth is accurate or you will keep having to manually identify the cadet every time there is an event import. 

Eithier the official membership list is wrong (it does happen) - in which case get it corrected. Or the initial addition of the sailor to Skipperman was done with the wrong date of birth: then you should fix it in Skipperman by [editing the sailor](view_and_edit_individual_cadet_help.md).


## If you add a new sailor

Sailors can be added to the Skipperman database in one of three ways:

- on the [add sailor menu option](add_sailor_help.md)  
- when [processing the registrations for a training or racing event](import_registration_data_help.md)  
- if they appear as a new member when a membership list is imported, described here.  

It is *very* important that a sailor is not added twice! So the system goes to a lot of effort to make sure that you aren't duplicating an existing sailor. 


# What do I need to do to upload a new list

## Prepare the import file

Firstly, make sure you are not in [read only](main-menu.md#read-only) mode if you want to make changes - use read only mode for experimenting. Then download the file you want to import from the membership system (currently Wild Apricot). 

The membership file must be a csv or xls with following named columns: `First name`, `Last name`, `Date of Birth`. If the column names shown on the Skipperman web page are different from these, use those shown on the web page. Currently, if you export a list of members from Wild Apricot, it will include these fields. Any additional fields will be ignored, but if any of the expected columns are missing it will break.

## Upload the file

***
***
![import_members1.png](/static/import_members1.png)
***
***

Click on choose file, select the file you want to import from your computer (which will probably be in the Downloads directory), then click upload file.

## If required, select existing sailors or add new ones

If a sailor is in the imported membership list, and there similar (but not identical) sailors in the system already then you will need to clarify whether this is an existing member, or add them as a genuinely new member.

***
***
![import_cadets_select_cadet.png](/static/import_cadets_select_cadet.png)
***
***

Here you can see that in the membership list we have the first name shown as the full name plus an abbreviation (the surname and DOB have been covered for privacy reasons, but these match in both the import list and the system). Whereas in the system we have an existing member sailor whose name is just shown as 'Max'. Since it's quite likely they are the same person, to avoid creating a duplicate the system asks us to check.

We can eithier:

- Add a new sailor, or
- Select an existing sailor

### Adding a new sailor

If you think the imported sailor really is new, then click on 'please check the details'

***
***
![import_cadets_add_cadet.png](/static/import_cadets_add_cadet.png)
***
***

You have the option of editing the name and DOB of the sailor before adding if you think the import file is wrong, but this isn't recommended. If there is a difference between the Skipperman database and the membership database (currently Wild Apricot), you will have to reconcile them every time you import a membership list. Only change the DOB if the club membership database is wrong (and ask to get it corrected), and only change the name if the sailor would really prefer to be known by a different name eg a shortened version, or if as here the membership system has two names as here. 

Once you are happy click on `Yes - these details are correct - add this new cadet` 
 

### Select an existing sailor and confirm their membership

The sailors you can choose from have buttons. Initially this will only show sailors that are similar to the imported member.

You can either:

- Click on `Choose from all existing sailors` if you think this is an existing sailor, but not one of the ones with buttons to select from. You can then choose one of those sailors, or switch back to seeing just the similar sailors. You can also sort the list of sailors in various ways to try and find the sailor you want.
- Click on the button with the sailor name on. This will mark that sailor as a member and move on to the next option.

*Note the membership status of the sailors who were originally marked as members in the system is shown as TBC - whilst the import is happening we aren't sure if sailors are members or not.*

Unfortunately if there is a difference between the Skipperman database and the membership database (currently Wild Apricot), you will have to reconcile them every time you import a membership list. Since dates of birth should be identical in both places, this will only happen if the names are different. Sometimes there is a valid reason for the different names, but you may want to consider editing the sailor in Skipperman to match the membership system or you will have to keep reconciling them on every import.

## Read the log messages

Whilst the import is going on, if any members have their status changed (eg because they were lapsed or non members who have now joined, or were unconfirmed members, or were members who are now non-members) will be logged - read and be aware of these messages, and double check if something unexpected happens.

