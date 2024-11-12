from app.data_access.data import *
from app.backend.volunteers.skills import get_list_of_skills
from app.backend.groups.list_of_groups import get_list_of_groups
from app.backend.volunteers.roles_and_teams import get_list_of_roles

import pandas as pd

list_of_skills = get_list_of_skills(object_store)
list_of_groups = get_list_of_groups(object_store)
list_of_roles = get_list_of_roles(object_store)

"""
vs = pd.read_csv('/home/rob/skipperman_data/lists/list_of_volunteers_skills.csv')

list_of_skills_ids =[]
for row in vs.iterrows():
    skill = row[1].skill
    skill_id = list_of_skills.matches_name(skill).id
    list_of_skills_ids.append(skill_id)

vs.skill = list_of_skills_ids
vs = vs.rename(columns={'skill': 'skill_id'})
vs.to_csv('/home/rob/skipperman_data/lists/list_of_volunteers_skills.csv', index=False)


for event_id in range(12):
    filename = "/home/rob/skipperman_data/mapped_events/cadets_with_groups_for_event_%s.csv" % str(event_id)

    try:
        df = pd.read_csv(filename)
    except:
        continue

    if len(df)==0:
        continue

    print(filename)
    list_of_group_ids = []
    for row in df.iterrows():
        group = list_of_groups.matches_name(group_name=row[1].group)
        list_of_group_ids.append(group.id)

    df.group = list_of_group_ids
    df = df.rename(columns = {'group': 'group_id'})
    df.to_csv(filename, index=False)



for event_id in range(12):
    filename = "/home/rob/skipperman_data/mapped_events/list_of_volunteer_role_targets_at_event_%s.csv" % str(event_id)

    try:
        df = pd.read_csv(filename)
    except:
        continue

    if len(df)==0:
        continue

    print(filename)
    list_of_role_ids = []

    for row in df.iterrows():
        role = list_of_roles.matches_name(role_name=row[1].role)
        list_of_role_ids.append(role.id)


    df.role = list_of_role_ids
    df = df.rename(columns = {'role': 'role_id'})
    df.to_csv(filename, index=False)

"""

for event_id in range(12)[8:]:
    filename = (
        "/home/rob/skipperman_data/mapped_events/list_of_volunteers_in_roles_at_event_%s.csv"
        % str(event_id)
    )

    try:
        df = pd.read_csv(filename)
    except:
        continue

    if len(df) == 0:
        continue

    print(filename)
    list_of_group_ids = []
    list_of_role_ids = []
    for row in df.iterrows():
        try:
            role = list_of_roles.matches_name(role_name=row[1].role)
        except:
            raise Exception(row[1].role)

        list_of_role_ids.append(role.id)
        group = list_of_groups.matches_name(group_name=row[1].group)
        list_of_group_ids.append(group.id)

    df.role = list_of_role_ids
    df.group = list_of_group_ids
    df = df.rename(columns={"group": "group_id"})
    df = df.rename(columns={"role": "role_id"})
    df.to_csv(filename, index=False)
