# SKIPPERMAN - Blackwater Sailing Club Cadet Skipper Managemet System


SKIPPERMAN will be a piece of software to ease the admin burden on the cadet skipper and their team, which is considerable and involves lots of manual hacking of spreadsheets. 


NOTE: This is not a proper readme.md, rather a series of notes.



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


## Components

- Data pipeline
- Interface (consisting of display and interactive input, plus reporting output). CLI and GUI will be provided.
- Driver, with hooks to the data pipeline and interface, which allows you to 'run' skipperman.
- Back end functions called by the driver.


## Features

### Minimum viable product:

- maintain a master list of cadets and events
- import a list of entries for a specific event from WA
- allocate cadets to groups 
- print a report of which cadet is in which group


### Basic:

- create a volunteer rota, manage it, and report on it
- maintain ticksheets, print and record ticks
- print roll call lists and contact details
- allocate resources such as club dinghies and safety boats
- import a set of members from WA to populate a list of cadets or volunteers
- allocate and maintain colour groups (CW)
- print spotter sheets (CW and racing events)
- maintain and report on tickets for gala dinner (CW)
- maintain and report on wristbands (CW)
- create a report of cadets and their ages for fancy dress (CW)
- create a report of cadets 
- create a report of t-shirts and other merch required (CW)
- create a report of polo shirts required (CW)
- create a report of RYA logbooks/certficates required (CW)


### Future / wishlist / nice to have:

- maintain lists of past, present and future cadet committee members
- create a list of key volunteers to invite to curry evening
- instructor facing interface to update ticks on a GUI
- instructor facing interface for roll call
- create a report of birthdays during an event
- maintain a list of key volunteers and thank yous (CW)
- manage orders for hoodies (CW)


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



