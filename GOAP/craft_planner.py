import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from math import sqrt, inf, ceil
from heapq import heappush, heappop

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Returns a function to determine whether a state meets a rule's requirements.
    # This code runs once, when the rules are constructed before the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        if 'Requires' in rule:
            for name in rule['Requires']:
                if state[name] < 1:
                    return False

        if 'Consumes' in rule:
            for name, amount in rule['Consumes'].items():
                if state[name] < amount:
                    return False

        return True

    return check


def make_effector(rule):
    # Returns a function which transitions from state to new_state given the rule.
    # This code runs once, when the rules are constructed before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        next_state = state.copy()

        if 'Consumes' in rule:
            for name, amount in rule['Consumes'].items():
                next_state[name] -= amount

        for name, amount in rule['Produces'].items():
            next_state[name] += amount


        return next_state

    return effect


def make_goal_checker(goal):
    # Returns a function which checks if the state has met the goal criteria.
    # This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for name, amount in goal.items():
            if state[name] < amount:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)

"""
def make_heuristic(recipes, goal):
    # sees what goals need
    requires = []
    consumes = []
    c2 = {}
    r = {}
    c = {}
    actions = {}
    subSet = {'wood': {'plank': 4, 'stick': 8}, 'plank': {'stick': 2}}
    subSet2 = {'stick': {'plank': 2, 'wood': 8}, 'plank': {'wood': 4}}


    def requireOrConsume(goal):
        goal_name, goal_amount = goal
        for receipe_name, rule in recipes.items():
            if 'Requires' in rule:
                if goal_name in rule['Requires']:
                    requires.append(goal_name)
                    return
        consumes.append(goal_name)
        c2[goal_name] = goal_amount


    def rec(goal):
        for goal_name, goal_amount in goal.items():
            for receipe_name, rule in recipes.items():
                if goal_name in rule['Produces']:
                    p_amount = rule['Produces'][goal_name]
                    if 'Requires' in rule:
                        for name in rule['Requires']:
                            if name not in requires:
                                requires.append(name)
                                rec({name: 1})
                    if 'Consumes' in rule:
                        for name in rule['Consumes']:
                            if name not in consumes:
                                consumes.append(name)
                                rec({name: 1})


    def everyThingToDict():
        for item in requires:
            r[item] = {}
            for receipe_name, rule in recipes.items(): 
                if item in rule['Produces']:
                    if 'Consumes' in rule:
                        for name in rule['Consumes']:
                            #r[item].append({name: rule['Consumes'][name]})
                            r[item][name] = rule['Consumes'][name]
        for item in consumes:
            c[item] = {}
            for receipe_name, rule in recipes.items(): 
                if item in rule['Produces']:
                    if 'Consumes' in rule:
                        for name in rule['Consumes']:
                            #c[item].append({name: rule['Consumes'][name]})
                            c[item][name] = rule['Consumes'][name]


    def findSameActions():
        temp = []
        for receipe_name, rule in recipes.items():
            if list(rule['Produces'].keys())[0] not in actions:
                actions[list(rule['Produces'].keys())[0]] = {}
            if 'Requires' in rule:
                n = list(rule['Requires'].keys())[0]
            else:
                n = None
            actions[list(rule['Produces'].keys())[0]][n] = rule['Time']


        for action in actions:
            if len(list(actions[action].items())) == 1:
                #print (actions[action])
                temp.append(action)
                
        for t in temp:
            del actions[t]



    def heuristic(state, action):


        # if item is not needed
        if pName not in c and pName not in r:
            #print ("____1____")
            return inf
        # if already have that required item
        if pName in r and state[pName] > 1:
            #print ("____2____")
            return inf
        # if we need that item to satisfy goal do it
        if pName in c2 and state[pName] <= c2[pName]:
            #print ("____3____")
            return 0


        # if we have too much of a consumable
        if pName in c:
            #print ("pName: ", pName)
            for s in state:

                # if there is something in inventory that has not been created and is also a requirment
                if state[s] == 0 and s in r:

                    # if that item needs pName
                    if pName in r[s]:
                        #print ("\n", action, ", ", pName, ": (state: ", state[pName], ", should have: ", r[s][pName], " for ", s, ") \n")
                        if r[s][pName] >= state[pName] or pAmount > 1:
                            return 0

                    # if that item needs subset of pName
                    else:
                        # if the subset of pName exist
                        if pName in subSet:
                            for sub_pName in subSet[pName]:
                                #print ("asdfadsf", sub_pName, subSet[pName])
                                #print ("asdfasdfasDF", test)
                                if sub_pName in r[s]:
                                    #(stick)
                                    if state[sub_pName] < r[s][sub_pName]:
                                        #print ("i dont have ", sub_pName, state[sub_pName], " < ", r[s][sub_pName])
                                        flag = False
                                        for i in subSet2[sub_pName]:
                                            #print ("sadfasdf", i, subSet2[sub_pName][i])
                                            howMuchNeeded = r[s][sub_pName] - state[sub_pName]
                                           
                                            if i == pName:
                                                #print("asdfasdf")
                                                howMuchWeHave = (state[i] - 1) * subSet2[sub_pName][i]
                                            else:
                                                howMuchWeHave = state[i] * subSet2[sub_pName][i]
                                            
                                            if howMuchWeHave > howMuchNeeded:
                                                #print(i, " = ", state[i], "@@@@", howMuchWeHave, howMuchNeeded)
                                                flag = True
                                        if not flag:
                                            return 0

                                                



                                   
            #print ("____4.2____")
            return inf



        # once you have upgraded version of something don't use the old version
        
        if pName in actions:
            if 'Requires' in recipes[action]:
                usedItem = list(recipes[action]['Requires'].keys())[0] 
            else:
                usedItem = None
            for a in list(actions[pName].keys()):
                if a != usedItem and actions[pName][a] < actions[pName][usedItem]:
                    if state[a] > 0:
                        print("1231212412412")
                        return inf
        
        
        return 0

        

    for (goal_name, goal_amount) in goal.items():
        requireOrConsume((goal_name, goal_amount))
    findSameActions()
    rec(goal)      
    everyThingToDict()
    
    #print ("\nrequires: ", requires)
    #print ("\nconsumes: ", consumes)
    print ("\nr: ", r)
    print ("\nc: ", c)
    print ("\nc2: ", c2)
    print ("\nActions: ", actions)

    return heuristic


def make_heuristic(recipes, goal):
    # sees what goals need
    requires = {}
    consumes = {}

    def rec(goal):
        for goal_name, goal_amount in goal.items():
            #print("Goal Name: ", goal_name, "\nGoal Amount: ", goal_amount)
            for receipe_name, rule in recipes.items():
                if goal_name in rule['Produces']:
                    p_amount = rule['Produces'][goal_name]
                    if 'Requires' in rule:
                        for name in rule['Requires']:
                            if name not in requires:
                                requires[name] = []
                                rec({name: 1})           
                    if 'Consumes' in rule:
                        for name in rule['Consumes']:
                            howMuch = rule['Consumes'][name]
                            #howMuch = ceil(goal_amount * rule['Consumes'][name] / p_amount)
                            if goal_name in requires and name not in requires[goal_name]:
                                requires[goal_name].append({name: howMuch})
                            if goal_name not in requires:
                                if goal_name in consumes and name not in consumes[goal_name]:
                                    consumes[goal_name].append({name: howMuch})
                                elif goal_name not in consumes:
                                    consumes[goal_name] = []
                                    rec({name: 1})


                            
                                howMuch = ceil(goal_amount * rule['Consumes'][name] / p_amount)
                                if name not in consumes:
                                    consumes[name] = rule['Consumes'][name] * howMuch
                                    rec({name: consumes[name]})
                                else:
                                    consumes[name] = rule['Consumes'][name] * howMuch
                            

    def heuristic(state, action):
        # once you have upgraded version of something don't make the old version
        # once you have upgraded version of something don't use the old version
        # once you made an item that is  a requirement don't make it again unless it's the goal
        
        for item in state.keys():
            if state[item] > 0:
                if (item not in consumes or consumes[item] < state[item]):
                    if (item not in requires):
                        return inf
                    else:
                        if ((state[item] > 1 and item not in goal) or (item in goal and goal[item] < state[item])):
                            return inf

        return 0

        for item in state.keys():
            if state[item] > 0:
                if (item not in consumes or consumes[item] < state[item]) and (item not in requires or state[item] > 1):
                    return inf
        return 0
        

    rec(goal)               

    print ("requires: ", requires)
    print ("consumes: ", consumes)

    return heuristic
"""


