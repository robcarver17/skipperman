**To access the field mapping menu: Main menu/Events/Select Event/Import registration data/Import from WA/Check or modify WA mapping**

Mapping converts Wild Apricot form entry names to our internal field names - we can't import an event without it.

[TOC]

# What is mapping?

Skipperman needs to identify certain pieces of information in imported registration data, and does so by labelling them with fixed field names, eg 'Cadet first name'. However, when Wild Apricot exports data, it labels information with the text given on the registration form for the event. And it's possible to use any text on the form that you like: for example 'First name', 'First Name', 'Forename', 'Cadet first name'... Skipperman can't just guess what has been used on the form.

The mapping for an event is basically a list of fields in the Wild Apricot export file, and what they correspond to in Skipperman. Without this list, there is no way for Skipperman to import the data from Wild Apricot.

# Recommended mapping process

This assumes you have [created the event in Skipperman](add_event_help.md), but done no other activities yet.

If you get lost, to return to the mapping menu page is: Main menu/Events/Select Event/Import registration data/Import from WA/Check or modify WA mapping.

- [Create your event in Wild Apricot](WildApricothelp#creating-a-duplicated-event) by duplicating an existing event that is as similar as possible, and is already in Skipperman.
- From the mapping menu, select ['Clone the mapping for an existing event'](WA_clone_mapping_help) and choose the existing event that you duplicated.
- The mapping menu page will now display a table of 'Wild Apricot' names that need to be in the Wild Apricot form and their corresponding Skipperman fields.
- **Do not change anything in the Wild Apricot form that will be used by Skipperman**. You can change other parts of the form, or add new entries. 
- Do a test registration or two in Wild Apricot to populate the data and to make sure you are happy with the form / event. Don't forget to [mark the entries as test](link_required) in Skipperman when they are imported, and cancel them in WA afterwards.  
- [Export registration data from Wild Apricot to a .csv file](WildApricothelp#downloading-the-registration-file-for-skipperman-upload)
- [Upload the WA export file into Skipperman](link_required) and then go to the mapping menu
- There should be no issues raised by the [mapping diagnostics](#mapping-diagnostics), and you can proceed to opening up the event for registration on WA
- **Once you have imported data from WA into Skipperman it is strongly advised not to change the WA form or the Skipperman/WA mapping as this will cause serious problems.**

See [other ways to do the mapping](#other-ways-to-do-the-mapping).


# The mapping menu

The mapping menu has the following options (as well as the usual, back and help buttons):

- [**Clone** the mapping for an existing event](WA_clone_mapping_help.md). This is the easiest way to do mapping: if you create an event in Wild Apricot by duplicating a past event and make no changes to the form then you can just clone the mapping for that past event.
- Use [**template** mapping](WA_template_mapping_help.md). Templates are mapping for 'typical' events; cadet week, training and racing weekends. They aren't guaranteed to work, but can be a good starting point to see what Skipperman fields you are likely to need.
- [**Create** your own mapping file](WA_create_your_own_mapping_help.md). This is advanced stuff!

Below the mapping menu is the [mapping table](#the-mapping-table), and the [mapping diagnostics](#mapping-diagnostics).

# The mapping table

Once mapping has been set up, it is displayed as a table under the mapping menu. You can also make changes to the mapping here. Only do this if you are sure of what you are doing! - **Once you have imported data from WA into Skipperman it is strongly advised not to the Skipperman/WA mapping as this will cause serious problems.**

## Adding a new mapping

If you want to add a new mapping, click on the dropdown 'Choose skipperman field to add to mapping', and then click on the button 'Add selected skipperman field to mapping'.

The button will then be replaced with either:

- If you have uploaded a WA file of registrations, a list of the WA files
- or if there is no file uploaded, you can just type the WA field name. **Warning: Make sure you type it exactly. I strongly recommend that you create a test registration, export the WA event file, and then import it before modifying the mapping**.

If you have put the wrong skipperman field, you can also change it now. Then click 'Add selected skipperman & WA field to mapping' to add the mapping. If you don't select a skipperman and WA field, then it will cancel the addition of the new mapping. 

## Deleting an existing mapping

You can't add mapping for skipperman and WA fields that are already being used elsewhere; to change these first delete the mapping. You may also want to delete mappings where the names are misspelt (highlighted in the table).
Simply click on the delete button next to an existing mapping to remove it. This will free up the relevant Skipperman and WA fields to use in a new mapping.

# Mapping diagnostics

There are four types of mapping diagnostics. The following will appear once mapping has been set up:

- Skipperman fields in the mapping file that are misspelt
- Fields from Skipperman that are missing from the mapping file

And these will appear once mapping is set up, and a Wild Apricot export file has been upload:

- Fields that are in the Wild Apricot export file, but not in the mapping file
- Wild Apricot fields that are in the mapping file, but missing from the Wild Apricot file

## Skipperman fields in the mapping file that are misspelt

Headed with: "Following skipperman internal fields defined in mapping file are unknown to skipperman - will not be used - correct typos in the mapping file:"

These will also be highlighted in the [mapping table](#the-mapping-table).

This is problematic - if you don't fix it then the relevant fields will be ignored by Skipperman - and it's most likely cause is that you have manually created a mapping file and there are some typos. See the [mapping guide for experts](link_required) for a list of skipperman field names.
You should delete them from the [mapping table](#the-mapping-table), and add with the correct names.

## Fields from Skipperman that are missing from the mapping file

Headed with "Following internal skipperman fields are not defined in mapping file, might be OK depending on event type but check:"

This is quite normal, because:

- Sometimes we can get the same information in different ways, so there are multiple Skipperman fields that mean the same thing
- Not all events have all types of data, eg only Cadet Week needs food information

Read the notes next to each missing field to see if you need to take action, and add them as new fields in the [mapping table](#the-mapping-table).

## Fields that are in the Wild Apricot export file, but not in the mapping file

Headed with "Following fields are in WA file but will not be imported, probably OK"

This is quite normal, there is a lot of junk in the WA export files, plus there may be information from the form that Skipperman doesn't need.
Of course, it might be that you need to add or make changes to the [mapping table](#the-mapping-table) to include this new field.

## Wild Apricot fields that are in the mapping file, but missing from the Wild Apricot file

Headed with "Following expected fields in the mapping file are missing from WA file; remove from the mapping file if not needed"

These will also be highlighted in the [mapping table](#the-mapping-table).

The most likely cause of this is that you have cloned an existing mapping and changed the WA form without changing the mapping; or created your own mapping file and made a typo. Delete the mapping from the mapping table and add the correct value.

# Other ways to do the mapping

These all assume you have [created the event in Skipperman](add_event_help.md), but done no other activities yet.

If you get lost, to return to the mapping menu page is: Main menu/Events/Select Event/Import registration data/Import from WA/Check or modify WA mapping.

## Recommended (repeated from earlier)

- [Create your event in Wild Apricot](WildApricothelp#creating-a-duplicated-event) by duplicating an existing event that is as similar as possible, and is already in Skipperman.
- From the mapping menu, select ['Clone the mapping for an existing event'](WA_clone_mapping_help) and choose the existing event that you duplicated.
- The mapping menu page will now display the [mapping table](#the-mapping-table) of 'Wild Apricot' names that need to be in the Wild Apricot form and their corresponding Skipperman fields.
- **Do not change anything in the Wild Apricot form that will be used by Skipperman**. You can change other parts of the form, or add new entries. 
- Do a test registration or two in Wild Apricot to populate the data and to make sure you are happy with the form / event. Don't forget to [mark the entries as test](link_required) in Skipperman when they are imported, and cancel them in WA afterwards.  
- [Export registration data from Wild Apricot to a .csv file](WildApricothelp#downloading-the-registration-file-for-skipperman-upload)
- [Upload the WA export file into Skipperman](link_required) and then go to the mapping menu
- There should be no issues raised by the [mapping diagnostics](#mapping-diagnostics), and you can proceed to opening up the event for registration on WA
- **Once you have imported data from WA into Skipperman it is strongly advised not to change the WA form or the Skipperman/WA mapping as this will cause serious problems.**

## If short of time and feeling confident

- [Create your event in Wild Apricot](WildApricothelp#creating-a-duplicated-event) by duplicating an existing event that is as similar as possible, and is already in Skipperman.
- From the mapping menu, select ['Clone the mapping for an existing event'](WA_clone_mapping_help) and choose the existing event that you duplicated.
- The mapping menu page will now display the [mapping table](#the-mapping-table) of 'Wild Apricot' names that need to be in the Wild Apricot form and their corresponding Skipperman fields.
- **Do not change anything in the Wild Apricot form that will be used by Skipperman**. You can change other parts of the form, or add new entries. 
- Open up the event for registration in WA
- Once some registrations have happened, [export registration data from Wild Apricot to a .csv file](WildApricothelp#downloading-the-registration-file-for-skipperman-upload), and [upload the WA export file into Skipperman](link_required)
- On the mapping menu page there should be no significant issues raised by the  [mapping diagnostics](#mapping-diagnostics) - if there are you have a problem! Serves you right for being cocky!

## If you need to make small changes to the WA event form

- [Create your event in Wild Apricot](WildApricothelp#creating-a-duplicated-event) by duplicating an existing event that is as similar as possible, and is already in Skipperman.
- From the mapping menu, select ['Clone the mapping for an existing event'](WA_clone_mapping_help) and choose the existing event that you duplicated.
- The mapping menu page will now display  the [mapping table](#the-mapping-table) of 'Wild Apricot' names that need to be in the Wild Apricot form and their corresponding Skipperman fields.
- Make required changes to the form in Wild Apricot, then make a note of them. 
- Do a test registration or two in Wild Apricot to populate the data and to make sure you are happy with the form / event. Don't forget to [mark the entries as test](link_required) in Skipperman when they are imported, and cancel them in WA afterwards.  
- [Export registration data from Wild Apricot to a .csv file](WildApricothelp#downloading-the-registration-file-for-skipperman-upload)
- [Upload the WA export file into Skipperman](link_required) and then go to the mapping menu
- From the main mapping menu page, [make any required changes to the mapping in the mapping table](#the-mapping-table). See [the list of WA fields](List_and_explanation_of_skipperman_fields)
- Check the [mapping diagnostics](#mapping-diagnostics) to check there is nothing significant missing
- When you are happy with everything, you can open the event up for registration in Wild Apricot
- **Once you have imported data from WA into Skipperman it is strongly advised not to change the WA form or the Skipperman/WA mapping as this will cause serious problems.**

## Advanced

Only do this if you have read and thoroughly understood [the list of WA fields](List_and_explanation_of_skipperman_fields)!

- Create your event in Wild Apricot ideally by [duplicating an existing event](WildApricothelp#creating-a-duplicated-event) that is as similar as possible, and is already in Skipperman. If you choose not to, it will require more work.
- If you make changes to the WA form of an existing event, then make a note of them. 
- Do a test registration or two to populate the data in Wild Apricot  
- [Export registration data from Wild Apricot to a .csv file](WildApricothelp#downloading-the-registration-file-for-skipperman-upload)
- [Upload the WA export file into Skipperman](link_required) and then go to the mapping menu
- If you have an advanced understanding of the mapping then you can use [cloning](WA_clone_mapping_help), but also [template mapping](WA_template_mapping_help), or [create your own mapping](WA_create_your_own_mapping_help). See the [mapping menu](#the-mapping-menu) for more information.
- From the main mapping menu page, [make any required changes to the mapping in the mapping table](#the-mapping-table)
- Check the  [mapping diagnostics](#mapping-diagnostics) to check there is nothing significant missing
- When you are happy with everything, you can open the event up for registration in Wild Apricot
- **Once you have imported data from WA into Skipperman it is strongly advised not to change the WA form or the Skipperman/WA mapping as this will cause serious problems.**

