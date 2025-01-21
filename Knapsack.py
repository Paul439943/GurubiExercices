import numpy as np
import gurobipy as gp
from gurobipy import GRB

def generate_knapsack(num_items):
    # Fixer une graine pour la reproductibilité
    rng = np.random.default_rng(seed=0)
    # Valeurs et poids des objets
    values = rng.uniform(low=1, high=25, size=num_items)
    weights = rng.uniform(low=5, high=100, size=num_items)
    # Capacité du sac à dos
    capacity = 0.7 * weights.sum()

    return values, weights, capacity

def solve_knapsack_model(values, weights, capacity):
    num_items = len(values)

    # Conversion des tableaux numpy en dictionnaires pour Gurobi
    values_dict = {i: values[i] for i in range(num_items)}
    weights_dict = {i: weights[i] for i in range(num_items)}

    # Création de l'environnement et du modèle
    with gp.Env() as env:
        with gp.Model(name="knapsack", env=env) as model:
            # Définir les variables de décision (0 ou 1)
            x = model.addVars(num_items, vtype=GRB.BINARY, name="x")

            # Définir la fonction objectif (maximiser la valeur totale)
            model.setObjective(gp.quicksum(values_dict[i] * x[i] for i in range(num_items)), GRB.MAXIMIZE)

            # Ajouter la contrainte de capacité
            model.addConstr(gp.quicksum(weights_dict[i] * x[i] for i in range(num_items)) <= capacity, name="capacity")

            # Optimiser le modèle
            model.optimize()

            # Afficher les résultats
            if model.status == GRB.OPTIMAL:
                print("Valeur optimale:", model.objVal)
                #print("Objets sélectionnés:")
                #for i in range(num_items):
                    #if x[i].X > 0.5:  # Vérifie si l'objet est sélectionné
                        #print(f"  Objet {i}: valeur = {values_dict[i]}, poids = {weights_dict[i]}")

# Générer les données pour 10 000 objets
data = generate_knapsack(10000)
# Résoudre le problème
solve_knapsack_model(*data)
