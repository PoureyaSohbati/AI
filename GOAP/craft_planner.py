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


def heuristic(state):
    # This heuristic function should guide your search.
    return 0


"""
def search(graph, state, is_goal, limit, heuristic):
    start_time = time()

    # Search
    while time() - start_time < limit:
        pass

    # Failed to find a path
    print("Failed to find a path from", state, 'within time limit.')
    return None
"""

def search(graph, state, is_goal, limit, heuristic):
    start_time = time()

    # Search
    while time() - start_time < limit:
        pass

    # Failed to find a path
    print("Failed to find a path from", state, 'within time limit.')
    return None

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
    print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])


    print ("Original State: ", state)
    newstate = state.copy();
    for i in all_recipes:
        if i.name == "craft furnace at bench":
            if i.check(state) == False:
                print ("fuck")
            else:
                newstate = i.effect(state)
                print ("New State: ", newstate)

    if is_goal(newstate):
        print("goal satisfied")
    else:
        print("goal failed")

    # Search - This is you!





