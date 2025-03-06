**To get to the template mapping page: Main menu/Events/Select event/Import registration data/Import from WA/Check of modify WA mapping/Create your own mapping file**

Custom mapping is useful for *advanced* users of Skipperman to create custom field mapping files. [More help on field mapping](WA_field_mapping_help.md).

**Warning: if you upload a new mapping file it will delete any existing field mapping. There will be no warning or confirmation!! Click Cancel if you are unusure.**

# Custom mapping files

It's normally best to work by adapting existing mapping from past events, or templates, by modifying the mapping in the [mapping table](WA_field_mapping_help.md#the-mapping-table). 

However, you may prefer to work directly with mapping *files*. A mapping file is just a .csv file with two columns, labelled as: 

- 'skipperman_field'
- 'wa_field'

Each row in the file consists of a mapping from Skipperman field to Wild Apricot field.

The workflow here is to download mapping files from various sources, edit them in a spreadsheet or text editor, and then upload the modified mapping file (eithier here as a custom mapping for a specific event, or as a new [mapping template](WA_template_mapping_help.md)).

# Create your own mapping menu options

From the 'create your own mapping menu' you can:

- Download a mapping file to edit: you can choose from a [template mapping](WA_template_mapping_help.md), mapping from a previous event FIXME, or if set up the field mapping for the current event.
- Upload a new mapping file - once you have finished editing the file locally. **Warning: if you upload a new mapping file it will delete any existing field mapping. There will be no warning or confirmation!!**. You may also want to use your file as a [template](WA_template_mapping_help.md).

You can also download information to help you with constructing your mapping file:

- Download a file of Skipperman fields to use in creating a mapping file. The file contains recommended fields for different types of event, as discussed [here](List_and_explanation_of_skipperman_fields.md). 
- (If you have already uploaded a WA export file to Skipperman) Download a file of WA field names used in the current uploaded file.  
