import matplotlib.pyplot as plt
import io
import base64
from matplotlib.ticker import MaxNLocator

def plot_evolution_restaurations(labels, valeurs):
    """
    Diagramme en barres : évolution annuelle des restaurations
    - labels : liste de chaînes ('2022', '2023', ...)
    - valeurs : liste d'entiers (1, 2, 3, ...)
    """

    fig, ax = plt.subplots(figsize=(7, 4))

    # Diagramme en barres (catégories)
    ax.bar(labels, valeurs)

    # Titres et labels
    ax.set_title("Évolution annuelle des restaurations")
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de restaurations")

    # Axe Y : uniquement des entiers
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Mise en forme propre
    fig.tight_layout()

    # Conversion en image (base64) pour Flask
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)

    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
