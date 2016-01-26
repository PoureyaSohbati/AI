from p1_support import load_level, show_level, save_level_costs
from math import inf, sqrt
from heapq import heappop, heappush


def dijkstras_shortest_path(initial_position, destination, graph, adj):
    """ Searches for a minimal cost path through a graph using Dijkstra's algorithm.

    Args:
        initial_position: The initial cell from which the path extends.
        destination: The end location for the path.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        If a path exits, return a list containing all cells from initial_position to destination.
        Otherwise, return None.

    """

    distances = {initial_position: 0}           # Table of distances to cells 
    previous_cell = {initial_position: None}    # Back links from cells to predecessors
    queue = [(0, initial_position)]             # The heap/priority queue used

    # Initial distance for starting position
    distances[initial_position] = 0

    while queue:
        # Continue with next min unvisited node
        current_distance, current_node = heappop(queue)
        
        # Early termination check: if the destination is found, return the path
        if current_node == destination:
            node = destination
            path = [node]
            while node is not None:
                path.append(previous_cell[node])
                node = previous_cell[node]
            return path[-2::-1]

        # Calculate tentative distances to adjacent cells
        for adjacent_node, edge_cost in adj(graph, current_node):
            new_distance = current_distance + edge_cost

            if adjacent_node not in distances or new_distance < distances[adjacent_node]:
                # Assign new distance and update link to previous cell
                distances[adjacent_node] = new_distance
                previous_cell[adjacent_node] = current_node
                heappush(queue, (new_distance, adjacent_node))
                    
    # Failed to find a path
    print("Failed to find a path from", initial_position, "to", destination)
    return None


def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """
    distances = {initial_position: 0}           # Table of distances to cells 
    previous_cell = {initial_position: None}    # Back links from cells to predecessors
    queue = [(0, initial_position)]             # The heap/priority queue used

    # Initial distance for starting position
    distances[initial_position] = 0

    while queue:
        # Continue with next min unvisited node
        current_distance, current_node = heappop(queue)

        # Calculate tentative distances
        for adjacent_node, edge_cost in adj(graph, current_node):
            new_distance = current_distance + edge_cost

            if adjacent_node not in distances or new_distance < distances[adjacent_node]:
                # Assign new distance and update link to previous cell
                distances[adjacent_node] = new_distance
                previous_cell[adjacent_node] = current_node
                heappush(queue, (new_distance, adjacent_node))

    # Return distances
    return distances


def navigation_edges(level, cell):
    """ Provides a list of adjacent cells and their respective costs from the given cell.

    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        cell: A target location.

    Returns:
        A list of tuples containing an adjacent cell's coordinates and the cost of the edge joining it and the
        originating cell.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """
    x, y = cell
    spaces = level['spaces']
    adjacent_nodes = {}

    for delta_x in [-1, 0, 1]:
        for delta_y in [-1, 0, 1]:
            next_cell = (x + delta_x, y + delta_y)
            if next_cell != cell and next_cell in spaces:
                distance = sqrt(delta_x ** 2 + delta_y ** 2)
                adjacent_nodes[next_cell] = distance * (spaces[cell] + spaces[next_cell])/2

    return adjacent_nodes.items()


def test_route(filename, src_waypoint, dst_waypoint):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source and destination coordinates from the level.
    src = level['waypoints'][src_waypoint]
    dst = level['waypoints'][dst_waypoint]

    # Search for and display the path from src to dst.
    path = dijkstras_shortest_path(src, dst, level, navigation_edges)
    if path:
        show_level(level, path)


def cost_to_all_cells(filename, src_waypoint, output_filename):
    """ Loads a level, calculates the cost to all reachable cells from
    src_waypoint, then saves the result in a csv file with name output_filename.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        output_filename: The filename for the output csv file.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source coordinates from the level.
    src = level['waypoints'][src_waypoint]

    # Calculate the cost to all reachable cells from src and save to a csv file.
    costs_to_all_cells = dijkstras_shortest_path_to_all(src, level, navigation_edges)
    save_level_costs(level, costs_to_all_cells, output_filename)


if __name__ == '__main__':
    filename, src_waypoint, dst_waypoint = 'test_maze.txt', 'a', 'b'

    # Use this function call to find the route between two waypoints.
    test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_costs.csv')
