When an event is being imported Skipperman will try and find the volunteers who have been mentioned in the imported registration data. 

- If a volunteer has an identical name to one in the data, they will be added automatically.
- If their name is very similar, but no identical, they will be added with a warning (assuming there is only one similar volunteer):

```
Volunteer Jane Doe is very similar to one in form Janet Doe, adding automatically. Go to rota to change if problematic."
```

To see a list of volunteers added in this way, go to the [volunteer rota warnings.](volunteer_rota_help.md#warnings)

- If a volunteer isn't identical to one already in the data (same name), then Skipperman will give you the option of adding them as a new volunteer, or selecting an existing volunteer. You will see a screen like this:

***
***
![add_select_volunteer.png](/static/add_select_volunteer.png)
***
***

The page tells you which sailor the volunteer was registered with. Since you can have multiple volunteers for a single sailor, we also show the 'volunteer number' (1, 2...). 

## This is not a new volunteer

If this isn't actually a new volunteer: you will probably see buttons to select an existing volunteer - Skipperman will show you the volunteers that have similar names. Click on the appropriate volunteer to identify them. If you can't see the volunteer you want, click on `See all volunteers`. You can sort the full list of volunteers a few different ways to try and find the person you want. You can go back to seeing just the most similar volunteers by clicking `See similar volunteers only`.

## This is a new volunteer

**It's really important that you don't add duplicate volunteers to the Skipperman data**

But if you are sure this is a new volunteer: check the first and second name are correct, then click `I have double checked the volunteers details entered - allow me to add`, and then `Yes - these details are correct - add this new volunteer`. 

## This isn't really a volunteer, or a non volunteering parent who will be on site

If this isn't really a volunteer: click on `Skip permanently - this isn't a volunteer or a parent on site`. The most common cause of this is where the parent has accidentally put the cadets name in instead of their own. The system warns against this. Another possibility is that it is a test registration with a made up name.


## I'm not sure

If you need to clarify who the volunteer is, click `Skip for now and import later`. You will see this volunteer again the next time you import from the same or an updated WA file.