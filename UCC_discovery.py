import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', 
                    default='satellites.csv',
                    help='specify the dataset to be used')
arguments = parser.parse_args()

def get_pli_from(column):
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

def apriori(r):
    k = 0
    E = []
    F = []
    print(len(r.columns))
    E.append([[[i], get_pli_from(r.iloc[:,i])] for i in range(len(r.columns))])
    F.insert(k, prune(E[k]))

    # LOGGER
    # print(f"E{k}: ")
    # print(E[k])
    # print(f"F{k}: ")
    # print(F[k], end="\n\n")

    while (F[k]):
        E.insert(k+1, candidates(F[k]))
        F.insert(k+1, prune(E[k+1]))
        k += 1
        
        # LOGGER
        # print(f"E{k}: ")
        # print(E[k])
        # print(f"F{k}: ")
        # print(F[k], end="\n\n")

    result = []
    for j in range(k):
        result += [x for x in E[j] if x not in F[j]]
    return result

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

def prune(E):
    F = []
    for e in E:
        cols = e[0]
        pli = e[1]

        if any(pli.values()):
            F.append([cols, pli])
    return F

print(arguments.dataset)
    
data = pd.read_csv(arguments.dataset, header=None, dtype = str)
uccs = apriori(data)
print("UCCs found:")
print(list(map(lambda x: x[0], uccs)))