# Fonction pour lire les données à partir d'un fichier texte
def read_input_file(file_path):
    """
    Lit les données d'un fichier texte pour créer une liste de photos.
    Chaque photo est représentée comme un dictionnaire contenant son ID, son orientation, et ses tags.

    :param file_path: Chemin vers le fichier d'entrée.
    :return: Liste de photos, chaque photo étant un dictionnaire.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Nombre de photos dans le fichier
    n_photos = int(lines[0].strip())
    photos = []

    # Lecture de chaque photo (ID, orientation, et tags)
    for i in range(1, n_photos + 1):
        parts = lines[i].strip().split()
        orientation = parts[0]  # Orientation : 'H' ou 'V'
        tags = set(parts[2:])  # Ensemble des tags associés à la photo
        photos.append({'id': i - 1, 'orientation': orientation, 'tags': tags})

    return photos

def read_solution_file(file_path):
    """
    Lit le fichier de solution pour extraire l'ordre des diapositives.

    :param file_path: Chemin vers le fichier de solution.
    :return: Liste des diapositives.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Lire le nombre de diapositives
    num_slides = int(lines[0].strip())
    slides = []

    # Lire chaque diapositive
    for line in lines[1:num_slides + 1]:
        slides.append(tuple(map(int, line.strip().split())))

    return slides


def verify_solution(photos, slides):
    """
    Vérifie si une solution est valide et calcule son score total.

    :param photos: Liste des photos (tags, orientation, etc.).
    :param slides: Liste des diapositives (issues du fichier solution).
    :return: Tuple (is_valid, total_score).
    """
    used_photos = set()
    tags_by_slide = []

    # Construire les tags pour chaque diapositive
    for slide in slides:
        slide_tags = set()
        for photo_id in slide:
            if photo_id in used_photos:
                print(f"Erreur : La photo {photo_id} est utilisée plus d'une fois.")
                return False, 0
            used_photos.add(photo_id)
            slide_tags.update(photos[photo_id]['tags'])
        tags_by_slide.append(slide_tags)

    # Vérifier que toutes les photos utilisées sont valides
    if len(used_photos) > len(photos):
        print("Erreur : Plus de photos utilisées que disponible.")
        return False, 0

    # Calculer le score total
    total_score = 0
    for i in range(len(tags_by_slide) - 1):
        score = transition_score(tags_by_slide[i], tags_by_slide[i + 1])
        total_score += score

    return True, total_score


def transition_score(tags1, tags2):
    """
    Calcule le score d'intérêt entre deux ensembles de tags.

    :param tags1: Ensemble de tags de la première diapositive.
    :param tags2: Ensemble de tags de la seconde diapositive.
    :return: Score d'intérêt.
    """
    common_tags = tags1 & tags2
    only_in_1 = tags1 - tags2
    only_in_2 = tags2 - tags1
    return min(len(common_tags), len(only_in_1), len(only_in_2))


# Lecture des photos depuis le fichier d'entrée
photos = read_input_file("data/PetPics-20.txt")  # Remplacez par le fichier d'entrée utilisé

# Lecture de la solution depuis le fichier slideshow.sol
solution_slides = read_solution_file("slideshow.sol")

# Vérifier la solution
is_valid, total_score = verify_solution(photos, solution_slides)

# Afficher les résultats de la vérification
if is_valid:
    print(f"La solution est valide. Score total : {total_score}")
else:
    print("La solution est invalide.")