def make_heuristic(recipes, goal):

    requires = []
    consumes = []
    r = {}
    t = {'ingot': 6, 'stick': 1}


    def everyThingToDict():
        for item in requires:
            r[item] = 1
                   
        for receipe_name, rule in recipes.items(): 
            if 'Consumes' in rule:
                for name in rule['Consumes']:
                    if name not in r or r[name] < rule['Consumes'][name]:
                        r[name] = rule['Consumes'][name]
                for name in rule['Produces']:
                    if name not in r or r[name] < rule['Produces'][name]:
                        r[name] = rule['Produces'][name]


    def requireOrConsume(goal):
        goal_name, goal_amount = goal
        print (goal_name)
        if goal_name not in r or r[goal_name] < goal_amount:
            r[goal_name] = goal_amount


    def rec(goal):
        for goal_name, goal_amount in goal.items():
            for receipe_name, rule in recipes.items():
                if goal_name in rule['Produces']:
                    p_amount = rule['Produces'][goal_name]
                    if 'Requires' in rule:
                        for name in rule['Requires']:
                            if name not in requires:
                                requires.append(name)
                                rec({name: 1})
                    if 'Consumes' in rule:
                        for name in rule['Consumes']:
                            if name not in consumes:
                                consumes.append(name)
                                rec({name: 1})


    def heuristic(state, action):
        #print (state)

        pName, pAmount = list(recipes[action]['Produces'].items())[0]


        if pName in t and state[pName] <= r[pName]:
            #print("Asdfasfdasf")
            #print (pName, state[pName])
            return -1000

        
        #print (pName, state, s, "\n\n")
        """
        flag = False
        for goal_name, goal_amount in goal.items():
            for receipe_name, rule in recipes.items():
                if goal_name in rule['Produces']:
                    if 'Requires' in rule:
                        for name in rule['Requires']:
                            if s[name] < rule['Requires'][name]:
                                flag = True
                                break
                    if 'Consumes' in rule:
                        for name in rule['Consumes']:
                            if s[name] < rule['Consumes'][name]:
                                flag = True
                                break
        if not flag:
            print ("affa")
            return inf
        """
        

        for item in state:
            if state[item] == 0: 
                continue
            if item in r and state[item] > r[item]:
                #print("____1____")
                return inf

        

        return 0
        
      

    

    rec(goal)
    everyThingToDict()
    for (goal_name, goal_amount) in goal.items():
       requireOrConsume((goal_name, goal_amount)) 
       
    #print (requires)
    #print (consumes)
    print (r)


    return heuristic


