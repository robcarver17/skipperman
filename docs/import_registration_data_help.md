To import the registration data for an event, from the **main menu** choose **events**, then select the event, then click on **import registration data**.

[TOC]

# A quick guide to importing registration data (from Wild Apricot)

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

To export registration data from WA, click on the 'Export registrants' button, select 'Export to: CSV', make sure 'Export all fields' is ticked, and click Export (it's more reliable to export a .csv file, but Skipperman can also handle .xlsx spreadsheet files if you prefer to use those).

***
***
![WA_export_registrations.png](/static/WA_export_registrations.png)
***
***

# Importing data into Skipperman

First [add the event in Skipperman](add_event_help.md) in Skipperman.
Now select 'Main menu/Events/ Event name / Import registration data / Import from WA spreadsheet file' to get ready to import.

If it's a brand new event, you should see the following:

```
Status:
No field mapping set up - do this before you import any data
No WA file has ever been uploaded before (or WA ID has been manually cleared).
No registration data imported yet.
No file currently uploaded for import.
```

## Field mapping

More [information on field mapping here](WA_field_mapping_help.md).

'Fields' are the labels given to different types of information in Skipperman, like the first and surname of a cadet. 'Field mapping' is the process of going from the data as it comes out of Wild Apricot, and transforming it into labelled fields that Skipperman would recognise. 

Let's assume that you duplicated an existing Cadet event in Wild Apricot without making any changes, and that it's an event which already exists in Skipperman. If not, then you will need to read the [detailed help on field mapping](WA_field_mapping_help).

Assuming you're already in 'Main menu/Events/ Event name / Import registration data / Import from WA spreadsheet file', now click on 'Set up WA field mapping'. Then in the following menu, choose 'Clone the mapping for an existing event'. Then choose the event you want to clone. You will now see the message 'Mapping copied from event June training 2023 to **New event name and year**'.  
After pressing 'Finished', you will see the message 'Mapping already set up for TestEvent 2025'. Click on back and you are back at the main import page. The status will have changed to:


```
Status:
*Field mapping has been setup.*
No WA file has ever been uploaded before (or WA ID has been manually cleared).
No registration data imported yet.
No file currently uploaded for import.
```

## Uploading a WA export file

You are now ready for the next step - uploading the WA file you exported earlier. Click on the 'Upload a WA export file', 'Choose file', and then 'Upload selected file'. If all goes well, you will see the message 'Uploaded file successfully'. The status in the import page will now read:

```
Status:
Field mapping has been setup.
*A WA file with WA ID 5271589 has been previously uploaded.*
No registration data imported yet.
*WA file has been uploaded ready for import*
```

The WA ID is a number given by WA to each event, which Skipperman found in the file and is now using to identify the event. And you can also see that we have uploaded a file which is ready for the next stage,  importing.

## Importing from the WA import file

You should now be back at the main WA import page. Click on 'Import data from uploaded WA file'.  The import will go through a series of steps to get all the data from the file into Skipperman. These stages are:

- Importing all the cadets attending
- Importing all the volunteers who are helping
- Where relevant; importing any clothing size data (only for events with merchandise)
- Where relevant; importing any food requirements (only for catered events)

### Importing all the cadets attending

Skipperman will attempt to identify all the cadets in the imported WA event file. If the cadet isn't identical to one that is already in the data (EXACTLY the same name, and date of birth), then Skipperman will ask you to add the cadet to it's data. You will see a screen like this:

***
***
![add_select_cadet.png](/static/add_select_cadet.png)
***
***

- If this isn't actually a new cadet: you will probably see buttons to select an existing cadet. Click on the appropriate cadet. If you can't se the cadet you want, click on 'See all cadets'. **It's really important that you don't add duplicate cadets to the Skipperman data**
- If this is a new cadet: check the name and date of birth, and membership status. For racing events you won't usually have the date of birth - if they are a visitor don't worry about including this. If they are a member that is new to Skipperman, you can [edit the date of birth later](view_and_edit_individual_cadet_help.md). For membership status unless you are sure they are (or are not) a member, put 'unconfirmed'. Membership can be confirmed by importing a list of members exported from WA (Main menu/Sailors/ [import a list of club members](import_membership_list_help)). It is possible to edit the cadet details, and these can also be updated by importing a list of club members from Wild Apricot, so don't worry too much if these aren't precisely right.  
- If this is a test entry and not a real cadet: click the "Skip: this is a test entry" button. 

More help with identifying cadets [here](identify_cadets_at_event_help.md)

## Importing all the volunteers attending

Next, Skipperman will try and find the volunteers who have mentioned in the WA event file. If a volunteer isn't identical to one already in the data (same name), then Skipperman will give you the option of adding them as a new volunteer, or selecting an existing volunteer. You will see a screen like this:

***
***
![add_select_volunteer.png](/static/add_select_volunteer.png)
***
***

volunteer number

- If this isn't actually a new volunteer: you will probably see buttons to select an existing volunteer. Click on the appropriate volunteer. If you can't se the volunteer you want, click on 'See all volunteers'. **It's really important that you don't add duplicate volunteers to the Skipperman data**
- If this is a new volunteer: check the first and second name are correct, then click 'add this new volunteer'.   
- If this isn't really a volunteer: click on skip. The most common cause of this is where the parent has accidentally put the cadets name in instead of their own. The system warns against this. 


More help with identifying volunteers [here](identify_volunteers_at_event_help.md). 

## Conflicts between volunteer and cadet information

The next step is to check that the information that has been registered is internally consistent. Skipperman will check:

- that the volunteer availability is consistent across registrations (eg if they are associated with more than one cadet)
- that the information the volunteer has put down about their duty preference is consistent over multiple registrations
- that the volunteer is attending on days when none of their sailors is not attending (note we don't check to see if the reverse is true - eg a volunteer not coming for all the days their sailor is attending)




# Updating an event

```
Status:

```

