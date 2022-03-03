def inclusions(V, U, B):
    # input: [R], [r], [unary INDs]
    rhs = {}
    for A in U:
        rhs[str(A)] = U
    for v in V:
        for A in [A_b for v_b, A_b in B if v_b == v]:
            c = [C for v_c, C in B if v_c == v]
            rhs[str(A)] = [x for x in rhs[str(A)] if x in c]
    I = []
    for A in U:
        for B in rhs[str(A)]:
            I.append((A, B))
    return I

V = [1, 2, 3, 4, 6, 7, 9]
U = [0, 2, 4, 6, 10]
B = [(1, 0), (2, 0), (3, 2), (4, 2), (1, 4), (2, 4), (4, 4), (7, 4), (3, 6), (4, 6), (6, 6), (9, 6), (1, 10), (2, 10), (4, 10), (7, 10), (9, 10)]

print(inclusions(V, U, B))