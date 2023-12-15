import itertools


def all_unique(xs) -> bool:
    """Returns whether all elements in `xs` are unique."""
    seen = set()
    for x in xs:
        if x in seen: return False
        seen.add(x)
    return True


def apply_permutation(xs, perm):
    """
    Permute the list `xs` according to `perm`. That is, return a list `ys` where `ys[i] = xs[perm[i]]` for each `i`.
    """
    return [xs[i] for i in perm]


def compute_combinations(n: int, k: int):
    """
    Returns all possible 'combinations' of length n, where each value is an integer between 1 and k.
    For example, `combinations(2,3)` gives [[1,1], [1,2], [1,3], [2,1], [2,2], [2,3], [3,1], [3,2], [3,3]].
    """
    return itertools.product(range(1, k+1), repeat=n)


def group_by(xs, selector):
    """
    Partitions the elements of `xs` with respect to a key. For a given element, the key is found by applying `selector`
    on that element. The groups are sorted by the value of the key.
    :return: a sequence of sequences (not a list)
    """
    xs = sorted(xs, key=selector)
    for key, group in itertools.groupby(xs, key=selector):
        yield group  # of type generator


def list_group_by(xs, selector):
    """
    Same as `group_by`, but returns a list of lists instead of a sequence.
    """
    return [list(ys) for ys in group_by(xs, selector)]
