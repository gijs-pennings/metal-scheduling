from data_structures import *
from utils import *
import greedy_partitioner


def build_sequence(steps3_all: list[Step], permutations: list[list[int]] | None = None):
    """
    Creates a schedule (for the last machine) for the given steps. Each due date interval is built in sequence. For each
    interval, the steps are grouped by metal. Then, each group is sorted from smallest to largest step length, and
    lastly the groups themselves are sorted by step length, and then flattened into a sequence. The sequences for all
    intervals are then concatenated.
    :param permutations: Optionally, for each due date, you can specify a permutation for the groups of steps per metal.
    :return: A list that specifies the order of steps on the slab caster, from which the full schedule can be inferred.
    """

    seq = []

    # partition steps by due date
    due_classes = group_by(steps3_all, lambda s: s.run.due)

    if permutations is None:
        permutations = [None] * len(due_classes)
    else:
        assert None not in permutations

    for steps3_due, perm in zip(due_classes, permutations):
        # partition steps by metal
        # and then sort each subset from smallest to largest length
        steps3_metal: list[list[Step]] = [
            sorted(steps, key=lambda s: s.length)
            for steps in group_by(steps3_due, lambda s: s.run.metal)
        ]

        if perm is None:
            # sort subsets by (the last) step length
            steps3_metal.sort(key=lambda steps: steps[-1].length)
        else:
            # apply permutation (if it was specified)
            steps3_metal = apply_permutation(steps3_metal, perm)

        # flatten `steps3_metal` and add it to the sequence so far
        seq.extend([s for steps in steps3_metal for s in steps])

    return seq


problem = read_problem()

best_solution: Solution | None = None
best_cost: float | None = None

# create all possible permutations for the metal groups (in each due date interval)
# there are two intervals, so the total set of options if the product of all permutations
metal_permutations = list(itertools.permutations(range(3)))
print(f"we will consider {len(metal_permutations)**2} permutations")
for p1, p2 in itertools.product(metal_permutations, metal_permutations):
    # build sequence using the above function
    sequence = build_sequence(
        [s for s in problem.steps if s.phase() == 2],
        [p1, p2]
    )

    # create schedule from sequence and compute cost
    solution = Solution(problem)  # empty
    solution = greedy_partitioner.sequence_to_schedule(solution, sequence)
    cost = solution.cost()

    print(f"with permutations [{','.join([str(x) for x in p1])}] and [{','.join([str(x) for x in p2])}], cost = {cost}")

    # keep track of best solution
    if best_cost is None or cost < best_cost:
        best_solution = solution
        best_cost = cost

print(best_cost)
write_solution(best_solution, "greedy_solution.csv")
