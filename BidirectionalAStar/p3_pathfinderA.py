from math import sqrt, inf
from heapq import heappush, heappop

def find_path(source, destination, mesh):
	queue = []
	dist = {}
	prev = {}
	path = []
	visited = []
	coord = {}

	sourceBox = findBox(source, mesh)
	visited.append(sourceBox)
	destinationBox = findBox(destination, mesh)
	#print(source, destination)
	#print(sourceBox, destinationBox)

	if destinationBox == None or sourceBox == None:
		print("No Path!")
		return [], []

	boxes = list(mesh['boxes'])
	for box in boxes:
		dist[box] = inf
		prev[box] = None
		coord[box] = None

	dist[sourceBox] = 0
	prev[sourceBox] = None
	coord[sourceBox] = source
	heappush(queue, (0, sourceBox))

	while queue:
		d, box = heappop(queue)

		if box == destinationBox:
			while box != None:
				path.append(box)
				box = prev[box]
			path.reverse()

			#print (path)
			c = coordinate(path, coord, destination)
			return c, visited

		neighbors = mesh['adj'][box]
		for neighbor in neighbors:
			nc = find_box_coordinate(coord[box], neighbor)
			act_dist = actual_distance(coord[box], nc)
			alt = dist[box] + act_dist
			if alt < dist[neighbor]:
				dist[neighbor] = alt
				prev[neighbor] = box
				coord[neighbor] = nc
				if neighbor not in queue:
					visited.append(neighbor)
					heappush(queue, (alt + heuristic(nc, destination), neighbor))

	print ("No Path!")
	return [], []

def findBox(coor, mesh):
	#print(coor[0], coor[1])
	boxes = list(mesh['boxes'])
	for box in boxes:
		if box[0] < coor[0] and box[1] > coor[0]: # between x
			if box[2] < coor[1] and box[3] >  coor[1]: # between y
				return box
	return None

def coordinate(boxes, coord, destination):
	c = []
	for i in range(len(boxes)-1):
		c.append((coord[boxes[i]],coord[boxes[i+1]]))
	c.append((coord[boxes[-1]], destination))
	return c


def heuristic (point1, point2):
	distance = sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))
	return distance

def find_box_coordinate(coor, box):
	bx1 = box[2]
	bx2 = box[3]
	by1 = box[0]
	by2 = box[1]

	best_x = min (bx2, max(bx1, coor[1]))
	best_y = min(by2, max(by1, coor[0]))
	return (best_y, best_x)

def actual_distance(point1, point2):
	if point1[0] == point2[0]:
		return abs(point1[1] - point2[1])
	elif point1[1] == point2[1]:
		return abs(point1[0] - point2[0])
	else:
		return sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))

		