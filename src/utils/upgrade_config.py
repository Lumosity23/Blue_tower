import json
import os

from settings import Settings
from utils.path import resource_path as rp


def save_entity_upgrade(name: str, raw_data: tuple) -> None:
    """
    Sauvegarde la config d'upgrade d'une entité dans le JSON de schéma.

    Format attendu pour chaque item de raw_data :
        ("Label", "attr_name", max_value, price_value, rate_percent)

    Exemple :
        save_entity_upgrade("PLAYER", [
            ("Damage",   "damage",   100,  200, 10),
            ("Velocity", "velocity", 1000, 300,  5),
        ])

    Le JSON résultant stocke max/price/rate directement — les entités
    n'ont plus besoin d'attributs max_dm / price_dm etc.
    """
    st = Settings()
    filename = rp(st.UPGRADE_SCHEMA_PATH)

    data = {}
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}

    new_schema = []
    for item in raw_data:
        label, attr, max_val, price, rate = item
        new_schema.append(
            {
                "label": label,  # Nom affiché dans l'UI
                "attr": attr,  # Attribut lu/écrit sur l'entité
                "max": max_val,  # Valeur plafond (int/float)
                "price": price,  # Coût de l'upgrade
                "rate": rate,  # Pourcentage d'augmentation par upgrade
            }
        )

    data[name] = new_schema

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"⚙️  UPGRADE Auto-Config : {name} mis à jour ({len(new_schema)} upgrades).")
