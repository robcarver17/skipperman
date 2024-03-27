# SKIPPERMAN - Blackwater Sailing Club Cadet Skipper Managemet System


SKIPPERMAN will be a piece of software to ease the admin burden on the cadet skipper and their team, which is considerable and involves lots of manual hacking of spreadsheets. 



## Abbreviations

WA - Wild Apricot, the BSC club management system
CW - cadet week

## Where does the name come from

Since we have ‘Dutyman (BSC Duty Management system), I thought a good name for this would be ‘Skipperman (BSC Cadet Skipper Management System)’. Obviously a certain lycra orange bodysuit costume was also inspirational here.

## Overall requirements, architecture and design decisions


### Data storage
 This will be in .csv files. We do not require concurrent access or speed; and this will mean that the underlying data is both human readable, can be hacked in excel, or imported into a future replacement product. It also means that full or partial sets of data can easily be shared by sending files, without requiring a central server; there will be no need for users to eg launch a database server. We won't use eg sqllite to maintain data consistency, but will enforce the use of common keys across tables eg for Cadets.

Generally each .csv table will have a minimum amount of information in (eg we wouldn't have one giant cadet data table), but there would be the option to create consolidated .csv with information from several tables as a report.

### Language
The back-end, and as much as possible of the front-end, will be in Python. Partly this is because Python is a full stack capable language, but also because the principal developer has mostly forgotten the other 50 or so languages he used to know.

### Useability and interface

Skipperman needs to be useable by non-technical people. Hence, Skipperman will have two interfaces; a CLI interface that will be used to ensure that back end development can occur concurrently with front end and so that the current cadet skipper can get immediate value from the product, and a GUI for non technical users. 

A key design decision is how the GUI is implemented and deployed; a web front end seems the most logical solution, but should this be local or cloud hosted?

Skipperman also needs to be flexible enough so that it can cope with eg changes in WA event fields without rewriting code.



## Features

### Done:

- maintain a master list of cadets and events
- import a list of entries for a specific event from WA
- allocate cadets to groups 
- print a report of which cadet is in which group
- view / delete cadets
- edit / delete events
- view / edit /add volunteers 
- allocate volunteers to a rota
- allocate safety boats
- copy roles between volunteers on volunteer rota
- allow list of boats/dinghies/etc to be reordered
- import a set of members from WA to populate a list of cadets
- report on a volunteer rota
- reports can now be sent to .xls/.csv files
- spotter sheets report
- report to public weblink is optional and puts report in different place
- filter volunteer sheets on qualification
- regular backups on all writes; include roll back function (showing user who did edits) UTILITIES MENU


### Required for racing event:
  
- basic level of niceness
- double check write on save behaviour
- full test of everything
- change password / forgot password (needs email, link users to specific volunteer name)

### Required for social event:

- think carefully about how to handle events with no cadets, volunteers etc
- two types of food event: as part of training event, or social only seperate
- manage social event with food only (Social)


### Required for training event (ASAP):

- record qualification data and backfill
- backfill Cadet week data
- maintain ticksheets, print and record ticks
- backfill ticksheet data
- add * for boat allocation to group report
- filter volunteer sheet on available days
- allow selection of group subset in reporting arrangement
- print roll call lists and contact details
- registration report with literally everything
- birthdays during an event - splash on event screen

### Required for training event (Can wait):

- GDPR document
- instructor login (send link to create)
- ticksheet level security
- refactor reporting so uses common data model
- key report links for instructors on landing page
- handle waiting lists (new state)
- clear old reports for event (remove rednedant permalinks) and other temp directories UTILITIES MENU


### Required for cadet week:


- two types of clothing event: as part of training event, or social only seperate
- allocate and maintain colour groups (CW)
- maintain and report on tickets for gala dinner, include additional gala dinner invites eg sponsors, plus ones (CW)
- maintain and report on wristbands (CW)
- create a report of cadets and their ages for fancy dress (CW)
- create a report of t-shirts and other merch required (CW)
- create a report of polo shirts required (CW)
- create a report of RYA logbooks/certficates required (CW)
- maintain a list of key volunteers and thank yous (CW)
- manage orders for hoodies (CW)
- maintain lists of past, present, potential and future cadet committee members (CW)
  

  ### General required before handover to Jonny:

- don't allow duplicate templates and delete templates allowed
- template for import of list of cadets
- edit event (warnings especially days!)
- anything that is displayed on screen can be exported to .csv eg reg details, volunteer rota (and imported...???)
- upload/download all data as zip
- clean up eg old data, uploaded files, staged files
- move all dangerous deletes to special area: , delete event (many warnings!), delete cadet, delete volunteer
- editable user sailing groups, volunteer roles, skills
- create a list of key volunteers to invite to curry evening
- create a report of cadets
- dropdown list of previous event names
- clear description of field names

### Future / wishlist / nice to have:

- nicer CSS
- instructor facing interface to update ticks on a GUI
- instructor facing interface for roll call


## Business objects

- Cadets
- Volunteers
- People
- Events
- Ticksheet
- Boats


## Tables

- Cadets
- Event configuration
- Tick sheets
- Cadets at Events
- Volunteers at events (rotas)


## Security and GDPR

'Real' underyling data won't be available to the development team so a set of fake data will be created for testing purposes.

## Random thoughts


Whilst merging in lists of potential new cadets or volunteers, need to avoid accidental duplicates use [fuzzy](https://github.com/seatgeek/thefuzz) or similar.

## A few questions - Sam
### Q:How is data storage going to work? Are we going to do cloud storage? Otherwise we would have a different copy for each user that then would need merging.

A: Mostly this is single user, but the main exception would be the volunteer rotas where the skipper and deputy will work on these in colloboration so there might be a case for having a merge feature for this specific use case.

That does not preclude cloud storage, which may make sense depending on how the application is ultimatly deployed.

### I think we could probably find a good python library so we wouldn't need a web interface. Either that or there exist plenty of good libraries in other languages (I have experience with .NET MAUI for example, which is cross platform).

-Sam

