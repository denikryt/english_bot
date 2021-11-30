import yaml
from path import directory


def open_yaml():
    file_name = 'users.yaml'
    with open(directory(file_name),'r', encoding='utf-8') as yamlfile:
        cur_yaml = yaml.safe_load(yamlfile)
    return cur_yaml

def write(user_name, user_id, message_id=None, target=str):
    file_name = 'users.yaml'
    # with open(directory(file_name),'r', encoding='utf-8') as yamlfile:
    #     cur_yaml = yaml.safe_load(yamlfile) # Note the safe_load
    cur_yaml = open_yaml()

    if target == 'new user':
        data = {
            user_name:{
                'id':user_id
            }
        }
        cur_yaml['users'].update(data)

    if target == 'last message':
        data = {'last message':message_id}
        cur_yaml['users'][user_name].update(data)

    if target == 'last notify':
        last_message = cur_yaml['users'][user_name]['last message']
        data = {'last message':last_message+1, 'last notify':last_message+1}
        cur_yaml['users'][user_name].update(data)

    if cur_yaml:
        with open(directory(file_name),'w', encoding='utf-8') as yamlfile:
            yaml.safe_dump(cur_yaml, yamlfile, allow_unicode=True)



# from path import CURR_DIR

# LAST_MESSAGE = {}
# WORKING_USERS = {}

# with open('chat_id.yaml', 'r', encoding='utf-8') as f:
#     try:
#         CHAT_ID = yaml.load(f, Loader=yaml.FullLoader)['users']
#     except TypeError:
#         pass


# for id in CHAT_ID.values():
#     WORKING_USERS[id] = False
# print(WORKING_USERS)











# class User():
#     _active = False
#     def __init__(self, name, id):
#         self.name = name
#         self.id = id 
    