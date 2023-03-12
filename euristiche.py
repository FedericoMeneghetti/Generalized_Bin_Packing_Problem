import problem as pr
import copy

#######################################################################
### Greedy algorithm ###

def greedy_solution(items, bins, budget):
    
    # We work with a deepcopy of the objects to not modify the original 
    # ones
    items1 = copy.deepcopy(items)
    bins1 = copy.deepcopy(bins)
    res_budg = budget

    # We sort bins and items
    comp_it = [item for item in items1 if item.compulsory]
    n_comp_it = [item for item in items1 if not item.compulsory]
   
    comp_it = sorted(comp_it, key=lambda x: x.w, reverse=True)
    n_comp_it = sorted(n_comp_it, key=lambda x: x.p/x.w, reverse=True)

    items1 = comp_it + n_comp_it
    bins1 = sorted(bins1, key=lambda x: x.W/x.C, reverse=True)

    # Assign each item to the first bin that has enough capacity
    for item in items1:
        for bin in bins1:
            if bin.W_res >= item.w: 
                if bin.items == [] and bin.C <= res_budg:  
                    #if bin was empty, we pay its cost by decreasing 
                    # the budget
                    res_budg -= bin.C
                    bin.add_item(item)
                    bin.W_res -= item.w
                else:
                    bin.add_item(item)
                    bin.W_res -= item.w
                break

    sol = pr.Solution(bins1, res_budg)
    return sol

######################################################################
### Constructive heuristic ###

def first_fit(items, bins, budget, items_order = 'p/w', 
                bins_order = 'W'):
    
    # We work with a deepcopy of the objects to not modify the 
    # original ones
    items1 = copy.deepcopy(items)
    bins1 = copy.deepcopy(bins)
    res_budg = budget

    items1, bins1 = sort_objects(items1, bins1, items_order, bins_order)

    # Bins are divided in selected and free ones
    selected_bins = []
    free_bins = copy.copy(bins1)

    # Assign each item to the first bin that has enough capacity
    for item in items1:
        if item.compulsory: #compulsory items are put in the first 
                            #available bin
            for bin in bins1:
                if bin.W_res >= item.w and bin.C <= res_budg:
                    if bin not in selected_bins:    
                        selected_bins.append(bin)
                        free_bins.remove(bin)
                        res_budg -= bin.C
                    bin.add_item(item)
                    bin.W_res -= item.w
                    break
        else: #non compulsory
            flag = 0 
            for bin in selected_bins:
                #nc items are added if some of the selected bins is 
                #available 
                if bin.W_res >= item.w and bin.C <= res_budg:
                    bin.add_item(item)
                    bin.W_res -= item.w
                    flag = 1
                    break
            if flag == 1:
                continue
            # If no bin was available, items are added only if 
            # convenient
            for fbin in free_bins:
                ind = items1.index(item) 
                items2 = items1[ind:] #not yet collected items 
                profit = 0
                for it in items2:
                    if fbin.W_res >= it.w and fbin.C <= res_budg:  
                        profit = profit + item.p
                if profit > bin.C:
                    selected_bins.append(fbin)
                    free_bins.remove(fbin)
                    fbin.add_item(item)
                    fbin.W_res -= item.w
                    res_budg -= fbin.C
                    break
    
    # We search among the free bins if there if someone with lower cost
    # that can substitute a selected one.
    for bin in selected_bins:
        for other_bin in free_bins:
            if bin.W-bin.W_res <= other_bin.W and other_bin.C < bin.C:
                selected_bins.remove(bin)
                free_bins.append(bin)
                selected_bins.append(other_bin)
                free_bins.remove(other_bin)
                for item in bin.items:
                    other_bin.add_item(item)
                bin.reset_bin()
                res_budg = res_budg + bin.C - other_bin.C
                break
            
    sol = pr.Solution(bins1, res_budg)
    return sol
    

def sort_objects(items, bins, items_order, bins_order):
    '''This function can provide different sortings for bin and items
    according to its input values'''
    
    comp_it = [item for item in items if item.compulsory]
    n_comp_it = [item for item in items if not item.compulsory]

    # Compulsory ones are always sorted according to their w
    comp_it = sorted(comp_it, key=lambda x: x.w, reverse=True)

    if items_order == 'w':
        n_comp_it = sorted(n_comp_it, key=lambda x: x.w, reverse=True)
    if items_order == 'p/w':
        n_comp_it = sorted(n_comp_it, key=lambda x: x.p/x.w,
                            reverse=True)
    if items_order == 'p':
        n_comp_it = sorted(n_comp_it, key=lambda x: x.p, reverse=True)

    items = comp_it + n_comp_it
    
    if bins_order == 'W':
        bins = sorted(bins, key=lambda x: x.W, reverse=True)
    if bins_order == 'W/C':
        bins = sorted(bins, key=lambda x: x.W/x.C, reverse=True)
    if bins_order == 'C':
        bins = sorted(bins, key=lambda x: x.C, reverse=False)
    
    return items, bins

