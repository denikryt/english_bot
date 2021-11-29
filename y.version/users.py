import yaml
from path import CURR_DIR

LAST_MESSAGE = {}
WORKING_USERS = {}


with open('chat_id.yaml', 'r', encoding='utf-8') as f:
    try:
        CHAT_ID = yaml.load(f, Loader=yaml.FullLoader)['users']
    except TypeError:
        pass


for id in CHAT_ID.values():
    WORKING_USERS[id] = False
print(WORKING_USERS)



with open('bugs.yaml','r') as yamlfile:
    cur_yaml = yaml.safe_load(yamlfile) # Note the safe_load
    cur_yaml['bugs_tree'].update(d)

if cur_yaml:
    with open('bugs.yaml','w') as yamlfile:
        yaml.safe_dump(cur_yaml, yamlfile)







# class User():
#     _active = False
#     def __init__(self, name, id):
#         self.name = name
#         self.id = id 
    