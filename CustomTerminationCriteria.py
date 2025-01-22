from functools import partial
import gurobipy as gp
from gurobipy import GRB
import time

class CallbackData:
    def __init__(self):
        self.last_gap_change_time = -GRB.INFINITY  # Temps du dernier changement significatif de gap
        self.last_gap = GRB.INFINITY  # Dernier MIPGap enregistré

def callback(model, where, *, cbdata):
    if where == GRB.Callback.MIP:
        # Nombre de solutions trouvées
        solution_count = model.cbGet(GRB.Callback.MIP_SOLCNT)
        if solution_count == 0:
            return  # Pas encore de solution, rien à faire

        # Temps écoulé depuis le début
        runtime = model.cbGet(GRB.Callback.RUNTIME)

        # Obtenir le MIPGap courant
        best_obj = model.cbGet(GRB.Callback.MIP_OBJBST)  # Meilleure solution trouvée
        bound_obj = model.cbGet(GRB.Callback.MIP_OBJBND)  # Meilleure borne
        if abs(best_obj) > 1e-6:  # Évite la division par zéro
            current_gap = abs(bound_obj - best_obj) / abs(best_obj)
        else:
            current_gap = float('inf')  # Si aucune solution n'a été trouvée

        # Si c'est la première solution trouvée, initialiser le temps
        if cbdata.last_gap == GRB.INFINITY:
            cbdata.last_gap_change_time = runtime
            cbdata.last_gap = current_gap
            return

        # Vérifier si le MIPGap a changé significativement
        gap_change = abs(cbdata.last_gap - current_gap)
        if gap_change > epsilon_to_compare_gap:
            # Mettre à jour les informations sur le dernier changement significatif
            cbdata.last_gap_change_time = runtime
            cbdata.last_gap = current_gap
        else:
            # Vérifier si le temps écoulé depuis le dernier changement dépasse la limite
            if runtime - cbdata.last_gap_change_time > time_from_best:
                print(f"Terminating: No significant gap improvement in {time_from_best} seconds.")
                model.terminate()  # Arrêter l'optimisation

# Charger le modèle
with gp.read("data/mkp.mps.bz2") as model:
    # Paramètres pour le callback
    time_from_best = 50  # Temps d'attente maximal après la dernière amélioration
    epsilon_to_compare_gap = 1e-4  # Seuil pour considérer un changement de gap significatif

    # Initialiser les données pour le callback
    callback_data = CallbackData()
    callback_func = partial(callback, cbdata=callback_data)

    # Lancer l'optimisation avec le callback
    model.optimize(callback_func)

    # Afficher les résultats si l'optimisation est terminée
    if model.status == GRB.OPTIMAL:
        print("Optimization complete. Solution found.")
    elif model.status == GRB.TIME_LIMIT:
        print("Time limit reached.")
    elif model.status == GRB.INTERRUPTED:
        print("Optimization was terminated by the callback.")
    else:
        print(f"Optimization ended with status {model.status}.")