from scipy.optimize import linprog
import numpy as np


class Node:
	def __init__(self, parent, x=[], index=0):
		self._x = x
		self._parent = parent
		self._index = index

		print("Node:", index)
		print("x:",_x)


######################################################
c = [-78, -77, -90, -97, -31]

A_ub = [
			[11, 4, -41, 44, 7],
			[-87, 33, 24, 14, -13],
			[61, 69, 69, -57, 23]
	]

b_ub = [82, 77, 87]

int_var = [1,2,3]

# bounds for x0, x1 ...
# Ex: bounds for x0, x1 (None => no constraint)
# x_bounds = (
#	(0, None),
#	(-3, None)
#	)
x_bounds = []

x_bounds.append([2, None])
x_bounds.append([0, None])
x_bounds.append([0, None])
x_bounds.append([0, None])
x_bounds.append([0, None])


dangling_nodes = []
######################################################

res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=x_bounds)

print(res['message'])
print(res['fun'])
print(res['x'])




