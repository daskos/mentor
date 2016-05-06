from __future__ import absolute_import, division, print_function

import operator


def weight(items, **kwargs):
    if not len(kwargs):
        raise ValueError('Missing attribute for weighting items!')
    scaled = []
    for attr, weight in kwargs.items():
        values = [float(getattr(item, attr)) for item in items]
        try:
            s = sum(values)
            scaled.append([weight * (v / s) for v in values])
        except ZeroDivisionError:
            # s equals to zero, attr wont contribute
            scaled.append([0] * len(items))

    return map(sum, zip(*scaled))


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


def ffd(items, targets, **kwargs):
    """First-Fit Decreasing

    This is perhaps the simplest packing heuristic;
    it simply packs items in the next available bin.

    This algorithm differs only from Next-Fit Decreasing
    in having a 'sort'; that is, the items are pre-sorted
    (largest to smallest).

    Complexity O(n^2)
    """
    sizes = zip(items, weight(items, **kwargs))
    sizes = sorted(sizes, key=operator.itemgetter(1), reverse=True)
    items = map(operator.itemgetter(0), sizes)
    return ff(items, targets)


def mr(items, targets, **kwargs):
    """Max-Rest

    Complexity O(n^2)
    """
    bins = [(target, []) for target in targets]
    skip = []

    for item in items:
        capacities = [target - sum(content) for target, content in bins]
        weighted = weight(capacities, **kwargs)

        (target, content), capacity, _ = max(zip(bins, capacities, weighted),
                                             key=operator.itemgetter(2))
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


def bf(items, targets, **kwargs):
    """Best-Fit

    Complexity O(n^2)
    """
    bins = [(target, []) for target in targets]
    skip = []

    for item in items:
        containers = []
        capacities = []
        for target, content in bins:
            capacity = target - sum(content)
            if item <= capacity:
                containers.append(content)
                capacities.append(capacity - item)

        if len(capacities):
            weighted = zip(containers, weight(capacities, **kwargs))
            content, _ = min(weighted, key=operator.itemgetter(1))
            content.append(item)
        else:
            skip.append(item)
    return bins, skip


def bfd(items, targets, **kwargs):
    """Best-Fit Decreasing

    Complexity O(n^2)
    """
    sizes = zip(items, weight(items, **kwargs))
    sizes = sorted(sizes, key=operator.itemgetter(1), reverse=True)
    items = map(operator.itemgetter(0), sizes)
    return bf(items, targets, **kwargs)


def bfh(items, targets):
    """Best-Fit-Heap

    Slightly Improved Complexity
    """
    raise NotImplementedError()