#####################################################################
### Local Search algorithm ###

def local_search(items, bins, budget, max_iter=1000):
    current_solution = first_fit(items, bins, budget)

    # Calculate the objective function value for the current solution
    current_value = current_solution.obj_value(items)

    for i in range(max_iter):
        neighbors = generate_neighbors(current_solution, items, bins)

        # Check if the list of neighbors is empty
        if not neighbors:
            break
        
        # Best neighbor is selected
        best_neighbor = min(
            neighbors, key=lambda x: x.obj_value(items))

        # If the chosen neighboring solution has a lower objective 
        # function value than the current solution, current solution 
        # is updated
        if best_neighbor.obj_value(items) < current_value:
            current_solution = best_neighbor
            current_value = best_neighbor.obj_value(items)
        else:
            break  
    
    return current_solution


def generate_neighbors(solution, items, bins):
    '''It generates a list of neighbors, searching for a bins that can 
    substitute an already selected one'''

    # We make the following deepcopies in order not to loose any
    # original information
    old_sol_bins = copy.deepcopy(solution.bins) 
    bins_list = copy.deepcopy(solution.bins)
    old_budg_res = solution.budget_res
    budg_res = solution.budget_res

    neighbors = []
    
    # neighbors generation strategy
    for bin in bins_list:
        bins1 = copy.deepcopy(old_sol_bins)
        for other_bin in bins:
            other_bin1 = copy.deepcopy(other_bin)
            if bin.W-bin.W_res <= other_bin.W and other_bin.C < bin.C:
                for item in bin.items:
                    other_bin1.add_item(item)
                bins1.append(other_bin1)
                for bin1 in bins1:
                    if bin1.name == bin.name:
                        bins1.remove(bin1)
                budg_res = budg_res + bin.C - other_bin.C
                neighbors.append(pr.Solution(bins1, budg_res))
                budg_res = old_budg_res

    return neighbors

#####################################################################
### GRASP ###

def GRASP_algorithm(items, bins, budget, max_iter=1000):
    solutions = []

    # define the starting points by the constructive heuristcs with 
    # different combinations of objects orders
    solutions.append(first_fit(items, bins, budget, 'p/w', 'W'))
    solutions.append(first_fit(items, bins, budget, 'p', 'C'))
    solutions.append(first_fit(items, bins, budget, 'w', 'W/C'))
    solutions.append(first_fit(items, bins, budget, 'p/w', 'W'))
    solutions.append(first_fit(items, bins, budget, 'p', 'C'))
    solutions.append(first_fit(items, bins, budget, 'w','W/C'))
    solutions.append(first_fit(items, bins, budget, 'p/w', 'W'))
    solutions.append(first_fit(items, bins, budget, 'p', 'C'))
    solutions.append(first_fit(items, bins, budget, 'w', 'W/C'))
    solutions.append(greedy_solution(items, bins, budget))
    
    j = 0
    for current_solution in solutions:
        j+=1  
        current_value = current_solution.obj_value(items)

        # Local search on each starting point
        for i in range(max_iter):
            # Generate a list of valid neighboring solutions
            neighbors = generate_neighbors(current_solution, items, 
                                            bins)
            
            # Check if the list of neighbors is empty
            if not neighbors:
                break
            
            # Best neighbor is selected
            best_neighbor = min(
                neighbors, key=lambda x: x.obj_value(items))

            # If the chosen neighboring solution has a lower objective 
            # function value than the current solution, current 
            # solution is updated
            if best_neighbor.obj_value(items) < current_value:
                current_solution = best_neighbor
                current_value = best_neighbor.obj_value(items)
            else:
                break
        
        # Update the best solution if a better one is found
        if j == 1:
            best_sol = current_solution
        elif current_value < best_sol.obj_value(items):
            best_sol = current_solution 
    
    return best_sol

#######################################################################
### LNS ###

