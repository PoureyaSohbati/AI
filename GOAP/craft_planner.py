import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from math import sqrt, inf
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


def make_heuristic(recipes, goal):
    # sees what goals need
    requires = []
    consumes = {}

    def rec(goal):
        for goal_name, goal_amount in goal.items():
            #print("Goal Name: ", goal_name, "\nGoal Amount: ", goal_amount)
            for receipe_name, rule in recipes.items():
                if goal_name in rule['Produces']:
                    if 'Requires' in rule:
                        for name in rule['Requires']:
                            if name not in requires:
                                #####################
                                if name != "iron_pickaxe" and name != "iron_axe":
                                #####################
                                    requires.append(name)
                                    rec({name: 1})
                    if 'Consumes' in rule:
                        for name in rule['Consumes']:
                            if name not in consumes:
                                consumes[name] = rule['Consumes'][name] * goal_amount
                                rec({name: rule['Consumes'][name] * goal_amount})
                            else:
                                consumes[name] += rule['Consumes'][name] * goal_amount


    def heuristic(state, action):
        # once you have upgraded version of something don't make the old version
        # once you have upgraded version of something don't use the old version
        for item in state.keys():
            if state[item] > 0:
                if (item not in consumes or consumes[item] < state[item]) and (item not in requires or state[item] > 1):
                    return inf
        return 0


    rec(goal)               

    print ("requires: ", requires)
    print ("consumes: ", consumes)

    return heuristic


def search(graph, state, is_goal, limit, heuristic):
    start_time = time()
    queue = []
    cost = {}
    prev = {}
    action = []

    cost[state] = 0
    prev[state] = None
    heappush(queue, (0, (cost[state], state, None)))

    # Search
    while time() - start_time < limit:
        estimatedDist, node = heappop(queue)
        if (estimatedDist == inf):
            print ("wtf")

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
            if s not in cost.keys() or alt < cost[s]:
                cost[s] = alt
                prev[s] = node
                new_node = (alt, s, a)
                if new_node not in queue:
                    heappush(queue, (alt+heuristic(s), new_node))

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
    total_cost, actions = search(graph, state, is_goal, 1000, heuristic)
    #if actions:
        #print ("\n\n", state, "\n")
    if actions:
        for action in actions:
            for recipe in all_recipes:
                if action == recipe.name:
                    state = recipe.effect(state)
                    print (recipe.cost, ", ", recipe.name, "-> \n", state, "\n")
        print("total_cost: ", total_cost, ", length: ", len(actions), "\n\n")

    

