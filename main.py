import os
import time
import numpy as np
import gurobipy as grb

import problem as pr
import euristiche as eu


np.random.seed(2)

# define initial parameters
n_bins = 25
n_bin_types = 9
n_compulsory_items = 9
n_non_compulsory_items = 12
n_items = n_compulsory_items + n_non_compulsory_items

items, bins, budget = pr.generate_instance(n_bins, n_bin_types, 
                                            n_compulsory_items,
                                            n_non_compulsory_items)

########################################################################
### Gurobi solver ###
model = grb.Model('gbpp')

C = [bins[j].C for j in range(n_bins)]
W = [bins[j].W for j in range(n_bins)]
p = [items[i].p for i in range(n_items)]
w = [items[i].w for i in range(n_items)]

# Y = 1 if bin j is rented
Y = model.addVars(n_bins, vtype=grb.GRB.BINARY, name='Y')

X = model.addVars(n_items, n_bins, vtype=grb.GRB.BINARY, name='X')

# set objective function
expr = sum(
    C[j] * Y[j] for j in range(n_bins)
)
expr -= grb.quicksum(p[i] * X[i,j] for i in range(n_compulsory_items, 
                    n_items) for j in range(n_bins))
model.setObjective(expr, grb.GRB.MINIMIZE)
model.update()

# add capacity constraints
model.addConstrs(
    (grb.quicksum(w[i]*X[i,j] for i in range(n_items)) <= W[j]*Y[j] \
                    for j in range(n_bins)),
    name="capacity_constraint"
)

# add compulsory item constraints
model.addConstrs(
    ( grb.quicksum(X[i,j] for j in range(n_bins)) == 1 \
                    for i in range(n_compulsory_items)),
    name="compulsory_item"
)

# add non compulsory item constraints
model.addConstrs(
    ( grb.quicksum(X[i,j] for j in range(n_bins)) <= 1 \
                    for i in range(n_compulsory_items, n_items)),
    name="non_compulsory_item"
)

model.addConstr(
    ( grb.quicksum(C[j]*Y[j] for j in range(n_bins)) <= budget),
    name="budget_constraint"
)

# model.setParam('MIPgap', 0.1)
# model.setParam(grb.GRB.Param.TimeLimit, 3600)
model.setParam('OutputFlag', 1)

model.setParam(
    'LogFile',
    os.path.join('.', 'logs', 'gurobi.log') 
)
model.write(
    os.path.join('.', 'logs', "model.lp") 
)
start = time.time()
model.optimize()
end = time.time()
comp_time = end - start

# This function converts the solution given by X and Y in a more 
# readable and manageable dictionary format
def change_form(items, bins):
    for j in range(n_bins):
        for i in range(n_items):
            if X[i,j].X > 0.5:
                bins[j].add_item(items[i])
    return bins

sol = pr.Solution(change_form(items, bins), budget)

print('Gurobi solution:')
sol.print()
print(model.ObjVal)
print(f"computational time: {comp_time} s\n")

#######################################################################
### Heuristics ###

# We first have to reset bins in term of capacities and items contained
for bin in bins:
    bin.reset_bin()


### Greedy algorithm ###
start = time.time()
greedy = eu.greedy_solution(items, bins, budget)
end = time.time()
comp_time = end - start

print('Greedy solution:')
greedy.print()
print(greedy.obj_value(items))
print(f"computational time: {comp_time} s\n")


### First Fit algorithm ###
start = time.time()
constructive = eu.first_fit(items, bins, budget)
end = time.time()
comp_time = end - start

print('First Fit solution:')
constructive.print()
print(constructive.obj_value(items))
print(f"computational time: {comp_time} s\n")


### Local search algorithm ###
start = time.time()
local = eu.local_search(items, bins, budget)
end = time.time()
comp_time = end - start

print('Local Search solution:')
local.print()
print(local.obj_value(items))
print(f"computational time: {comp_time} s\n")


### GRASP algorithm ###
start = time.time()
GRASP = eu.GRASP_algorithm(items, bins, budget)
end = time.time()
comp_time = end - start

print('GRASP solution:')
GRASP.print()
print(GRASP.obj_value(items))
print(f"computational time: {comp_time} s\n")


### LNS algorithm ###
start = time.time()
LNS = eu.LNS_algorithm(items, bins, budget)
end = time.time()
comp_time = end - start

print('LNS solution:')
LNS.print()
print(LNS.obj_value(items))
print(f"computational time: {comp_time} s\n")


### Mixing GRASP and LNS ###
start = time.time()
GRASP_large = eu.GRASP_large_search(items, bins, budget)
end = time.time()
comp_time = end - start

print('GRASP large solution:')
GRASP_large.print()
print(GRASP_large.obj_value(items))
print(f"computational time: {comp_time} s\n")


start = time.time()
LNS_local = eu.LNS_algorithm(items, bins, budget)
end = time.time()
comp_time = end - start

print('LNS local solution:')
LNS_local.print()
print(LNS_local.obj_value(items))
print(f"computational time: {comp_time} s\n")

