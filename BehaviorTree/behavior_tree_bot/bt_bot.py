#!/usr/bin/env python
#

"""
// The do_turn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist.
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


def setup_behavior_tree():
    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    grab_what_enemy_wants = Sequence(name='Getting what enemy wants')
    neutral_planet_check = Check(if_neutral_planet_available)
    is_grabbing = Check(if_a_good_neutral_available)
    take_good_neutral = Action(if_a_good_neutral_available_now)
    grab_what_enemy_wants.child_nodes = [neutral_planet_check, is_grabbing, take_good_neutral]


    offensive_plan = Sequence(name='Offensive Strategy')
    largest_fleet_check = Check(have_largest_fleet)
    #largest_growth_rate_check = Check(have_largest_growth_rate)
    attack = Action(attack_weakest_enemy_planet)
    offensive_plan.child_nodes = [largest_fleet_check, attack]

    send_three_to_neutral = Sequence(name='send 3 neutral')
    above_30 = Check(above_30_not_sending)
    send_one = Action(send_to_closest_neutral_if_backup)
    send_backup = Action(send_affensive_help)
    send_three_to_neutral.child_nodes = [above_30, send_one, send_backup, send_backup]
    

    spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    have_enough = Check(if_dont_have_enough_neutral)
    #spread_action = Action(spread_to_weakest_neutral_planet)
    spread_action = Action(spread_to_best_neutral)
    #spread_action = Action(send_to_closest_neutral)
    spread_sequence.child_nodes = [neutral_planet_check, have_enough, spread_action]

    root.child_nodes = [grab_what_enemy_wants, offensive_plan, spread_sequence]

    logging.info('\n' + root.tree_to_string())
    return root


if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                behavior_tree.execute(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
