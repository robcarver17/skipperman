To refresh the Skipperman skills list from the official BSC qualifications list, go to the **main menu**, select **Volunteers**, and then click on **Refresh key skills from .csv file**.
---

The skills that each volunteer has are not automatically updated in Skipperman when volunteers get new qualifications, or if existing ones expire. To refresh the skills that volunteers have you can eithier [manually edit them](view_individual_volunteer_help.md), or import them from the 'official' BSC spreadsheet.

[TOC]

# Preparing the spreadsheet and uploading the downloaded file

From the official Google Docs version of the spreadsheet (the current link to which is shown on the import page), go to the first tab with the names of all the instructors on, and click 'Export to .csv'.

The import assumes that the column names have a particular format. This can be changed by modifying the [configuration](/docs/technical/configuration.md#import-skills-csv) file, which can only be done admin users with acces to the code. Any redundant columns can be ignored, so if the spreadsheet has the right columns it will work without further cleaning.

Choose the downloaded .csv file and click upload file.

# Identifying volunteers

For each row in the file, Skipperman will first try and match it to a known volunteer. If a volunteer isn't identical to one already in the data (same name), then Skipperman will give you the option of adding them as a new volunteer, or selecting an existing volunteer. 

**It's really important that you don't add duplicate volunteers to the Skipperman data**

- If this isn't actually a new volunteer: you will probably see buttons to select an existing volunteer. Click on the appropriate volunteer. If you can't see the volunteer you want, click on `See all volunteers`. You can sort the volunteers. 
- If this is a new volunteer: check the first and second name are correct, click on `I have double checked the volunteer details - allow me to add` then click `Add this new volunteer`.   
- If you don't want to process this row of the file: click on `Skip`. 


# Reconciling and editing skills

After the volunteer is identified, Skipperman will then check that the qualifications in the file match those in the existing Skipperman data. If they do, it will silently move on to the next volunteer. 

Otherwise, you will see a series of messages:

- The skill that is inconsistent, and an explanation of why the skill is or is not in the imported file
- The skills registered in the imported file, and the existing Skipperman data 
- Some explanatory notes

You will then be presented with a check box. This is autofilled with the **existing** Skipperman skills. 

- Hit save to keep those skills and move on to the next volunteer in the file
- Edit the skills to reflect those in the file and any notes, 
- Cancel will abandon the import. But any changes made so far will be kept.

Notes:

The imported file has some quirks to be aware of:

- Currently, the imported file does not contain PB2 information. We know that SI, DI and RCL2 will automatically have PB2, so if you are adding an instructor qualification make sure you check PB2 as well
- By convention, and SI is also a DI, but the imported file may not have DI as SI.
- DI or RCL2 who used to be AI will have an AI qualification in the file. You can ignore this or make the DI up to be AI as well, it will make no difference to Skipperman.
