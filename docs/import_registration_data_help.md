To import the registration data for an event, from the **main menu** choose **events**, then select the event, then click on **import registration data**.
___

[TOC]


# Introduction

As people can't register for events using Skipperman, and currently use the sailing club's 'Wild Apricot' system, we have to import registration data from there.

Once imported, any new registrations can then be reflected in the Skipperman data by reimporting an updated file.

This is a quick guide to importing data - more detailed help is available at each stage.

# Setting up wild Apricot events 

When setting up a Wild Apricot event it is *strongly recommended* that you use the 'copy previous event' function and make *no* changes to the registration form.

***
***
![wa_duplicate_event.png](/static/wa_duplicate_event.png)
***
***

If you do feel you have to make changes to the form, then you will need to understand how [**field mapping**](WA_field_mapping_help.md) works.

# Exporting registration data from Wild Apricot

It's strongly recommended that you create at least one test registration in Wild Apricot at this stage before exporting the data.

To export registration data from WA, click on the `Export registrants` button, select `Export to: CSV`, make sure `Export all fields` is ticked, and click `Export` (it's more reliable to export a .csv file, but Skipperman can also handle .xlsx spreadsheet files if you prefer to use those).

***
***
![WA_export_registrations.png](/static/WA_export_registrations.png)
***
***

# Importing data into Skipperman

First [add the event in Skipperman](add_event_help.md) in Skipperman.
Now select `Main menu / Events/ Event name / Import registration data / Import from WA spreadsheet file` to get ready to import.

If it's a brand-new event, you should see the following status update:

> `Status`:  
> `No field mapping set up - do this before you import any data`  
> `No WA file has ever been uploaded before (or WA ID has been manually cleared).`  
> `No registration data imported yet.`  
> `No file currently uploaded for import.`  


## Field mapping

More [information on field mapping here](WA_field_mapping_help.md).

'Fields' are the labels given to different types of information in Skipperman, like the first and surname of a cadet. 'Field mapping' is the process of going from the data as it comes out of Wild Apricot, and transforming it into labelled fields that Skipperman would recognise. 

Let's assume that you duplicated an existing Cadet event in Wild Apricot without making any changes, and that it's an event which already exists in Skipperman. If not, then you will need to read the [detailed help on field mapping](WA_field_mapping_help).

Assuming you're already in `Main menu / Events/ Event name / Import registration data / Import from WA spreadsheet file`, now click on `Set up WA field mapping`. Then in the following menu, choose `Clone the mapping for an existing event`. Then choose the event you want to clone. You will now see the message `Mapping copied from event June training 2023 to New event name and year`.  
After pressing `Finished`, you will see the message `Mapping already set up for TestEvent 2025`. Click on `Back` and you are now at the main import page. The status will have changed to:


> `Field mapping has been setup.`  
> `No WA file has ever been uploaded before (or WA ID has been manually cleared).`  
> `No registration data imported yet.`  
> `No file currently uploaded for import.`  


## Uploading a WA export file

You are now ready for the next step - uploading the WA file you exported earlier. Click on the `Upload a WA export file`, `Choose file`, and then `Upload selected file`. If all goes well, you will see the message `Uploaded file successfully`. The status in the import page will now read:

> `Field mapping has been setup.`  
> `A WA file with WA ID 5271589 has been previously uploaded.`  
> `No registration data imported yet.`  
> `WA file has been uploaded ready for import`  



The WA ID is a number given by WA to each event, which Skipperman found in the file and is now using to identify the event (obviously your WA ID will be something quite different!). And you can also see that we have uploaded a file which is ready for the next stage, importing.

### Duplicate WA ID

If you try and upload a file with a WA ID that has already been assigned to an existing event, you will get an error like this:


> `Problem with file upload Can't upload file for TestEvent 2025, WA ID 5271589 in file is already mapped to a different existing event June training 2023 - are you sure you have the right file?. If you are sure, then clear the WA ID for June training 2023 before retrying.`  

This is to prevent users from accidentally uploading the wrong downloaded event file.

The main reason, apart from testing, that this could happen is if you set up an event twice for some reason; and then get as far as importing data on one event, and then try to do it on the second event. Ideally, you shouldn't do this! But if you do then you will have to eithier:

- go back to using the original event that was set up (and ignore the new one)
- Or, if you want to use the new event instead of the old one, then follow the instructions in the error message, navigate to the original event, then choose `Import registration data`, `Import from Wild Apricot`, and then click on `Reset the stored WA event ID` 

The latter will not delete or modify the old event in any way, but it will allow you to upload a file with the duplicate WA ID into a different event.


## Importing from the WA import file

You should now be back at the main WA import page. Click on 'Import data from uploaded WA file'.  The import will go through a series of steps to get all the data from the file into Skipperman. These stages are:

- Importing all the cadets attending
- Importing all the volunteers who are helping
- Where relevant; importing any clothing size data (only for events with merchandise)
- Where relevant; importing any food requirements (only for catered events)

## Importing all the cadets attending

Skipperman will attempt to identify all the cadets in the imported WA event file. If a cadet is identical to one that is already in the data (EXACTLY the same name, and date of birth) it will be added silently. If a cadet entry is very close, but not identical. In this case the cadet will be added to the data, but you will see a warning like this:

```
Found cadet John Doe (2001-10-01) Member, looks a very close match for Jon Doe (2001-01-10) Unconfirmed member in registration data. If not correct, replace in edit registration page.
```

If the cadet isn't identical or very similar, then Skipperman will ask you to add the cadet to it's data. You will see a screen like this:

***
***
![add_select_cadet.png](/static/add_select_cadet.png)
***
***

- If this isn't actually a new cadet: you will probably see buttons to select an existing cadet. Click on the appropriate cadet. If you can't see the cadet you want, click on `See all cadets`. **It's really important that you don't add duplicate cadets to the Skipperman data**
- If this is a new cadet: check the name and date of birth, and membership status. For racing events you won't usually have the date of birth - if they are a visitor don't worry about including this. If they are a member that is new to Skipperman, you can [edit the date of birth later](view_and_edit_individual_cadet_help.md). For membership status unless you are sure they are (or are not) a member, put 'unconfirmed'. Membership can be confirmed by [importing a list of club members exported from WA](import_membership_list_help)). It is possible to edit the cadet details, and these can also be updated by importing a list of club members from Wild Apricot, so don't worry too much if these aren't precisely right.  
- If this is a test entry and not a real cadet: click the "Skip permanently: this is a test entry" button. 
- If you aren't sure and what to come back to this cadet on the next import, click "Skip for now"


