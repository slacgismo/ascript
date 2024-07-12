import marimo

__generated_with = "0.6.16"
app = marimo.App()


@app.cell
def __(mo, np):
    S = [1.0,0,0,0.1] # node supply capacity (MW)
    D = [0,0.1,0.2,0.1] # node demand (MW)
    R = [0.5,0.6,0.7] # line resistances (Ohm)
    G = [[0,1],[1,2],[1,3]] # graph of network

    M = len(G) # number of lines
    N = len(S) # number of nodes

    mo.stop(len(R)!=M,"incorrect number of line resistances")
    mo.stop(len(D)!=N,"incorrect number of demands")
    mo.stop(min(min(G))!=0 or max(max(G))!=N-1,"graph contains invalid nodes")

    A = np.zeros((N,N)) # admittance matrix
    for n,tf in enumerate(G):
        A[tf[0],tf[1]] = A[tf[1],tf[0]] = 1/R[n]
    return A, D, G, M, N, R, S, n, tf


@app.cell
def __(A):
    A
    return


@app.cell
def __(A, M, N, cp):
    f = cp.Variable(M) # line flows
    v = cp.Variable(N) # node voltages

    objective = cp.Minimize(v*A*v)
    constraints = [
        f == A*v
    ]
    return constraints, f, objective, v


@app.cell
def __():
    import marimo as mo
    import cvxpy as cp
    import numpy as np
    return cp, mo, np


if __name__ == "__main__":
    app.run()
