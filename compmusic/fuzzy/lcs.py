#taken from http://wordaligned.org/articles/longest-common-subsequence
#based on the algorithm proposed in http://dl.acm.org/citation.cfm?id=360861
#License: Unknown

import itertools

def lcs_lens(xs, ys):
    curr = list(itertools.repeat(0, 1 + len(ys)))
    for x in xs:
        prev = list(curr)
        for i, y in enumerate(ys):
            if x == y:
                curr[i + 1] = prev[i] + 1
            else:
                curr[i + 1] = max(curr[i], prev[i + 1])
    return curr

def lcs(xs, ys):
    nx, ny = len(xs), len(ys)
    if nx == 0:
        return []
    elif nx == 1:
        return [xs[0]] if xs[0] in ys else []
    else:
        i = nx // 2
        xb, xe = xs[:i], xs[i:]
        ll_b = lcs_lens(xb, ys)
        ll_e = lcs_lens(xe[::-1], ys[::-1])
        _, k = max((ll_b[j] + ll_e[ny - j], j)
                    for j in range(ny + 1))
        yb, ye = ys[:k], ys[k:]
        return lcs(xb, yb) + lcs(xe, ye)