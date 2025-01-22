import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Charger les données du fichier JSON
with open("data/portfolio-example.json", "r") as f:
    data = json.load(f)

# Extraire les données
n = data["num_assets"]
sigma = np.array(data["covariance"])
mu = np.array(data["expected_return"])
mu_0 = data["target_return"]
k = data["portfolio_max_size"]

# Créer le modèle Gurobi
with gp.Model("portfolio") as model:
    # Variables continues pour les investissements
    x = model.addVars(n, vtype=GRB.CONTINUOUS, name="x")
    # Variables binaires pour indiquer si un actif est inclus
    y = model.addVars(n, vtype=GRB.BINARY, name="y")

    # Définir la fonction objectif : Minimiser le risque (variance du portefeuille)
    risk = gp.quicksum(sigma[i, j] * x[i] * x[j] for i in range(n) for j in range(n))
    model.setObjective(risk, GRB.MINIMIZE)

    # Contrainte : Retour attendu doit dépasser le seuil minimum
    model.addConstr(gp.quicksum(mu[i] * x[i] for i in range(n)) >= mu_0, name="return")

    # Contrainte : La somme des investissements doit être égale à 1
    model.addConstr(gp.quicksum(x[i] for i in range(n)) == 1, name="budget")

    # Contrainte : Limiter le nombre maximal d'actifs dans le portefeuille
    model.addConstr(gp.quicksum(y[i] for i in range(n)) <= k, name="max_assets")

    # Contrainte : L'investissement dans un actif est nul si l'actif n'est pas sélectionné
    for i in range(n):
        model.addConstr(x[i] <= y[i], name=f"select_{i}")

    # Optimiser le modèle
    model.optimize()

    # Vérifier si une solution optimale a été trouvée
    if model.status == GRB.OPTIMAL:
        # Extraire les résultats
        portfolio = [x[i].X for i in range(n)]
        risk = model.ObjVal
        expected_return = sum(mu[i] * portfolio[i] for i in range(n))

        # Créer un DataFrame pour afficher les résultats
        #df = pd.DataFrame(
            #data=portfolio + [risk, expected_return],
            #index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
            #columns=["Portfolio"],
        #)
        #print(df)
    else:
        print("Aucune solution optimale n'a été trouvée.")