from django import template
register = template.Library()


def insert_ellipse(lst, ellipse=0):
    '''Insert ellipse where it's not sequential

    An ellipse is represented by @ellipse.

    E.g.:
        [1, 2, 5] -> [1, 2, 0, 5]
        [1, 2, 4] -> [1, 2, 3, 4]

    The last example is that if only one step is missing, just add it instead
    of an ellipse.
    '''

    if len(lst) <= 1:
        return list(lst[:])
    gap = lst[1] - lst[0]
    if gap <= 1:
        return [lst[0]] + insert_ellipse(lst[1:], ellipse)
    elif gap == 2:
        return [lst[0], lst[0] + 1] + insert_ellipse(lst[1:], ellipse)
    else:
        return [lst[0], ellipse] + insert_ellipse(lst[1:], ellipse)

def pick_pages(num_pages, current):
    '''pick pages to display in the pager

    It's like: 1 ... (x-2) (x-1) (x) (x+1) (x+2) ... N.
    '''

    ret = []

    for p in range(current - 2, current):
        if p >= 1:
            ret.append(p)
    ret.append(current)
    for p in range(current + 1, current + 3):
        if p <= num_pages:
            ret.append(p)

    if ret[0] != 1:
        ret.insert(0, 1)
    if ret[-1] != num_pages:
        ret.append(num_pages)
    ret = insert_ellipse(ret)

    return ret
    
register.filter('pick_pages', pick_pages)    