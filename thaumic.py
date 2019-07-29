import json, pprint, string, os, sys
from functools import partial

# PrettyPrinter setup
pp = pprint.PrettyPrinter()
print = pp.pprint


# Open the file and load
thuamicJSON = os.path.join(sys.path[0], 'thaumicjei_itemstack_aspects.json')
aspectJSON = os.path.join(sys.path[0], 'aspect_tiers.json')
data, tiers = json.load(open(thuamicJSON, 'r')), json.load(open(aspectJSON, 'r'))

# Dictionary object for keying items
#  build = {
#     'minecraft:grass' : {
#         'herba' : 2,
#         'terra' : 5
#     }
#  }

build = {}

# Convert a data structure into a suitable string for the dictionary to append
def convert(get):
    # Detect whether it's a ForgeCaps or it has a 'tag' entry in it (add support for tag decoding later)
    if 'ForgeCaps' in get or 'tag' in get:
        return None, None
    else:
        get = [str.strip() for str in get.split(',')]
        item = get[0][5:-1]
        count = get[1].strip(string.ascii_letters + string.punctuation)
        damage = get[2].strip(string.ascii_letters + string.punctuation)
        return '{}:{}'.format(item, damage), count

for aspect in range(len(data)):
    curAspect = data[aspect]['aspect']
    for item in range(len(data[aspect]['items'])):
        # Get the structure and ready it for conversion
        get = data[aspect]['items'][item]
        # Convert it into mod:item:damage and the count.
        key, value = convert(get)
        if key == None or value == None:
            continue
        # If the key (item name) has not been initialized before
        try:
            build[key]
        except:
            build[key] = {'aspects' : {}}
            build[key]['aspects'] = {}
        build[key]['aspects'][curAspect] = int(value)

# Get the names, aspects and the keylist generated
names = build.keys()
aspects = [build[key]['aspects'] for key in build.keys()]
current = [1 for _ in range(len(names))]

# Returns a ratio of the selected (whitelist) aspects compared to others.
# Reverse will make the whitelist into a blacklist.
def ratio_selected_to_others(item, whitelist, reverse=False):
    others = filter_count(item, whitelist)
    selected = sum(item[1]['aspects'].values()) - others
    if reverse: selected, others = others, selected
    return selected / max(1.0, others)

# Returns the count of the selected aspects for an item.
# Reverse will make the whitelist into a blacklist.
def filter_count(item, whitelist, reverse=False):
    if not reverse:
        return sum(item[1]['aspects'][subitem] for subitem in item[1]['aspects'].keys() if subitem in whitelist)
    elif reverse:
        return sum(item[1]['aspects'][subitem] for subitem in item[1]['aspects'].keys() if subitem not in whitelist)

# Returns True if the mod is in the whitelist.
# Reverse turns the whitelist into a blacklist.
def mod_filter(item, whitelist, reverse=False):
    mod = item[0].split(':')[0]
    value = mod in whitelist
    return not value if reverse else value

# Returns True if the item is in the whitelist.
# Reverse turns the whitelist into a blacklist
def item_filter(item, whitelist, reverse=False):
    item = item[0].split(':')[0]
    value = item in whitelist
    return not value if reverse else value

# Constants for sorting/filtering
# Empty blacklist/whitelist will do nothing. Both being non-empty may cause unintended behavior.
selected_aspects = ['terra']
whitelistItems = []
blacklistItems = []
whitelistMods = ['bloodmagic']
blacklistMods = []

# Filter the items
build_items = list(build.items())
# Blacklist Mods
if blacklistMods: build_items = list(filter(partial(mod_filter, whitelist=blacklistMods, reverse=True), build_items))
# Whitelist Mods
if whitelistMods: build_items = list(filter(partial(mod_filter, whitelist=whitelistMods, reverse=False), build_items))
# Blackist Items
if blacklistItems: build_items = list(filter(partial(item, whitelist=whitelistItems, reverse=True), build_items))
# # Whitelist Items
if whitelistItems: build_items = list(filter(partial(item_filter, whitelist=whitelistItems, reverse=False), build_items))
# build_items = list(filter)

# Builds the maps
map_selected_ratio = map(partial(ratio_selected_to_others, reverse=True, whitelist=selected_aspects), build_items)
map_selected_count = map(partial(filter_count, reverse=False, whitelist=selected_aspects), build_items)
# Zip the ratios and the items
zipped = list(zip(build_items, map_selected_ratio, map_selected_count))
# Sort the zipped item based on the maps zipped within
zipped.sort(key=lambda item : item[1:])
print(zipped[-100:])

# x = build_items[0]
# print(x)
# print(mod_filter(x, whitelist=['minecraft']))