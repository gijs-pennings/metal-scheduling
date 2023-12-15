from greedy_partitioner import *
from data_structures import *

# read problem
problem = read_problem("data/input/data.csv")

# read provided solution for this problem
# solution = parse_solution(problem)
# print(solution.cost())
# print(feasibility(solution))

# solve problem, compute cost, and check feasibility
solution = solve(problem)
print(solution.cost())
print(feasibility(solution))

# write solution to file (for visualization)
write_solution(solution, "greedy_solution.csv")
