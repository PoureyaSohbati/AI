

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())


def have_largest_growth_rate(state):
    return sum(planet.growth_rate for planet in state.my_planets()) \
           > sum(planet.growth_rate for planet in state.enemy_planets())


def above_30_not_sending(state):
	counter = 0
	for planet in state.my_planets():
		if planet.num_ships > 30:
			counter += 1
	if counter > 2:
		return True
	return False


def if_a_good_neutral_available(state):
	limit = 15

	nPlanet = min(state.neutral_planets(), key=lambda p: p.num_ships)
	if nPlanet.num_ships < limit:
		return True

	for eFleet in state.enemy_fleets():
		for nPlanet in state.neutral_planets():
			if eFleet.destination_planet == nPlanet.ID:
				if abs(eFleet.num_ships - nPlanet.num_ships) < limit:
					return True
	return False

def if_dont_have_enough_neutral(state):
	return len(state.my_planets()) < 4


def better_enemy_exist(state):
	# Find my strongest planet.
    strongest_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    # Find the weakest enemy planet.
    weakest_planets = sorted(state.enemy_planets(), key=lambda p: p.num_ships)
    return True


def worth_attacking_neutral(state):
	"""
	best_neutral = min(state.neutral_planets(), key=lambda p: p.num_ships)
	if best_neutral.num_ships < 30:
		return True
	return False
	"""
	return min(state.neutral_planets(), key=lambda p: p.num_ships).num_ships < 30

