from itertools import combinations
from gurobipy import Model, GRB, quicksum

def load_data(filename):
    with open(filename, "r") as f:
        n_photos = int(f.readline().strip())
        photos = []
        for i in range(n_photos):
            parts = f.readline().strip().split()
            orientation = parts[0]
            tags = set(parts[2:])
            photos.append((i, orientation, tags))
    return photos

def interest_score(tags1, tags2):
    common = len(tags1 & tags2)
    only_in_first = len(tags1 - tags2)
    only_in_second = len(tags2 - tags1)
    return min(common, only_in_first, only_in_second)

def create_model(photos):
    model = Model("Photo Slideshow")
    model.setParam('OutputFlag', 0)  # Suppress output

    # Separate horizontal and vertical photos
    horizontal_photos = [p for p in photos if p[1] == 'H']
    vertical_photos = [p for p in photos if p[1] == 'V']

    # Create all possible slides
    slides = []
    # Horizontal slides
    slides.extend([(p[0],) for p in horizontal_photos])
    # Vertical photo pair slides
    for v1, v2 in combinations(vertical_photos, 2):
        if v1[0] != v2[0]:
            slides.append((v1[0], v2[0]))

    # Decision variables
    x = model.addVars(len(slides), vtype=GRB.BINARY, name="slide_selection")

    # Constraint: Each photo used at most once
    photo_usage = {}
    for i, slide in enumerate(slides):
        for photo in slide:
            if photo not in photo_usage:
                photo_usage[photo] = []
            photo_usage[photo].append(i)

    for photo, slide_indices in photo_usage.items():
        model.addConstr(quicksum(x[i] for i in slide_indices) <= 1)

    # Compute total interest
    def compute_total_interest(selected_slide):
        total_interest = 0
        for i in range(len(selected_slide) - 1):
            tags1 = set().union(*(photos[p][2] for p in selected_slide[i]))
            tags2 = set().union(*(photos[p][2] for p in selected_slide[i+1]))
            total_interest += interest_score(tags1, tags2)
        return total_interest

    # Objective function: Maximize total interest
    def add_interest_constraints():
        total_interest = 0
        for i in range(len(slides)):
            for j in range(i+1, len(slides)):
                tags1 = set().union(*(photos[p][2] for p in slides[i]))
                tags2 = set().union(*(photos[p][2] for p in slides[j]))
                score = interest_score(tags1, tags2)
                # Big-M method to capture pairwise interest
                M = 1000  # Large constant
                total_interest += score * x[i] * x[j]
        return total_interest

    # Set objective
    model.setObjective(add_interest_constraints(), GRB.MAXIMIZE)

    # Solve the model
    model.optimize()

    # Afficher fonction objectif
    print(f"Objectif : {model.objVal}")

    # Extract selected slides
    selected_slides = [slides[i] for i in range(len(slides)) if x[i].X > 0.5]
    return selected_slides

def write_output(selected_slides, output_file):
    with open(output_file, "w") as f:
        f.write(f"{len(selected_slides)}\n")
        for slide in selected_slides:
            f.write(" ".join(map(str, slide)) + "\n")

def main():
    #input_file = 'data/trivial.txt'
    input_file = 'data/PetPics-20.txt'
    output_file = 'slideshow.sol'
    photos = load_data(input_file)
    selected_slides = create_model(photos)
    write_output(selected_slides, output_file)
    print(f"Number of slides: {len(selected_slides)}")
    for slide in selected_slides:
        print(slide)
    print()

if __name__ == "__main__":
    main()
