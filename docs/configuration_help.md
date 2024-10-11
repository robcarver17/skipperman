The configuration pages allow you to modify various important lists used in Skipperman.

[TOC]

# General notes

Each list of items can be:

- reordered. Order matters; where lists are in drop downs you will see them in this order, and the order is also used for reporting (although this can be configured).
- have their name edited

You can also add a new item to the list. Some items are protected, they can't be modified (although they can be re-ordered).

In some cases it's also possible to:

- Hide an item from selection in a dropdown. This is useful as it's not possible to delete items in a list (this would corrupt data). So for example if a particular sailing group was only used for one event, you can hide it in future.
- Edit certain other attributes about items in a list; for example for sailing groups the location they sail in.
- Edit the underyling items in a specific category; for example the 'tick lists' for a qualification, or the members of a specific volunteer team

Some points about editing:

- The up and down buttons change the order, and they 'wrap around'; if you click up on the top item it will go to the bottom and vice versa.
- Changes to ordering (using the up and down buttons) happen immediately. Changes to the hidden attribute, name or other attributes will only happen if you click 'Save edits'
- If you click cancel any edits you have made will be discarded, but not changes to ordering.
- To add a new entry type a name in the relevant box, and then click 'Add'. If 
- Names in a list must be unique. If you try and change a name of an item to match another item, or add a new item with a duplicate name, an error will be reported.

# Club dinghies

These are the boats that cadets can borrow if they don't have their own. They can be hidden from view if a type of boat is no longer used. You don't need to list each boat individually; just the types of boat.

# Patrol boats

These are the safety boats used for rescuing. The ordering will be used when we allocate volunteers to boats, and in reports. It's recommended that you use the following order:

- Launch
- Club owned big RIBs
- Borrowed big RIBs
- River Jaffa, Dory
- Miniribs (Stealh first)
- Lake jaffas

Patrol boats can be hidden. This is useful if you borrow a boat for just one or a few events.

# Boat classes

These are the classes of boats that Cadets can sail. They can be hidden. You might want to add an 'exotic' boat sailed as a one off in a race series, and then hide it to reduce the clutter in the dropdown. I recommend you keep these in alphabetical order to make it easier to find a class in a dropdown.

# Volunteer skills

These are things volunteers can do or have certification for. Two skills are protected: PB2 and SI. These are used as an integral part of Skipperman. It isn't possible to hide skills as there shouldn't be that many available.

Skills can be required for a specific volunteer role, see below. Although you can reorder skills, it isn't important to do so.


# Volunteer roles

A volunteer role is something a volunteer can do at an event. As well as the name of the volunteer, and the ability to hide a role, you can set whether a particular role can be associated with a specific saiing group. This is the case for instructors and lake helpers. Note they don't have to be associated at a specific event, but it's an option. You can also set whether a volunteer role needs specific skills by ticking the checkboxes. A volunteer put in that role without those skills at an event will result in a warning.

The SI role is protected since it determines access to information at a specific event; as is the 'no role allocated' role. 

I recommend you stick to alphabetic ordering since that will make it easier to find them in a dropdown. The order isn't used for reporting purposes. Volunteers can be put into teams for reporting purposes and that is what determines the order; see the next section.

# Volunteer teams

A volunteer team is a group of people in a specific role.

As well as the name of the team, you can set a 'warn on location'. This is used to warn if people in a specific team are related to sailors who are in that location. Right now we only warn for lake helpers and lake safety. 

Teams can't be hidden; since they're used only for reporting a team will only be reported on if there are people from that team in the event.

The instructors team is protected since it's a core part of Skipperman.

## Edit individual roles in a team

If you click on the edit button at the end of a team row, you can re-order the roles in a team, or add new roles to a team. The first role mentioned in a team is the 'team leader', and the other roles will be in that order when we create a volunteer rota. 

It's fine for people to be in more than one team; for example the lake co-ordinator / deputy skipper is the lead of both the lake helpers and lake safety team. 

Note that you can't add entirely new roles, or change the names or other attributes of a role, you need to go the 'Volunteer roles' configuration page for that.


# Sailing groups

These are the training and racing groups that sailors can be in. As well as a name, each group has a location: Lake training, River training, MG. They can be hidden - this is very useful here as we often have 'one off' groups that are only used for certain events, and the dropdown options would be.

It's recommended that the order here is lake training, river training, MG groups; from beginners (Sprites), up to the most difficult MG group (General handicap). This will be the default for reporting.

# Sailing qualifications

These are the list of qualifications that cadets can achieve, both internal (eg lake badge) and RYA. [If you click on 'edit' you can change the underlying syllabus items ('ticks') for each qualification](edit_qualification_tick_help).

