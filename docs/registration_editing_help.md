To access the page to edit and view registration details, from the **main menu** select **Events**, choose your event, and then click on **Edit sailors registration data**
___

[TOC]

# Overview of the registration page

The registration edit page consists of some sorting buttons, and then the table of sailors and their registration data.

# Overview of the sailors table

***
***
![edit_registration.png](/static/edit_registration.png)
***
***

The sailors table contains:

- The name of the sailor with their DOB and membership status
- The registration status (editable)
- Attendance fields (editable)
- Health and notes fields (editable)
- Other registration fields (you will need to scroll right to see them all) - some of which are editable

# Viewing and editing registration information

## Changing registration status

The **status** of a registration can be eithier active (eg paid, unpaid, partially paid), active manual, or inactive (eg cancelled). 

Manual registrations are made by [manually adding a sailor](manually_adding_a_sailor.md) or [a sailing partner](help_adding_partner.md). 

Normally the status of a registration will be automatically updated when new registration data is updated, however you may wish to make some changes without waiting for an update:

- An existing manual registration can be cancelled. See [here](manually_adding_a_sailor.md) for more help with manual registrations.
- A cancelled registration can be 'un-cancelled' by making it paid, partially paid or unpaid
- A paid, partially paid, or unpaid registration can be cancelled.

### If you cancel a registration

The sailor will become inactive and will be removed from any sailing groups, plus any partnerships will be broken up. As a result, you may get this error:

> `John Smith was sailing with partner Jane Doe, now they aren't sailing: Jane Doe has no partner on Wednesday`

Go to the [group allocation page](group_allocation_help.md) to add new partners. You may also get this error:

> `Following volunteers associated with cadet John Smith (2000-01-01) Member for whom status updated to deleted or cancelled - check their availability, and if no longer available update volunteer rota: John Smith Sr.`

You should go to the [volunteer rota](volunteer_rota_help.md) once you have clarified if the volunteer can still help. It may also be worth looking at the [rota warnings](volunteer_rota_help.md#warnings).



## Changing attendance

To change attendance, click the checkboxes next to each day and press save. If you remove availability on a day when someone has a sailing partner, you will get errors like:

> `John Smith was sailing with partner Jane Doe, now they aren't sailing: Jane Doe has no partner on Wednesday`

Go to the [group allocation page](group_allocation_help.md) to add new partners. You may also get this error:

> `Following volunteers associated with sailor John Smith for whom days attending updated - check they are still available for their nominated days, and if not update volunteer rota: John Smith Jr.`

You should go to the [volunteer rota](volunteer_rota_help.md) once you have clarified if the volunteer can still help on the relevant days. It may also be worth looking at the [rota warnings](volunteer_rota_help.md#warnings).


## Editing notes, health data, and emergency contacts

Some of the fields in the sailors table have edit boxes; make any changes you need and then hit save.

- Notes. Useful for notes about sailor, but not published. Appears on [group allocation page](group_allocation_help.md)
- Health. Appears on [tick sheets](ticksheets_help.md) and [roll call reports](roll_call_help.md). Populated from [Skipperman field](WA_field_mapping_help.md) 'Cadet health'.
- Responsible adult number. Appears on [roll call reports](roll_call_help.md). Populated from [Skipperman field](WA_field_mapping_help.md) 'Responsible adult number'.
- Responsible adult.  Appears on [roll call reports](roll_call_help.md). Populated from [Skipperman field](WA_field_mapping_help.md) 'Responsible adult'.

# Sorting the sailors table

If you want to see the sailors in a different order, click one of the sort buttons at the top of the table. Note any changes you make before pressing a sort button will be saved.

# Adding a sailor manually

You may also want to add sailors to an event who:

- haven't been officially registered. This is very useful for racing events, when you want to produce an accurate spotter sheet.
- who you know *will* be registered but haven't yet been
- or you know *has* been registered, but you don't want go through the hassle of [importing data from Wild Apricot](import_registration_data_help.md) 

Click on the `Add unregistered sailor` button at the bottom of the sailors table, and then eithier choose an existing sailor, or add a new one.  See [here for more help](manually_adding_a_sailor.md). Note that any changes you make before pressing the add button will be saved.

Note that adding a sailor manually will set their registration status to 'Manual'. Since there is no registration information, all the registration fields will be blank. 

If the sailor is subsequently registered on Wild Apricot, and the data imported, you will get an error message: 

> `ACTION REQUIRED: Cadet John Smith (2000-01-01) Member appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!`

You have two options:

- Change the original manual registration to `Cancelled` in Skipperman. Then you can re-import the Wild Apricot file with the new registration. This has the disadvantage that you will lose any changes / additional information added in Skipperman. 
- Ignore the error. This has the disadvantage that you will need to manually update the original manual registration with any relevant information from Wild Apricot.

NOTE: In a future version of Skipperman the system will allow you to replace the manual registration with an official one automatically.