def search(graph, state, is_goal, limit, heuristic):
    start_time = time()
    queue = []
    cost = {}
    prev = {}
    action = []

    cost[state] = 0
    prev[state] = None

    # heuristic, cost, state, action
    heappush(queue, (0, (0, state, None)))

    # Search
    while time() - start_time < limit:
        estimatedDist, node = heappop(queue)

        if (estimatedDist == inf):
            print ("wtf", state)
            #print("asdfadsf",node[2], node[1])
        #print(node[2], node[1])


        if is_goal(node[1]):
            total_cost = node[0]
            while node != None:
                action.append(node[2])
                node = prev[node[1]]
            action.reverse()
            print("Time: ", time() - start_time)
            return total_cost, action

        for a, s, c in graph(node[1]):
            alt = node[0] + c
            if s not in cost or alt < cost[s]:
                cost[s] = alt
                prev[s] = node
                new_node = (alt, s, a)
                if new_node not in queue:
                    heappush(queue, (alt+heuristic(s, a), new_node))


    # Failed to find a path
    print("Failed to find a path from", state, 'within time limit.')
    return None, None


if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # List of items that can be in your inventory:
    print('All items:',Crafting['Items'])

    # List of items in your initial inventory with amounts:
    print('Initial inventory:',Crafting['Initial'])

    # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])

    # Dict of crafting recipes (each is a dict):
    #print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])
    heuristic = make_heuristic(Crafting['Recipes'], Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search - This is you!
    total_cost, actions = search(graph, state, is_goal, 30, heuristic)
    #if actions:
        #print ("\n\n", state, "\n")
    if actions:
        for action in actions:
            for recipe in all_recipes:
                if action == recipe.name:
                    state = recipe.effect(state)
                    print (recipe.cost, ", ", recipe.name, "-> \n", state, "\n")
        print("total_cost: ", total_cost, ", length: ", len(actions), "\n\n")

    

