from math import ceil
import sys
sys.path.insert(0, '../')
#from planet_wars import issue_order
from planet_wars import *

growthRateIm = -1.0/4.0
distIm = 3.0
fleetIm = 2.0

"""
def attack_weakest_enemy_planet(state):

  
    # Find my strongest planet.
    strongest_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    # Find the weakest enemy planet.
    weakest_planets = sorted(state.enemy_planets(), key=lambda p: p.num_ships)

    if not strongest_planets or not weakest_planets:
    # No legal source or destination
        return False

    #for weakest_planet in weakest_planets:
    weakest_planet = weakest_planets[0]
    total_ship_sent = 0
    num_turns = 0
    for strongest_planet in strongest_planets:
        if any(mFleet.source_planet == strongest_planet.ID and mFleet.destination_planet ==  weakest_planet.ID for mFleet in state.my_fleets()):
            continue
        temp_num_turns = state.distance(strongest_planet.ID, weakest_planet.ID)
        if temp_num_turns > num_turns:
            num_turns = temp_num_turns
        total_ship_sent += strongest_planet.num_ships / 2
        issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2 )

    return True

"""
def attack_weakest_enemy_planet(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    enemy_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

"""
def spread_to_best_neutral(state):
    strongest_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    best_neutrals = sorted(state.neutral_planets(), key=lambda p: p.growth_rate * growthRateIm \
                        + state.distance(strongest_planet.ID, p.ID) * distIm \
                        + p.num_ships * fleetIm)


    if not strongest_planets or not best_neutrals:
        return False

    for best_neutral in best_neutrals:
        if strongest_planet.num_ships < best_neutral.num_ships:
            return False

        #ship_amount = ceil((strongest_planet.num_ships - best_neutral.num_ships) * 2.0)
        ship_amount = best_neutral.num_ships + 2
        return issue_order(state, strongest_planet.ID, best_neutral.ID, ship_amount )
"""

def spread_to_best_neutral(state):
    strongest_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    if strongest_planets:
        strongest_planet = strongest_planets[0]
    else: 
        return False

    best_neutrals = sorted(state.neutral_planets(), key=lambda p: p.growth_rate * growthRateIm \
                        + state.distance(strongest_planet.ID, p.ID) * distIm \
                        + p.num_ships * fleetIm)


    if not strongest_planets or not best_neutrals:
        return False

    i = 0

    if any(mFleet.source_planet == strongest_planet.ID for mFleet in state.my_fleets()):
        return False 

    for best_neutral in best_neutrals:
        if i == 3:
            return True

        if strongest_planet.num_ships < best_neutral.num_ships:
            return False

        ship_amount = best_neutral.num_ships + 2
        issue_order(state, strongest_planet.ID, best_neutral.ID, ship_amount )
        i += 1
    return True


def send_to_closest_neutral(state):
    closet_dist = 10000
    closet_planet = None
    my_planet = None
    
    for mPlanet in state.my_planets():
        if any(mFleet.source_planet == mPlanet.ID for mFleet in state.my_fleets()):
            continue 
        for nPlanet in state.neutral_planets():
            if mPlanet.num_ships < nPlanet.num_ships:
                continue
            if any(mFleet.destination_planet == nPlanet.ID for mFleet in state.my_fleets()):
                continue 
            temp_dist = state.distance(mPlanet.ID, nPlanet.ID)
            if (temp_dist < closet_dist):
                closet_dist = temp_dist
                closet_planet = nPlanet
                my_planet = mPlanet

    if closet_planet == None:
        return False

    #ship_amount = ceil((my_planet.num_ships - closet_planet.num_ships) * 2.0)
    ship_amount = closet_planet.num_ships + 2
    return issue_order(state, my_planet.ID, closet_planet.ID, ship_amount )

def send_to_closest_neutral_if_backup(state):
    closet_dist = 10000
    closet_planet = None
    my_planet = None

    for mPlanet in state.my_planets():
        # if already sending from that my_planet skip
        if any(mFleet.source_planet == mPlanet.ID for mFleet in state.my_fleets()):
            continue 
        for nPlanet in state.neutral_planets():
            # if have 1/3 of the neutral ships
            if mPlanet.num_ships < (nPlanet.num_ships / 3.0):
                continue
            # if already sending to the neutral planet skip
            if any(mFleet.destination_planet == nPlanet.ID for mFleet in state.my_fleets()):
                continue 
            # if found a near neutral
            temp_dist = state.distance(mPlanet.ID, nPlanet.ID)
            if (temp_dist < closet_dist):
                closet_dist = temp_dist
                closet_planet = nPlanet
                my_planet = mPlanet

    if closet_planet == None:
        return False

    #ship_amount = ceil((my_planet.num_ships - closet_planet.num_ships) * 2.0)
    ship_amount = ceil(closet_planet.num_ships / 3.0)
    return issue_order(state, my_planet.ID, closet_planet.ID, ship_amount )

"""
def send_from_2_to_neutral(state):
    for i in range (-1, -len(state.my_fleets()), -1):
        print (state.my_fleets()[i])

    for nPlanet in state.neutral_planets():
        shipsGoingToNeutral = 0
        for mFleet in state.my_fleets():
            #if any ships are going to that planet
            if mFleet.destination_planet == nPlanet.ID:
                shipsGoingToNeutral += mFleet.num_ships

        # if there isn't enough ships for invating that planet
        if shipsGoingToNeutral < nPlanet.num_ships:
            # find a close planet to send ship from
            closest_planets = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, nPlanet.ID))
            for i in range (-1, -len(closest_planets), -1):
                print ("asdfa")
                print(-len(closet_planets))
                flag = False
                for mFleet in state.my_fleets():
                    if mFleet.source_planet == closest_planet[i].ID and mFleet.destination_planet == nPlanet:
                        flag = True
                if flag == False:
                    ship_amount = ceil(nPlanet.num_ships / 3.)
                    #if closest_planets[i].num_ships > ship_amount:
                    return issue_order(state, closest_planets[i].ID, nPlanet.ID, ship_amount )
    return False
"""


def send_affensive_help(state):
    #for i in range (-1, -len(state.my_fleets())-1, -1):
    if len(state.my_fleets()) < 1:
        return False

    fleet = state.my_fleets()[-1]

    ships_on_path = 0
    numFleets = 0
    for mFleet in state.my_fleets():
        #if any ships are going to that planet
        if mFleet.destination_planet == fleet.destination_planet:
            ships_on_path += mFleet.num_ships
            numFleets += 1

    if numFleets == 0:
        return False

    # find the destination planet
    nPlanet = None
    for planet in state.not_my_planets():
        if fleet.destination_planet == planet.ID:
            nPlanet = planet
            break

    # if there isn't enough ships for invading that planet
    if ships_on_path < nPlanet.num_ships:
        # sort close planets to send ship from
        closest_planets = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, fleet.destination_planet))
        #closest_planets.reverse()
        ship_amount = ceil(nPlanet.num_ships / 3.)
        if closest_planets[numFleets].num_ships > ship_amount:
            return issue_order(state, closest_planets[numFleets].ID, nPlanet.ID, ship_amount)
        # if not coming from the same planet 
        """
        for cPlanet in closest_planets:
            if any(fleet.destination_planet == myFleet.destination_planet and myFleet.source_planet == cPlanet.ID for myFleet in state.my_fleets()):
               continue
            ship_amount = ceil(nPlanet.num_ships / 3.)
            if cPlanet.num_ships > ship_amount:
                return issue_order(state, cPlanet.ID, nPlanet.ID, ship_amount)
        """
    return False


