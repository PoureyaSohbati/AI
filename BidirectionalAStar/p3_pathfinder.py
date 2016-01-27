from math import sqrt, inf
from heapq import heappush, heappop

def find_path(source, destination, mesh):
	queue = []
	forward_dist = {}
	backward_dist = {}
	forward_prev = {}
	backward_prev = {}
	path = []
	visited = []
	forward_coord = {}
	backward_coord = {}

	sourceBox = findBox(source, mesh)
	visited.append(sourceBox)
	destinationBox = findBox(destination, mesh)


	if destinationBox == None or sourceBox == None:
		print("No Path!")
		return [], []

	boxes = list(mesh['boxes'])
	for box in boxes:
		forward_dist[box] = inf
		forward_prev[box] = None
		backward_dist[box] = inf
		backward_prev[box] = None

	forward_dist[sourceBox] = 0
	forward_prev[sourceBox] = None
	backward_dist[destinationBox] = 0
	backward_prev[destinationBox] = None
	forward_coord[sourceBox] = source
	backward_coord[destinationBox] = destination

	heappush(queue, (0, sourceBox, 'destination'))
	heappush(queue, (0, destinationBox, 'source'))

	#counterD = 0
	#counterS = 0

	while queue:
		d, box, goal = heappop(queue)

		if(backward_prev[box] and forward_prev[box]):
			b = box
			while forward_prev[b] != None:
				path.append((forward_coord[forward_prev[b]], forward_coord[b]))
				b = forward_prev[b]
			path.reverse()
			path.append((forward_coord[box], backward_coord[box]))
			while backward_prev[box] != None:
				path.append((backward_coord[box], backward_coord[backward_prev[box]]))
				box = backward_prev[box]

			#print(counterD, counterS)
			return path, visited

		neighbors = mesh['adj'][box]
		for neighbor in neighbors:

			if goal == 'destination':
				#counterD += 1
				nc = find_box_coordinate(forward_coord[box], neighbor)
				act_dist = actual_distance(forward_coord[box], nc)
				alt = forward_dist[box] + act_dist
				if alt < forward_dist[neighbor]:
					forward_dist[neighbor] = alt
					forward_prev[neighbor] = box
					forward_coord[neighbor] = nc
					if neighbor not in queue:
						visited.append(neighbor)
						heappush(queue, (alt + heuristic(nc, destination), neighbor, goal))

			else:
				#counterS += 1
				nc = find_box_coordinate(backward_coord[box], neighbor)
				act_dist = actual_distance(backward_coord[box], nc)
				alt = backward_dist[box] + act_dist
				if alt < backward_dist[neighbor]:
					backward_dist[neighbor] = alt
					backward_prev[neighbor] = box
					backward_coord[neighbor] = nc
					if neighbor not in queue:
						visited.append(neighbor)
						heappush(queue, (alt + heuristic(nc, source), neighbor, goal))

	print ("No Path!")
	return [], []

def findBox(coor, mesh):
	boxes = list(mesh['boxes'])
	for box in boxes:
		if box[0] < coor[0] and box[1] > coor[0]: # between x
			if box[2] < coor[1] and box[3] >  coor[1]: # between y
				return box
	return None

def heuristic (point1, point2):
	return sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))

def find_box_coordinate(coor, box):
	bx1 = box[2]
	bx2 = box[3]
	by1 = box[0]
	by2 = box[1]

	best_x = min (bx2, max(bx1, coor[1]))
	best_y = min(by2, max(by1, coor[0]))
	return (best_y, best_x)

def actual_distance(point1, point2):
	return sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))

		