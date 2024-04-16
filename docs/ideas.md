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
- regular backups; include roll back function 
- record qualification data 
- record ticksheet data
- print roll call lists

### Bug fixes before next event import

- removing volunteer should also remove associated role ID
- cope with volunteer that already exists if manually added
- remove 'smart' volunteer finding when no first or surname found
- issues with duplicates on registration - fix when writing data model
- random issues with volunteer changes, fix when writing data model
- ignore cadet name on import (use for test cadets - need to be able to avoid on reimport as we do for volunteers)
- refactor reporting so uses common data model
- change event upload so doesn't store old files
- seperate health field which gets reported to instructors (seperate out different types of notes)
- waiting list - change unallocated status name


### Required for training event (Can wait):

- add health to ticksheets
- add contact details and health to roll call report
- multiple filter: filter volunteer sheet on available days (only volunteers available on a given day), only volunteers available and unallocated on a given day, only volunteers with certain skills
- store of previous events volunteer role / cadet allocation to speed up loading 
- click on cadet name to see previous groups
- click on volunteer name to see previous events
- allow selection of group subset in reporting when doing arrangement of groups
- print ticksheets from menu
- record ticksheet entries
- registration report with literally everything on it
- birthdays during an event - splash on event screen
- GDPR document
- instructor login (send link to create)
- ticksheet level security
- key report links for instructors on landing page
- clear old reports for event (remove rednedant permalinks) and other temp directories UTILITIES MENU
- set maximum allowable / target for each role
- put shareable files up like instructors documents; manage shared files eg deleete
- power boat only volunteer rota

### Required for social event:

- think carefully about how to handle events with no cadets, volunteers etc
- two types of food event: as part of training event, or social only seperate
- manage social event with food only (Social)


### Required for cadet week:

- list of non volunteers with cadet ages, previous groups
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
- template download for import of list of cadets
- edit event (warnings especially days!)
- anything that is displayed on screen can be exported to .csv eg reg details, volunteer rota (and imported...???)
- upload/download all data as zip
- clean up eg old data, uploaded files, staged files
- move all dangerous deletes to special admin area: , delete event (should never have to do this: many warnings!), delete cadet, delete volunteer
- merge cadet / merge volunteer
- editable user sailing groups, volunteer roles, skills
- create a list of key volunteers to invite to curry evening
- create a report of cadets
- dropdown list of previous event names
- clear description of field names
- instructions

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

