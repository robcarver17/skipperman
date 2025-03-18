
You may want to manually add sailors to an event who:

- haven't been officially registered. This is very useful for racing events, when you want to produce an accurate spotter sheet.
- who you know *will* be registered but haven't yet been
- or you know *has* been registered, but you don't want go through the hassle of [importing data from Wild Apricot](import_registration_data_help.md) 

This can be done from the [**registration editing**](registration_editing_help.md) or [**group allocation**](group_allocation_help.md) pages.
___

# If the sailor is already in Skipperman

Type the sailors first and last name into the relevant boxes. Then click on `Please check the details...`. A list of sailors with similar names should come up on the screen. If you can't see the sailor, then click on `Choose from all existing cadets`. You can sort the full list of sailors in a few different ways. 

Once the relevant sailor is on the screen, click on the button with their name and date of birth.

# If the sailor is new to Skipperman

 **It's really important that you don't add duplicate cadets to the Skipperman data**

But if you are sure this is a new cadet: enter their name and date of birth (making any corrections in the relevant input fields), and membership status. 

Date of birth: You won't usually have the date of birth for a new sailor, unless they have done a WA registration already. If they are a visitor don't worry about including this, leave it on the default date. If they are a member that is new to Skipperman, and you aren't sure of their date of birth or it hasn't been included in the registration form, then you can [edit the date of birth later](view_and_edit_individual_cadet_help.md). 

For membership status:

- if you are sure they are a paid up member, select `Member`
- if you are sure they are a non-member (visitor), select `None member`
- if you aren't sure, select `Unconfirmed member`

Membership or otherwise can be confirmed by [importing a list of club members](import_membership_list_help). 

Remember it is possible to edit the cadet details, and these can also be updated by importing a list of club members from Wild Apricot, so don't worry too much if these aren't precisely right.

Once you are confident then click on `Please check the details again for me` (if it's on screen), and then on `Yes - these details are correct - add this new cadet`.

# Effects of adding a sailor manually

Note that adding a sailor manually will set their registration status to 'Manual'. Since there is no registration information, all the registration fields will be blank. 

If the sailor is subsequently registered on Wild Apricot, and the data imported, you will get an error message: 

> `ACTION REQUIRED: Cadet John Smith (2000-01-01) Member appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!`

You have two options:

- Change the original manual registration to `Cancelled` in Skipperman. Then you can re-import the Wild Apricot file with the new registration. This has the disadvantage that you will lose any changes / additional information added in Skipperman. 
- Ignore the error. This has the disadvantage that you will need to manually update the original manual registration with any relevant information from Wild Apricot.

NOTE: In a future version of Skipperman the system will allow you to replace the manual registration with an official one automatically.
