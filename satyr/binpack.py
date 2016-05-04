from __future__ import absolute_import, division, print_function


def ff(items, targets):
    """First-Fit

    This is perhaps the simplest packing heuristic;
    it simply packs items in the next available bin.

    Complexity O(n^2)
    """
    bins = [(target, []) for target in targets]
    skip = []

    for item in items:
        for target, content in bins:
            if item <= (target - sum(content)):
                content.append(item)
                break
        else:
            skip.append(item)
    return bins, skip


def ffd(items, targets, key=lambda x: x):
    """First-Fit Decreasing

    This is perhaps the simplest packing heuristic;
    it simply packs items in the next available bin.

    This algorithm differs only from Next-Fit Decreasing
    in having a 'sort'; that is, the items are pre-sorted
    (largest to smallest).

    Complexity O(n^2)
    """
    items = sorted(items, key=key, reverse=True)
    return ff(items, targets)


def mr(items, targets):
    """Max-Rest

    Complexity O(n^2)
    """
    bins = [(target, []) for target in targets]
    skip = []

    for item in items:
        capacities = [(content, target - sum(content))
                      for target, content in bins]
        content, capacity = max(capacities, key=operator.itemgetter(1))
        if item <= capacity:
            content.append(item)
        else:
            skip.append(item)
    return bins, skip


def mrpq(items, targets):
    """Max-Rest Priority Queue

    Complexity O(n*log(n))
    """
    raise NotImplementedError()


def bf(items, targets):
    """Best-Fit

    Complexity O(n^2)
    """
    bins = [(target, []) for target in targets]
    skip = []

    for item in items:
        fits = []
        for target, content in bins:
            capacity = target - sum(content)
            if item <= capacity:
                fits.append((content, capacity - item))

        if len(fits):
            content, _ = min(fits, key=operator.itemgetter(1))
            content.append(item)
        else:
            skip.append(item)
    return bins, skip


def bfd(items, targets, key=lambda x: x):
    """Best-Fit Decreasing

    Complexity O(n^2)
    """
    items = sorted(items, key=key, reverse=True)
    return bf(items, targets)


def bfh(items, targets):
    """Best-Fit-Heap

    Slightly Improved Complexity
    """
    raise NotImplementedError()
