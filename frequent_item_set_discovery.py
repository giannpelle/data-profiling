def apriori(B, T, s_min):
    E = []
    F = []
    k = 0
    E.insert(k, list(map(lambda x: [x], B)))
    F.insert(k, prune(E[k], T, s_min))
    while (F[k]):
        E.insert(k+1, candidates(F[k]))
        F.insert(k+1, prune(E[k+1], T, s_min))
        k += 1
    
    flat_list = [item for sublist in F for item in sublist]
    return flat_list


def candidates(F):
    E = []
    for f1 in F:
        for f2 in F:
            if f1[:-1] == f2[:-1] and f2[-1] > f1[-1]:
                # canonical code word generation
                f = f1 + [f2[-1]]
                
                # infrequent item sets upward closed
                should_append = True
                for f3 in f:
                    f_subset = [x for x in f if x != f3]
                    if f_subset not in F:
                        should_append = False
                        break

                if should_append:
                    E.append(f)
    return E
                

def prune(E, T, s_min):
    s = {}
    for e in E:
        e_index = "".join(e)
        s[e_index] = 0
    
    for t in T:
        for e in E:
            if all(item in t for item in e):
                e_index = "".join(e)
                s[e_index] += 1

    F = []
    for e in E:
        e_index = "".join(e)
        if s[e_index] >= s_min:
            F.append(e)
    return F
        

B = ["a", "b", "c", "d", "e"]
T = [["a", "d", "e"], ["b", "c", "d"], ["a", "c", "e"], ["a", "c", "d", "e"], ["a", "e"], ["a", "c", "d"], ["b", "c"], ["a", "c", "d", "e"], ["b", "c", "e"], ["a", "d", "e"]]
s_min = 3

print(apriori(B, T, s_min))