def if_a_good_neutral_available_now(state):
    limit = 15
    lost_ships = 25
    min_turns = 1000
    best_planet = None

    # enemy fleets
    for eFleet in state.enemy_fleets():
        # neutral planets
        for nPlanet in state.neutral_planets():
            # if going to that planet
            if any(mFleet.destination_planet == nPlanet.ID for mFleet in state.my_fleets()):
                continue 
            if eFleet.destination_planet == nPlanet.ID:
                # if is worth it 
                if eFleet.num_ships < lost_ships:
                    continue
                # if amount of ships left is less than 15
                ships_alive = abs(eFleet.num_ships - nPlanet.num_ships)
                if  ships_alive < limit:
                    # how long it takes to get to the other planet
                    for planet in state.my_planets():
                        num_turns_enemy = state.distance(planet.ID, eFleet.destination_planet)
                        # if my planet has enough ships
                        num_ships = state.distance(nPlanet.ID, planet.ID) + ships_alive
                        if planet.num_ships > limit+2:
                            #send from the closest planet
                            num_turns_mine = state.distance(planet.ID, eFleet.destination_planet) - num_turns_enemy
                            if (num_turns_mine > 0) and (min_turns > num_turns_mine):
                                min_turns = num_turns_mine
                                best_planet = planet 
                    if best_planet:
                        return issue_order(state, best_planet.ID, eFleet.destination_planet, num_ships+2)
    return False

