from clustering import cluster_step_classes_by_length_then_sort
from data_structures import *
from utils import *
import math


def sequence_to_schedule(solution: Solution, sequence: list[Step]) -> Solution:
    """
    Extend an existing schedule `solution` with a sequence of steps for machine C. The schedules for machine A and B are
    inferred from machine C. This function does not modify `solution`, but returns a copy with changes.
    """

    assert all(s.phase() == 2 for s in sequence), "`sequence` must only consist of steps for the Slab Caster"
    assert all_unique(s.index for s in sequence)
    assert all(solution.start[s.index] is None for s in sequence)

    solution = solution.copy()

    start = [0, 0, 0]
    previous_metal = 0

    if all(t is None for t in solution.start):
        first_run = sequence[0].run

        step_a = first_run.steps[0]
        step_b = first_run.steps[1]
        step_c = sequence[0]

        start[0] = 0
        start[1] = start[0] + step_a.length
        start[2] = max(start[1] + step_b.length, 172800 - step_c.length)

        previous_metal = first_run.metal
    else:
        for i, t in enumerate(solution.start):
            if t is not None:
                step = solution.problem.steps[i]
                p = step.phase()
                if t + step.length > start[p]:
                    start[p] = t + step.length
                    if p == 2:
                        previous_metal = step.run.metal

    runs = [s.run for s in sequence]
    for run in runs:
        setup_time = 3600 if run.metal != previous_metal else 0
        previous_metal = run.metal

        for step in run.steps:
            p = step.phase()

            solution.start[step.index] = max(start[p], start[max(0, p-1)])
            start[p] = solution.start[step.index] + step.length

            if p == 2:
                solution.start[step.index] += setup_time
                start[p] += setup_time

    return solution


# interval = time between due dates
# sequence = series of steps belonging to machine C and one metal that are of approx. the same scale

#  0. filter Cxxx steps, i.e., only consider machine C
#  1. split problem into subproblems w.r.t. due dates
#     i.e., find all due dates and partition steps
#  2. solve each subproblem with parameters (start time, list of steps, current metal type of slab caster)
#     the start time of the next subproblem is the end of the previous
#  3. combine subproblems
#     be careful with the setup times
#  4. derive schedule for A,B from this schedule for C (call Pieter's function)

# (temp) for now we consider a fixed 2 clusters per metal, so 6 sequences for each interval

# func solve(start time, step list, current metal):
#  1. for each metal, cluster the steps w.r.t. time into (two) sequences
#  2. sort the sequences from shortest to longest step
#  3. compute avg. step length for each sequence
#  4. concat sequences from least to most avg. step length

# TODO: the very first step can be the largest one, since the time before 172800 is essentially free
#       this is implemented naively, can be improved by trying all three options of longest run per metal

def solve(problem: Problem) -> Solution:
    # partition the runs of `problem` into `subproblems` w.r.t. the due dates
    # the first subproblem corresponds to the first due date, the second to the second, etc.
    subproblems: list[list[Run]] = list_group_by(problem.runs, lambda r: r.due)

    # solve each subproblem in order (greedily) and simply concat schedules
    solution = Solution(problem)  # create empty solution
    for i, sub in enumerate(subproblems):
        print(f"subproblem {i}")
        solution = solve_interval(i == 0, solution, sub)

    return solution



def solve_interval(firstInterval: bool, solution: Solution, runs: list[Run]) -> Solution:
    assert all(r.due == runs[0].due for r in runs), "all runs must share a due date"
    assert all(all(solution.start[s.index] is None for s in r.steps) for r in runs)

    # determine metal of slab caster at the end of `solution` (if it's not empty)
    last_run = solution.get_last_run()
    last_metal = None if last_run is None else last_run.metal

    # partition the last steps of `runs` w.r.t. metal type
    runs_by_metal: list[list[Run]] = list_group_by(runs, lambda r: r.metal)
    steps_by_metal: list[list[Step]] = [[r.steps[-1] for r in rs] for rs in runs_by_metal]
    num_metals = len(runs_by_metal)

    # for each metal type, cluster the steps w.r.t. their length
    # here we try different numbers of clusters, and take the clustering that yields the min cost
    best_solution: Solution | None = None
    best_cost: float = math.inf  # min cost so far
    for combination in compute_combinations(num_metals, 4):  # TODO: 4 clusters per metal for now
        clusters = cluster_step_classes_by_length_then_sort(steps_by_metal, combination)
        sequence = [s for c in clusters for s in c]  # flatten the clusters     TODO: try multiple orderings

        # if first interval, use the 'free' buffer space at the start of the solution
        if firstInterval:
            first_metal = sequence[0].run.metal
            max_job = max([s for s in sequence if s.run.metal == first_metal], key=lambda s: s.length)
            sequence.remove(max_job)
            sequence.insert(0,max_job)
            # TODO if the max_job is too lang for buffer space, then we should actually look for the longest
            #      job that fits, and put that one first

        # extend the solution (up to the last due date) with the current clustering
        new_solution = sequence_to_schedule(solution, sequence)

        # compute cost and take solution whose cost is minimal
        new_cost = new_solution.cost(runs)
        new_cost += last_metal is not None and sequence[0].run.metal != last_metal  # add one hour of setup time if first metal is different
        if best_solution is None or new_cost < best_cost:
            best_solution = new_solution
            best_cost = new_cost

        comb_string = ", ".join([str(i) for i in combination])
        print(f"    with [{comb_string}] clusters, cost = {new_cost}")

    # flatten clusters (temp)
    return best_solution
