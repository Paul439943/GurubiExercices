import gurobipy as gp
from gurobipy import GRB
import numpy as np

# 24 Hour Load Forecast (MW)
load_forecast = np.array([
    4, 4, 4, 4, 4, 4, 6, 6, 12, 12, 12, 12,
    12, 4, 4, 4, 4, 16, 16, 16, 16, 6.5, 6.5, 6.5,
])

# Solar energy forecast (MW)
solar_forecast = np.array([
    0, 0, 0, 0, 0, 0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.5,
    3.5, 2.5, 2.0, 1.5, 1.0, 0.5, 0, 0, 0, 0, 0, 0,
])

# Time intervals and thermal units
nTimeIntervals = len(load_forecast)
thermal_units = ["gen1", "gen2", "gen3"]
nThermalUnits = len(thermal_units)

# Thermal units' costs and startup/shutdown costs
thermal_units_cost, a, b, c, sup_cost, sdn_cost = gp.multidict(
    {
        "gen1": [5.0, 0.5, 1.0, 2, 1],
        "gen2": [5.0, 0.5, 0.5, 2, 1],
        "gen3": [5.0, 3.0, 2.0, 2, 1],
    }
)

# Thermal units operating limits
thermal_units_limits, pmin, pmax = gp.multidict(
    {"gen1": [1.5, 5.0], "gen2": [2.5, 10.0], "gen3": [1.0, 3.0]}
)

# Initial commitment status
thermal_units_dyn_data, init_status = gp.multidict(
    {"gen1": [0], "gen2": [0], "gen3": [0]}
)

# Convert dictionaries to arrays
pmin = np.array([pmin[g] for g in thermal_units])
pmax = np.array([pmax[g] for g in thermal_units])
init_status = np.array([init_status[g] for g in thermal_units])
a = np.array([a[g] for g in thermal_units])
b = np.array([b[g] for g in thermal_units])
c = np.array([c[g] for g in thermal_units])
sup_cost = np.array([sup_cost[g] for g in thermal_units])
sdn_cost = np.array([sdn_cost[g] for g in thermal_units])

# Initialize the model
with gp.Env() as env, gp.Model(env=env) as model:
    # Variables
    power = model.addMVar((nThermalUnits, nTimeIntervals), lb=0, name="power")
    startup = model.addMVar((nThermalUnits, nTimeIntervals), vtype=GRB.BINARY, name="startup")
    shutdown = model.addMVar((nThermalUnits, nTimeIntervals), vtype=GRB.BINARY, name="shutdown")
    commit = model.addMVar((nThermalUnits, nTimeIntervals), vtype=GRB.BINARY, name="commit")

    # Objective function
    quadratic_cost = gp.quicksum(
        c[g] * power[g, t] * power[g, t] for g in range(nThermalUnits) for t in range(nTimeIntervals)
    )
    linear_cost = gp.quicksum(
        b[g] * power[g, t] for g in range(nThermalUnits) for t in range(nTimeIntervals)
    )
    fixed_cost = gp.quicksum(
        a[g] * commit[g, t] for g in range(nThermalUnits) for t in range(nTimeIntervals)
    )
    startup_cost = gp.quicksum(
        sup_cost[g] * startup[g, t] for g in range(nThermalUnits) for t in range(nTimeIntervals)
    )
    shutdown_cost = gp.quicksum(
        sdn_cost[g] * shutdown[g, t] for g in range(nThermalUnits) for t in range(nTimeIntervals)
    )
    model.setObjective(quadratic_cost + linear_cost + fixed_cost + startup_cost + shutdown_cost, GRB.MINIMIZE)

    # Power balance
    model.addConstr(
        power.sum(axis=0) + solar_forecast == load_forecast,
        name="power_balance"
    )

    # Logical constraints
    for t in range(nTimeIntervals):
        if t == 0:
            model.addConstr(
                commit[:, t] - init_status == startup[:, t] - shutdown[:, t],
                name=f"logical_initial_{t}",
            )
        else:
            model.addConstr(
                commit[:, t] - commit[:, t - 1] == startup[:, t] - shutdown[:, t],
                name=f"logical_{t}",
            )
    model.addConstr(
        startup + shutdown <= 1,
        name="no_simultaneous_startup_shutdown",
    )

    # Indicator constraints for physical limits
    for g in range(nThermalUnits):
        for t in range(nTimeIntervals):
            model.addGenConstrIndicator(
                commit[g, t],
                True,
                power[g, t] >= pmin[g],
                name=f"min_power_{g}_{t}",
            )
            model.addGenConstrIndicator(
                commit[g, t],
                True,
                power[g, t] <= pmax[g],
                name=f"max_power_{g}_{t}",
            )
            model.addGenConstrIndicator(
                commit[g, t],
                False,
                power[g, t] == 0,
                name=f"zero_power_{g}_{t}",
            )

    # Optimize the model
    model.optimize()

    # Display results
    #if model.Status == GRB.OPTIMAL:
        #print(f"Optimal cost: {model.ObjVal:.2f}")
        #print("Power output:")
        #print(power.X)
        #print("Commitment status:")
        #print(commit.X)