def LNS_algorithm(items, bins, budget, max_iter=1000):
    solutions = []

    # define starting points by the constructive heuristcs with 
    # different combinations of objects orders
    solutions.append(first_fit(items, bins, budget, 'p/w', 'W'))
    solutions.append(first_fit(items, bins, budget, 'p', 'C'))
    solutions.append(first_fit(items, bins, budget, 'w', 'W/C'))
    solutions.append(first_fit(items, bins, budget, 'p/w', 'W'))
    solutions.append(first_fit(items, bins, budget, 'p', 'C'))
    solutions.append(first_fit(items, bins, budget, 'w','W/C'))
    solutions.append(first_fit(items, bins, budget, 'p/w', 'W'))
    solutions.append(first_fit(items, bins, budget, 'p', 'C'))
    solutions.append(first_fit(items, bins, budget, 'w', 'W/C'))
    solutions.append(greedy_solution(items, bins, budget))
    
    # Same process as in GRASP, but with different neighbors
    j = 0
    for current_solution in solutions:
        j+=1  
        current_value = current_solution.obj_value(items)

        for i in range(max_iter):
            # Generate a list of valid neighboring solutions
            neighbors = generate_large_neighbors(current_solution, 
                                                items, bins)
            
            # Check if the list of neighbors is empty
            if not neighbors:
                break
            
            # Best neighbor is selected
            best_neighbor = min(
                neighbors, key=lambda x: x.obj_value(items))
            
            # If the chosen neighboring solution has a lower objective 
            # function value than the current solution, current 
            # solution is updated
            if best_neighbor.obj_value(items) < current_value:
                current_solution = best_neighbor
                current_value = best_neighbor.obj_value(items)
            else:
                break
        
        # Update the best solution if a better one is found
        if j == 1:
            best_sol = current_solution
        elif current_value < best_sol.obj_value(items):
            best_sol = current_solution 
    
    return best_sol

def generate_large_neighbors(solution, items, bins):
    '''It generates a list of neighbors, searching for different items 
    to a fill an already selected bin'''
    
    # We make the following deepcopies in order not to loose any
    # original information
    old_sol_bins = copy.deepcopy(solution.bins) 
    bins_list = copy.deepcopy(solution.bins)
    budg_res = solution.budget_res
    items1 = copy.deepcopy(items)

    # We create the list of free items
    sel_it_name = [it.name for it in solution.items]
    free_items = [it for it in items1 if it.name not in sel_it_name]
    free_items1 = copy.deepcopy(free_items)
    free_items1 = sorted(free_items1, key=lambda x: x.p, reverse=True)

    neighbors = []
    
    for bin in bins_list: 
        bins1 = copy.deepcopy(old_sol_bins)
        for bin1 in bins1:
            if bin.name == bin1.name:
                b = bin1
                break
       
        for item in b.items: #destroy
            if not item.compulsory:
                b.items.remove(item)
                b.W_res += item.w

        for item in free_items1: #repair
            if item.w <= b.W_res:
                b.items.append(item)
                b.W_res -= item.w

        neighbors.append(pr.Solution(bins1, budg_res))

    return neighbors

#######################################################################
### Mixing LNS and GRASP ###

def LNS_local_search(items, bins, budget, max_iter=1000):
    current_solution = LNS_algorithm(items, bins, budget)
    # Calculate the objective function value for the current solution
    current_value = current_solution.obj_value(items)

    for i in range(max_iter):
        neighbors = generate_neighbors(current_solution, items, bins)

        if not neighbors:
            break
        best_neighbor = min(
            neighbors, key=lambda x: x.obj_value(items))

        # If the chosen neighboring solution has a lower objective 
        # function value than the current solution, update the 
        # current solution
        if best_neighbor.obj_value(items) < current_value:
            current_solution = best_neighbor
            current_value = best_neighbor.obj_value(items)
        else:
            break  
    
    return current_solution

def GRASP_large_search(items, bins, budget, max_iter=1000):
    current_solution = GRASP_algorithm(items, bins, budget)
    # Calculate the objective function value for the current solution
    current_value = current_solution.obj_value(items)

    for i in range(max_iter):
        neighbors = generate_large_neighbors(current_solution, items, 
                                            bins)

        if not neighbors:
            break
        best_neighbor = min(
            neighbors, key=lambda x: x.obj_value(items))

        # If the chosen neighboring solution has a lower objective 
        # function value than the current solution, update the 
        # current solution
        if best_neighbor.obj_value(items) < current_value:
            current_solution = best_neighbor
            current_value = best_neighbor.obj_value(items)
        else:
            break  
    
    return current_solution

