from scipy.optimize import linprog
import numpy as np
from math import floor, ceil

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

class Node:
	def __init__(self, x_bounds=[], freeze_var_list=[], index=0):
		self._x_bounds = x_bounds
		self._freeze_var_list = freeze_var_list
		self._index = index

		print("Node:", index)

	def freeze_var(self, index, val):
		self._x_bounds[index][0] = val
		self._x_bounds[index][1] = val
		self._freeze_var_list.append(index)

	def set_lp_obj_val(self, z):
		self._z = z

	def check_var_in_freeze_var_list(self, index):
		return True if index in self._freeze_var_list else False
		
	def check_integer_var_all_solved(self, m):
		return True if m == len(self._freeze_var_list) else False

	def get_x_bounds(self):
		return self._x_bounds

	def get_freeze_val_list(self):
		return self._freeze_var_list




def solve_LP(x_b):
	return linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=x_b)


######################################################


# res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=x_bounds)

# print(res['message'])
# print(res['fun'])
# print(res['x'])

z_star = -float('Inf')
node_counter = 0

node = Node(x_bounds, [] ,node_counter)
node_counter += 1
x_b  = node.get_x_bounds()
frez = node.get_freeze_val_list()

res = solve_LP(x_b)
node.set_lp_obj_val(res['fun'])


lower = floor(res['x'][integer_var[0]])
upper = lower + 1

lower_node = Node(x_b, frez, node_counter)
lower_node.freeze_var(integer_var[0], lower)
res = solve_LP(lower_node.get_x_bounds())
lower_node.set_lp_obj_val(res['fun'])

upper_node = Node(x_b, frez, node_counter)
upper_node.freeze_var(integer_var[0], upper)
res = solve_LP(upper_node.get_x_bounds())


node_counter += 1



dangling_nodes.append(Node())


while True:


	if len(dangling_nodes) == 0:
		break