More help with identifying cadets [here](identify_cadets_at_event_help.md)

## Adding cadet registration data

Next Skipperman will add the registration data for each sailor in the event. A quick guide to likely errors, [more detailed advice here](identify_cadets_at_event_help.md):

```
ACTION REQUIRED: Cadet John Smith appears more than once in WA file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!
```

This means the cadet has been registered multiple times, but the duplicate registrations have not been cancelled. Any registrations found in the file after the first one that is loaded in will be ignored.  If you allow a duplicate registration to occur, the best thing to do is to cancel the duplicated registrations in Wild Apricot and then re-import the data. Make sure that the details in the remaining registration on Skipperman reflect what the parent actually wants to do.

```
Cadet Jon Doe was added manually - is still not appearing in official registration import
```

This is fine for a racing event, but for training events where payment and agreement to terms and conditions is required, get the sailor to register and then export the data from WA and update in Skipperman.

You can see all the registration warnings for import on the [edit registration page](registration_editing_help.md#warnings) and there is advice here on [resolving warnings](resolve_warnings.md).

## Importing all the volunteers attending

Next, Skipperman will try and find the volunteers who have mentioned in the WA event file. 

If a volunteer has an identical name to one in the data, they will be added automatically.

If their name is similar, but no identical, they will be added with a warning:

```
Volunteer Jane Doe is very similar to one in form Janet Doe, adding automatically. Go to rota to change if problematic."
```

If a volunteer isn't very similar to one in the data, then Skipperman will give you the option of adding them as a new volunteer, or selecting an existing volunteer. You will see a screen like this:

***
***
![add_select_volunteer.png](/static/add_select_volunteer.png)
***
***


- If this isn't actually a new volunteer: you will probably see buttons to select an existing volunteer. Click on the appropriate volunteer. If you can't se the volunteer you want, click on `See all volunteers`. **It's really important that you don't add duplicate volunteers to the Skipperman data**
- If this is a new volunteer: check the first and second name are correct, then click `Add this new volunteer`.   
- If this isn't really a volunteer: click on `Skip permanently`. The most common cause of this is where the parent has accidentally put the cadets name in instead of their own. The system warns against this. 
- If you aren't sure and want to add the volunteer on a subsequent import, click `Skip for now`.

Important - if a 'volunteer' is actually a parent who can't help but will be on site, you should add them. You can then change their availability in the [rota page](volunteer_rota_help.md).

More help with identifying volunteers [here](identify_volunteers_at_event_help.md). 

## Conflicts between volunteer and cadet information

The next step is to check that the information that has been registered is internally consistent. Skipperman will check:

- that the volunteer availability is consistent across registrations (eg if they are associated with more than one cadet)
- that the information the volunteer has put down about their duty preference is consistent over multiple registrations
- that the volunteer is attending on days when none of their sailors is not attending (note we don't check to see if the reverse is true - eg a volunteer not coming for all the days their sailor is attending)

Any warnings generated in this process will appear [on the volunteer rota page, under warnings](volunteer_rota_help.md#warnings).

For more information, see [resolving warnings](resolve_warnings.md).

# Checking warnings

To check and resolve any outstanding issues raised in the event import, go to the [volunteer rota](volunteer_rota_help.md#warnings) and the [cadet registration edit page](registration_editing_help.md#warnings).

For more information, see [resolving warnings](resolve_warnings.md).

# Updating an event

Once you have imported a registration file, you have the option of re-importing an updated version.

You won't normally upload a registration file from WA to Skipperman just once. There will often be additional registrations, or last minute cancellations.

There will also potentially be changes to the registration information in Wild Apricot. It is **strongly advised** to only make changes in Wild Apricot that affect the amount that needs to be paid:

- the number of training days attended, 
- or any cancellation to an existing registration.
- or a reversal of a cancellation.

**Any other changes you make won't be reflected in Skipperman**. Instead, make the changes directly in Skipperman. This is to avoid the hassle of having to make multiple download and uploads of files. It also means that non Wild Apricot literate users of Skipperman can make their own updates.

You can also, if you prefer, make any of the changes above in Skipperman from the [registration page](registration_editing_help.md) to avoid the need to download and upload a new data file. If you make the changes only in Skipperman, and not in Wild Apricot, then a new invoice will not be generated. This might be preferable, if for example someone is still doing the same number of training days, but is doing Saturday only instead of Sunday. Or if someone has cancelled but with short notice and/or without a good reason, in which case you might not want to give them a refund.

## Uploading an updated event file

Before uploading, the status should show:

> `Field mapping has been setup.`  
> `A WA file with WA ID 5271589 has been previously uploaded.`  
> `Registration data has been imported already, but can be updated from a new file.`  
> `WA file has been uploaded ready for import` 

Note that the 'ready for import' message is still there, because the original WA file will stay on the system. This is in case we want to go back to skipped cadets and volunteers.

Click on `Upload a new WA export file`, choose the file and click upload. Then click on `Update data from current WA file` to update the registation data. 

## New registrations

Any new sailors that have not been registered before will be added to Skipperman automatically. You may need to [identify the sailors involved](identify_cadets_at_event_help.md), as you did with the first data import.


## Conflicts between existing and new registration information

You can see a list of cadets with import errors in the [registration editing, warnings section](registration_editing_help.md#warnings). 

[More about resolving warnings](resolve_warnings.md)

### More than one active registration in the new file for a given sailor 

```
ACTION REQUIRED: Cadet John Smith (2000-01-01) Member appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!
```

As it says, this means the cadet has been registered multiple times, but the duplicate registrations have not been cancelled. Any changes made to these registrations will be ignored. If you allow a duplicate registration to occur, the best thing to do is to cancel the duplicated registrations in Wild Apricot and then re-import the data. Make sure that the details in the remaining registration on Skipperman reflect what the parent actually wants to do.


### Missing sailor in registration file

```
Cadet John Smith (2000-01-01) Member was in imported data, now appears to be missing in latest file - possible data corruption of imported file or manual hacking - no changes in file will be reflected in Skipperman
```

This can happen if:

- For some stupid reason you have manually edited the data file exported from Wild Apricot and remove one or more rows. Unless you're an expert trying to debug something, don't do this. Instead, change the registration status to ['Cancelled' in the registration editing screen](registration_editing_help.md). Meanwhile, you can ignore this error.
- Wild Apricot themselves have changed their export output, or Skipperman has managed to corrupt it's own data. Please contact support - this is serious.



```
Cadet John Smith (2000-01-01) (2006-02-08) Member was added manually - is still not appearing in official registration import.
```

This happens if you manually add a sailor to Skipperman, but they haven't yet been registered and imported from WA. That is fine for eg racing events where no payment is required or formal confirmation of registration, in which case you can ignore.

Otherwise to clear, get the sailor registered on WA and then import into Skipperman.


### Status and availability changes

The **status** of a registration can be eithier active (eg paid, unpaid, partially paid) or inactive (eg cancelled). 

If the **status** of the registration changes, or the days a sailor can attend change, you will get a warning and a form to confirm any changes.

You have three options:

- Use the original data in Skipperman (which ignores any updates made in Wild Apricot)
- Use the data in the form. You can select a different status and/or available days. If you don't make any changes in the form, choosing this button will be the same as using the new data from Wild Apricot.
- Use the new data imported from Wild Apricot (recommended)

If a sailor was originally registered manually, then all their registration data will be imported. Warning - you won't see any notes they have entered unless you look at the registration details page.

## New conflicts between volunteer and cadet information

If you change the dates a specific cadet is available for, or cancel a cadets registration, it could have an impact on the volunteers they are connected to.

Check the [warnings on the volunteer rota page](volunteer_rota_help.md#warnings) to double-check that there is no inconsistency between when volunteers and attending, and when sailors are around.

[More about resolving warnings](resolve_warnings.md)

