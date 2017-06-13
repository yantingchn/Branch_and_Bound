from scipy.optimize import linprog
import numpy as np
from math import floor, ceil
import copy

############## var init ####################							
integer_var = [0,1,2]

c = [-78, -77, -90, -97, -31] 				#only for minimization problem

A_ub = [
		[11, 4, -41, 44, 7], 			#row 1
		[-87, 33, 24, 14, -13],			#row 2
		[61, 69, 69, -57, 23]			#row 3
	]

b_ub = [82, 77, 87]							#constraint


# bounds for x0, x1 ...
# Ex: bounds for x0, x1 
# x_bounds = (
#	(0, None),
#	(-3, None)
#	)
#
#None means no constraint
x_bounds = []
x_bounds.append([0, None])
x_bounds.append([0, None])
x_bounds.append([0, None])
x_bounds.append([0, None])
x_bounds.append([0, None])
##############################################


dangling_nodes = []
dangling_nodes_obj = []


class Node:
	def __init__(self, x_bounds=[], freeze_var_list=[], index=0, upper_or_lower=0):
		self._x_bounds = x_bounds
		self._freeze_var_list = freeze_var_list
		self._index = index
		self._upper_or_lower = upper_or_lower

		print("create Node:", index)
		print('')

	def freeze_var(self, index, val):
		self._x_bounds[index][0] = val
		self._x_bounds[index][1] = val
		self._freeze_var_list.append(index)

	def set_lp_res(self, res):
		self._res = res

		s = " "
		for l in range(len(self._res['x'])):
			if l in self._freeze_var_list:
				s += "[" + str(self._res['x'][l]) + "] "
			elif l in integer_var:
				s += "\'" + str(self._res['x'][l]) + "\' "
			else:
				s += str(self._res['x'][l])
		print("x: ", s)

	def check_integer_var_all_solved(self, m):
		return True if m == len(self._freeze_var_list) else False



def solve_LP(x_b):
	global c
	global A_ub
	global b_ub

	return linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=x_b)

def add_dangling_node(node):
	global z_star
	global dangling_nodes
	global dangling_nodes_obj
	global sol_node

	res = solve_LP(node._x_bounds)
	if check_feasibility(res) and res['fun'] < z_star:
		node.set_lp_res(res)
		dangling_nodes_obj.append(res['fun'])
		dangling_nodes.append(node)
		if node.check_integer_var_all_solved(len(integer_var)):
			z_star = res['fun']
			sol_node = node
			print("-----------Temporary sol-----------")
			print("x: ", sol_node._res['x'])
			print("z:", sol_node._res['fun'])
			print("-----------------------------------")
			print('')
		print("=> Add node to dangling list: ", node._index)
		print("=> current dangling nodes:", dangling_nodes_obj)
		print('')
		return True
	else:
		print("=> Node infeasibile: ", node._index)
		print("=> current dangling nodes:", dangling_nodes_obj)
		print('')
		return False

def del_higher_val_node(z_s):
	global dangling_nodes
	global dangling_nodes_obj
	
	del_list = []
	for i in range(len(dangling_nodes_obj)):
		if dangling_nodes_obj[i] >= z_s:
			del_list.append(i)

	s = ""
	for i in del_list:
		s += " " + str(dangling_nodes[i]._index)
		
	print("/***/ Remove nodes:", s)

	dangling_nodes = list(np.delete(dangling_nodes, del_list))
	dangling_nodes_obj = list(np.delete(dangling_nodes_obj, del_list))


	print("/***/ current dangling nodes: ", dangling_nodes_obj)
	print('')

def del_item(index):
	global dangling_nodes
	global dangling_nodes_obj

	print("/***/ Remove node: ", dangling_nodes[index]._index)

	dangling_nodes = list(np.delete(dangling_nodes, index))
	dangling_nodes_obj = list(np.delete(dangling_nodes_obj, index))
	print("/***/ current dangling nodes: ", dangling_nodes_obj)
	print('')

def check_feasibility(res):
	if res['status'] == 0:
		return True
	elif res['status'] == 2:
		return False
	else:
		raise("Problem Unbounded")
		exit()

def check_bounds(x_b, index, u_or_l):
	global x_bounds
	if u_or_l == 1:
		if x_b[index][0] is None and x_bounds[index][0] is not None:
			return False
		elif x_b[index][0] is not None and x_bounds[index][0] is None:
			return True
		elif x_b[index][0] is not None and x_bounds[index][0] is not None:
			return False if (x_b[index][0] < x_bounds[index][0]) else True 
	elif u_or_l == 2:
		if x_b[index][1] is None and x_bounds[index][1] is not None:
			return False
		elif x_b[index][1] is not None and x_bounds[index][1] is None:
			return True
		elif x_b[index][0] is not None and x_bounds[index][0] is not None:
			return False if (x_b[index][1] > x_bounds[index][1]) else True 
	else:
		print ("error of bounds")
		exit()
	


######################################################
print('')
print("######## Start B & B ###########")
print('')

z_star = float('Inf')
node_counter = 0
sol_node = None

node = Node(copy.deepcopy(x_bounds), [] ,node_counter)

node_counter += 1
res = solve_LP(x_bounds)

lower = floor(res['x'][integer_var[0]])
upper = lower + 1

lower_node = Node(copy.deepcopy(x_bounds), [], node_counter, 1)
lower_node.freeze_var(integer_var[0], lower)	
add_dangling_node(lower_node)

node_counter += 1

upper_node = Node(copy.deepcopy(x_bounds), [], node_counter, 2)
upper_node.freeze_var(integer_var[0], upper)
add_dangling_node(upper_node)

node_counter += 1

while len(dangling_nodes) > 0:

	index = np.argmin(dangling_nodes_obj)

	x_b  = dangling_nodes[index]._x_bounds
	frez = dangling_nodes[index]._freeze_var_list
	res = dangling_nodes[index]._res
	frez_var_index = len(frez)

	u_or_l = dangling_nodes[index]._upper_or_lower
	arbitrary_node = Node(copy.deepcopy(x_b), copy.deepcopy(frez), node_counter, copy.deepcopy(u_or_l))
	u_or_l_b = lower-1 if (u_or_l==1) else upper+1
	arbitrary_node.freeze_var(integer_var[frez_var_index - 1], u_or_l_b)
	x_b_arbi = arbitrary_node._x_bounds
	if check_bounds(x_b_arbi, integer_var[frez_var_index - 1], u_or_l):
		add_dangling_node(arbitrary_node)
	else:
		print("arbitrary Node infeasibile: ", arbitrary_node._index)
	
	node_counter += 1


	lower = floor(res['x'][integer_var[frez_var_index]])
	upper = lower + 1

	lower_node = Node(copy.deepcopy(x_b), copy.deepcopy(frez), node_counter, 1)
	lower_node.freeze_var(integer_var[frez_var_index], lower)	
	add_dangling_node(lower_node)

	node_counter += 1

	upper_node = Node(copy.deepcopy(x_b), copy.deepcopy(frez), node_counter, 2)
	upper_node.freeze_var(integer_var[frez_var_index], upper)
	add_dangling_node(upper_node)

	node_counter += 1

	del_item(index)
	del_higher_val_node(z_star)	
	print("#################################")

print('')
print("~~~~~~~~~~~~ Sol ~~~~~~~~~~~~~~")
print(sol_node._res)
print('')


