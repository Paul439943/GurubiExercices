import gurobipy as gp

parameters = {
    "OutputFlag": 0
}

with gp.Env(params=parameters) as env, gp.Model(env=env) as m:
    m.optimize()
print(gp.GRB.VERSION_MAJOR)