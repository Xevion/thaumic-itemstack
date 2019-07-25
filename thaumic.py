import json, pprint, string, os, sys
from functools import partial

# PrettyPrinter setup
pp = pprint.PrettyPrinter()
print = pp.pprint


# Open the file and load
with open(os.path.join(sys.path[0], 'thaumicjei_itemstack_aspects.json'), 'r') as file:
    data = json.load(file)

with open(os.path.join(sys.path[0], 'aspect_tiers.json'), 'r') as file:
    tiers = json.load(file)

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

# Allows recursive. Sorts by the number of (different) aspects in the list.
# current=key list
# aspect=aspect dictionary
# reverse=reverses how the keys are changed in the key array
def sort_aspect_count(current, aspects, descending=False):
    coefficient = max(list(map(len, aspects))) # Maximum value in the list
    current = list(map(lambda x : x * (coefficient + 1), current)) # Multiply by coefficient + 1
    # Reversal is done just by counting down FROM the cofficient (maximum value)
    if descending:
        for index in range(len(aspects)):
            current[index] += coefficient - len(aspects[index].keys()) # Add value for the key
    # Regular
    elif not descending:
        for index in range(len(aspects)):
            current[index] += len(aspects[index].keys()) # Add value for the key
    return current

# For use in process_sorts(), returns a function where descending has been predetermined
sort_aspect_count_prepare = lambda desc : partial(sort_aspect_count, descending=desc)

# current=key list
# aspect=aspect dictionary
# target=if specified, only count of a target aspect is considered
def sort_aspect_sum(current, aspects, targets=None, descending=False):
    # Target is specified, have to account for the new maximum coefficient
    if targets:
        coefficient = 0
        for aspectDict in aspects:
            # Calculate which targets are in the aspectDict
            available = [target for target in targets if target in aspectDict.keys()]
            # If any are in it
            if len(available) > 0:
                # Calculate the sum of the target aspect's count's
                # length of available is taken into account, items with higher target counts are prioritized
                coefficient = max(coefficient, sum([aspectDict[target] for target in available]))
    # Target is not specified, get a blanket sum
    elif not targets:
        coefficient = max(list(map(sum, [x.values() for x in aspects])))
    # Multiply key list by coefficient
    current = list(map(lambda x : x * (coefficient + 1), current))
    # Target is specified
    if targets:
        # Descending: += (coefficient - value)
        # Ascending: += (value)
        if descending:
            for index in range(len(current)):
                # If the target aspect is actually in the dictionary
                # then add it's count as the key 'change'
                # edit: changed to allow for list of targets, using sum()
                available = [target for target in targets if target in aspects[index].keys()]
                if len(available) > 0:
                    current[index] += sum([aspects[index][target] for target in available])
        elif not descending:
            for index in range(len(current)):
                available = [target for target in targets if target in aspects[index].keys()]
                if len(available) > 0:
                    current[index] += coefficient - (sum([aspects[index][target] for target in available]))
    elif not targets:
        if descending:
            for index in range(len(current)):
                # Just add the sum instead
                current[index] += sum(aspects[index].values())
        elif not descending:
            for index in range(len(current)):
                current[index] += coefficient - sum(aspects[index].values())
    return current

# For use in process_sorts, returns a function where target and descending have been predetermined
sort_aspect_sum_target = lambda targs, desc=False : partial(sort_aspect_sum, targets=targs, descending=desc)

def sort_target_ratio(current, aspects, targets, descending=False):
    keylist = []
    for item in aspects:
        available = [aspect for aspect in item if aspect in targets]
        sum_target = sum([item[aspect] for aspect in available]) # Sum of target counts
        sum_non_target = sum(item.values()) - sum_target # Sum of non-target counts
        if sum_non_target == 0:
            ratio = sum_target
        else:
            ratio = sum_target / sum_non_target
        keylist.append(ratio)
    
    pIndex = [i for i in range(len(keylist))] # Create an index for every item in current to preserve order
    preSort = list(zip(pIndex, aspects, keylist))
    preSort.sort(key=lambda x : x[2])
    pIndex, aspects, keylist = dezip(preSort)

    # Multiply values to maintain coefficient
    coefficient = len(keylist)
    current = [value * (coefficient + 1) for value in current]

    # Add values to complete 'sorting'
    for index in range(len(keylist)):
        current[pIndex[index]] += coefficient - index
    return current

sort_target_ratio_prepare = lambda targs, descending=True : partial(sort_target_ratio, targets=targs, descending=descending)

# Processes a list of sort_functions against a list of names, aspects and a possible keylist
def process_sorts(sort_functions, names, aspects, keylist=None, reverse=True):
    if keylist == None:
        keylist = [1 for _ in range(len(names))]
    for sort_func in sort_functions:
        keylist = sort_func(keylist, aspects)
    zipped = list(zip(names, aspects, keylist))
    zipped.sort(key=lambda x : x[2], reverse=reverse)
    newNames, newAspects, newKeylist = dezip(zipped)
    return newNames, newAspects, newKeylist

# Filters for or against specific aspects
def filter_aspects(names, aspects, keylist, targets=[], doBlacklist=False):
    zipped = zip(names, aspects, keylist)
    if not doBlacklist:
        zipped = [item for item in zipped if all(target in item[1].keys() for target in targets)]
    elif doBlacklist:
        zipped = [item for item in zipped if not any(target in item[1].keys() for target in targets)]
    names, aspects, keylist = dezip(zipped)
    return names, aspects, keylist

# Quick function to eliminate the tri element unzipping process
def dezip(zipped):
    x, y, z = zip(*zipped)
    x, y, z = list(x), list(y), list(z)
    return x, y, z

# Filters for or against a specific mod or set of mods.
def filter_mods(names, aspects, keylist, targets=[], doBlacklist=False):
    zipped = zip(names, aspects, keylist)
    evaluate = lambda item, flip=False : flip ^ (item[0].split(':')[0] in targets)
    if doBlacklist:
        evaluate = partial(evaluate, flip=True)
    zipped = [item for item in zipped if evaluate(item)]
    names, aspects, keylist = dezip(zipped)
    return names, aspects, keylist

# Get the names, aspects and the keylist generated
names = build.keys()
aspects = [build[key]['aspects'] for key in build.keys()]
current = [1 for _ in range(len(names))]

whitelist = ['ordo']
blacklist = []
blacklistMods = ['botania', 'twilightforest']

# Mod Filtering
names, aspects, current = filter_mods(names, aspects, current, targets=blacklistMods, doBlacklist=True)
# Aspect Filtering, first
names, aspects, current = filter_aspects(names, aspects, current, targets=whitelist)
names, aspects, current = filter_aspects(names, aspects, current, targets=blacklist, doBlacklist=True)
# Sorting, aspect type count, aspect target sum
names, aspects, current = process_sorts([sort_target_ratio_prepare(whitelist, descending=True), sort_aspect_sum_target(targs=whitelist)], names, aspects, reverse=True)
print(list(zip(names, aspects)))