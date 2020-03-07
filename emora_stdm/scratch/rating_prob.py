
ratings = {
    1: 97,
    2: 76,
    3: 86,
    4: 97,
    5: 181
}

def product(l):
    r = 1
    for e in l:
        r *= e
    return r

def avg(l):
    return sum(l) / len(l)

def update(l):
    i = 0
    carry = True
    while carry:
        carry = False
        i += 1
        last = l[-i]
        nxt = last + 1
        if nxt > 5:
            nxt = 1
            carry = True
        l[-i] = nxt
    return l

if __name__ == '__main__':

    probs = {s: n / sum(ratings.values()) for s, n in ratings.items()}

    ten = [1] * 5
    a = 0
    overall_prob = 0.0

    while a < 2.0:
        ten_p = [probs[e] for e in ten]
        p = product(ten_p)
        a = avg(ten)
        overall_prob += p
        ten = update(ten)

    print(overall_prob)




