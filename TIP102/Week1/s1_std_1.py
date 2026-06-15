from typing import List, Optional

def welcome():
    print("Welcome to The Hundred Acre Wood!")

welcome()

# ***************************************************************

def greeting(name: str):
    print(f'Welcome to The Hundred Acre Wood {name}! My name is Christopher Robin.')

greeting('Shubham')

# ***************************************************************

def print_catchphrase(character: str):
    if character == 'Pooh':
        print("Oh bother!")
    elif character == 'Tigger':
        print("TTFN: Ta-ta for now!")
    elif character == 'Eeyore':
        print("Thanks for noticing me.")
    elif character == 'Christopher Robin':
        print("Silly old bear.")
    else:
        print("Sorry! I don't know Piglet's catchphrase!")

character = "Pooh"
print_catchphrase(character)

character = "Piglet"
print_catchphrase(character)

# ***************************************************************

def get_item(items: List[str], x: int):
    if x <= len(items)-1:
        return items[x]
    else:
        return None

items = ["piglet", "pooh", "roo", "rabbit"]
x = 2
print(get_item(items, x))

items = ["piglet", "pooh", "roo", "rabbit"]
x = 5
print(get_item(items, x))

# ***************************************************************

def sum_honey(hunny_jars):
    res = 0
    for honey in hunny_jars:
        res += honey
    return res

hunny_jars = [2, 3, 4, 5]
print(sum_honey(hunny_jars))

hunny_jars = []
print(sum_honey(hunny_jars))

# ***************************************************************

def doubled(hunny_jars):
    res = []
    for honey in hunny_jars:
        res.append(honey*2)
    return res

hunny_jars = [1, 2, 3]
print(doubled(hunny_jars))

# ***************************************************************

def count_less_than(race_times: List[int], threshold: int):
    if len(race_times) == 0:
        return 0
    
    count = 0
    for time in race_times:
        if time < threshold:
            count += 1

    return count

race_times = [1, 2, 3, 4, 5, 6]
threshold = 4
print(count_less_than(race_times, threshold))

race_times = []
threshold = 4
print(count_less_than(race_times, threshold))

# ***************************************************************

def print_todo_list(task: List[str]):
    print("Pooh's To Dos:")
    for i, t in enumerate(task, start=1):
        if len(t) > 0:
            print(f'{i}. {t}')

task = ["Count all the bees in the hive", "Chase all the clouds from the sky", "Think", "Stoutness Exercises"]
print_todo_list(task)

task = []
print_todo_list(task)

# ***************************************************************

def can_pair(item_quantities: List[int]):
    if len(item_quantities) == 0:
        return True

    for item in item_quantities:
        if (item % 2) == 1:
            return False
    return True 

item_quantities = [2, 4, 6, 8]
print(can_pair(item_quantities))

item_quantities = [1, 2, 3, 4]
print(can_pair(item_quantities))

item_quantities = []
print(can_pair(item_quantities))

# ***************************************************************

def split_haycorns(quantity: int):
    res = []
    for i in range(1, quantity+1):
        if quantity % i == 0:
            res.append(i)

    return res

quantity = 6
print(split_haycorns(quantity))

quantity = 1
print(split_haycorns(quantity))

# ***************************************************************

def tiggerfy(s: str):
    exclude = ['t', 'i', 'g', 'e', 'r']
    res = []
    for c in s:
        if c.lower() not in exclude:
            res.append(c)

    return ''.join(res)

s = "suspicerous"
print(tiggerfy(s))

s = "Trigger"
print(tiggerfy(s))

s = "Hunny"
print(tiggerfy(s))

# ***************************************************************

def locate_thistles(items: List[str]):
    res = []
    for i, item in enumerate(items):
        if item == 'thistle':
            res.append(i)
    return res

items = ["thistle", "stick", "carrot", "thistle", "eeyore's tail"]
print(locate_thistles(items))

items = ["book", "bouncy ball", "leaf", "red balloon"]
print(locate_thistles(items))



