import numpy as np

# These 2 classes provide a structure for bins and items
class Bin:
    def __init__(self, capacity, cost, type, n):
        self.W = capacity
        self.W_res = capacity
        self.C = cost
        self.type = type
        self.name = f'bin{n}'
        self.n = n
        self.items = []

    def reset_bin(self):
        self.W_res = self.W
        self.items = []

    def add_item(self, item):
        self.items.append(item)


class Item:
    def __init__(self, profit, weight, compulsory, n):
        self.p = profit
        self.w = weight
        self.compulsory = compulsory
        self.n = n
        self.name = f'item{n}'


# Solution class encapsulates all the information about the object 
# involved in the solution
class Solution:
    def __init__(self, bins, budget):
        sol = {}    #solution representation in a dictionary form
        bins1 = []  #bins involved in the solution
        for bin in bins:
            if bin.items:   #we add only the ones that have items
                bins1.append(bin)
        self.bins = bins1
        for bin in self.bins:
            for item in bin.items:
                sol[item] = bin #we build the dictionary form
        self.sol = sol
        self.items = list(sol.keys())
        self.budget_res = budget

    def print(self):
        '''print() method makes the solution readable, printing
        only the names of the objects involved.'''
        
        bins = []
        items = []
        for bin, item in self.sol.items():
            bins.append(bin.name)
            items.append(item.name)
        sol = dict(zip(bins, items))
        print(sol)

    def obj_value(self, items):
        '''It returns the value of the objective function. 
        The value is 'inf' is the constraints are violated'''
        
        if not self.is_valid(items):
            return float('inf')

        total_cost = sum(bin.C for bin in self.bins)
        total_profit = sum(
            item.p for item in self.items if not item.compulsory)

        return total_cost - total_profit

    def is_valid(self, items):
        '''It checks if the solution the problem's constraints'''

        # Budget constraint
        if self.budget_res < 0:
            return False

        # Capacity constraints
        for bin in self.bins:
            total_weight = sum(
                item.w for item in self.items if self.sol[item] == bin)
            if total_weight > bin.W:
                return False

        it_names = []
        for it in self.items:
            it_names.append(it.name)
        
        # Compulsory items' constraint
        for item in items:
            if item.compulsory and item.name not in it_names:
                return False

        return True


def generate_instance(n_bins=10, n_bin_types=10,
                     n_compulsory_items=3, n_non_compulsory_items=4):
    '''This function generate an instance of the problem. Items are 
       a list of dictionaries with profit, weight and compulsory 
       as keys. Bins are a list of dictionaries too, whose kews are 
       capacity, cost and type. Alse the budget constraint is 
       generated.'''

    n_items = n_compulsory_items + n_non_compulsory_items

    C = np.random.uniform(200, 300, n_bin_types)  # costs of the bins
    W = np.random.uniform(6, 20, n_bin_types)  # capacities of the bins
    p = np.random.uniform(100, 120, n_items)  # profits of the items
    w = np.random.uniform(3, 8, n_items)  # weights of the items

    items = []
    for i in range(n_compulsory_items):
        item = Item(p[i], w[i], True, i+1)
        items.append(item)
    for i in range(n_compulsory_items, n_items):
        item = Item(p[i], w[i], False, i+1)
        items.append(item)

    bins = []
    for i in range(n_bins):
        j = np.random.choice(n_bin_types)  # we extract the bin type
        bin = Bin(W[j], C[j], j+1, i+1)
        bins.append(bin)  # bin is instantiated according to its type

    budget = np.random.uniform(2000, 3000)

    return items, bins, budget
