import argparse
from numpy import s_
import pandas as pd
from functools import reduce

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', 
                    default='satellites.csv',
                    help='specify the dataset to be used')
arguments = parser.parse_args()

def get_pli_from_index(col_index, r):
    column = r.iloc[:,col_index]
    pli = {} # valore: [indexes]
    known_elements = []
    for index, value in enumerate(column):
        if value in known_elements:
            pli.get(known_elements.index(value)).append(index)
        else:
            pli.update({len(known_elements): [index]})
            known_elements.append(value)

    pli = dict(filter(lambda x: len(x[1]) > 1, pli.items()))
    return pli

def get_intersected_row_pairs(first_pli, second_pli):
    prob_table = {}
    for key, value in first_pli.items():
        for v in value:
            prob_table[v] = key

    row_pairs = {}
    for key, value in second_pli.items():
        for v in value:
            if v in prob_table:
                pair = ", ".join([str(key), str(prob_table[v])])
                if pair in row_pairs:
                    row_pairs.get(pair).append(v)
                else:
                    row_pairs.update({pair: [v]})

    row_pairs = dict(filter(lambda x: len(x[1]) > 1, row_pairs.items()))
    return row_pairs

def get_pli_from_indexes(col_indexes, r):
    pli = get_pli_from_index(col_indexes[0], r)
    for col_index in col_indexes:
        if col_index == col_indexes[0]:
            continue
        pli = get_intersected_row_pairs(pli, get_pli_from_index(col_index, r))
    return pli

def get_key_error_from_pli(pli):
    count = 0
    for group in pli.items():
        count += (len(group[1]) - 1)
    return count

def get_support_error_from_plis(first_pli, second_pli):
    c_sum = 0
    for _, c in first_pli.items():
        c_sum += len(c)

    max_sum = 0
    for _, f_items in first_pli.items():
        max = 1
        for _, s_items in second_pli.items():
            if all(item in f_items for item in s_items) and len(s_items) > max:
                max = len(s_items)
        max_sum += max

    return c_sum - max_sum
            

def apriori(r):
    k = 0
    E = []
    C = []
    F = []

    primary_keys = []
    s_min = int(len(r) * 0.10)
    
    E.append([[[i], get_pli_from_index(i, r)] for i in range(len(r.columns))])
    C.append({str(i): list(range(len(r.columns))) for i in range(len(r.columns))})
    F.insert(k, prune(E[k], C[k], r, primary_keys))

    # LOGGER
    # print("-" * 100)
    # print(f"E{k}: ")
    # print(E[k])
    # print(f"C{k}: ")
    # print(C[k])
    # print(f"F{k}: ")
    # print(F[k])
    # print("-" * 100)

    while (F[k]):
        print(f"Working on level: {k + 1}")
        E.insert(k+1, candidates(F[k]))
        C.insert(k+1, dependencies(E[k+1], C[k], s_min, r))
        F.insert(k+1, prune(E[k+1], C[k+1], r, primary_keys))
        k += 1
        
        # LOGGER
        # print("-" * 100)
        # print(f"E{k}: ")
        # print(E[k])
        # print(f"C{k}: ")
        # print(C[k])
        # print(f"F{k}: ")
        # print(F[k])
        # print("-" * 100)

def candidates(F):
    E = []
    for f1, p1 in F:
        for f2, p2 in F:
            if f1[:-1] == f2[:-1] and f2[-1] > f1[-1]:
                # canonical code word generation
                f = f1 + [f2[-1]]
                p = get_intersected_row_pairs(p1, p2)

                # UCCs are upward closed
                should_append = True
                for f3 in f:
                    f_subset = [x for x in f if x != f3]
                    if f_subset not in list(map(lambda x: x[0], F)):
                        should_append = False
                        break

                if should_append:
                    E.append([f, p])

    return E

def dependencies(E, C, s_min, r):
    C_plus = {}
    for e in E:
        X = e[0]
        pli = e[1]
        
        subsets = []
        for x in X:
            subsets.append([element for element in X if element != x])

        subsets_rhs_list = list(map(lambda subset: C["".join([str(x) for x in subset])], subsets))
        C_plus["".join([str(x) for x in X])] = [x for x in subsets_rhs_list[0] if all(x in subset for subset in subsets_rhs_list)]

    for e in E:
        X = e[0]
        pli = e[1]
        key_error_pli = get_key_error_from_pli(pli)
        for A in [x for x in X if x in C_plus["".join([str(x) for x in X])]]:
            plis = get_pli_from_indexes([x for x in X if x != A], r)
            key_error_plis = get_key_error_from_pli(plis)

            early_exit_flag = get_key_error_from_pli(plis) < s_min and get_key_error_from_pli(plis) - get_key_error_from_pli(pli) > s_min
            if early_exit_flag or get_support_error_from_plis(plis, pli) <= s_min:
                print(f"minimal FD: {[x for x in X if x != A]} -> {A}")
                C_plus["".join([str(x) for x in X])] = [x for x in C_plus["".join([str(x) for x in X])] if x != A]

                if key_error_pli == key_error_plis:
                    for B in [x for x in list(range(len(r.columns))) if x not in X]:
                        C_plus["".join([str(x) for x in X])] = [x for x in C_plus["".join([str(x) for x in X])] if x != B]

    return C_plus

def prune(E, C, r, primary_keys):
    F = E
    
    for e in E:
        X = e[0]
        pli = e[1]

        if not C["".join([str(x) for x in X])]:
            F = list(filter(lambda x: not (x[0] == X and x[1] == pli), F))
        if not get_pli_from_indexes(X, r):
            #slide 69
            print(f"{X} is a key")
            primary_keys.append(X)
            for A in [x for x in C["".join([str(x) for x in X])] if x not in X]:
                subsets = []
                for x in X:
                    subsets.append(sorted([element for element in X if element != x] + [A]))
                
                #FIX for early pruning of primary keys
                to_be_removed = []
                for subset in subsets: 
                    for pk in primary_keys:
                        if all(x in subset for x in pk):
                            to_be_removed.append(subset)
                subsets = [subset for subset in subsets if subset not in to_be_removed]
                #END FIX
                
                if all("".join([str(x) for x in subset]) in C for subset in subsets):
                    if all(A in C["".join([str(x) for x in subset])] for subset in subsets):
                        print(f"minimal FD: {X} -> {A}")

            F = list(filter(lambda x: not (x[0] == X and x[1] == pli), F))

    return F

data = pd.read_csv(arguments.dataset, dtype = str)
fds = apriori(data)

