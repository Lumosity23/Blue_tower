import json
import os
from settings import Settings
from utils.path import resource_path as rp


def save_entity_upgrade( name, raw_data: tuple ):

        st = Settings()

        # On le chemin vers le ficher de config
        filename = rp(st.UPGRADE_SCHEMA_PATH)

        # Charger l'existant
        data = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f: data = json.load(f)
            except: data = {}

        new_schema = []
        for item in raw_data:
            # On extrait la clé (ex: "BAR") et le label
            label, *mapping_values = item

            new_schema.append({
                "label": label,
                "mapping": dict(zip(st.REFERENT_UPGRADE, mapping_values))
            })

        # Mise à jour et sauvegarde
        data[name] = new_schema
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        # Petit feedback discret dans la console au lancement
        print(f"⚙️  UPGRADE Auto-Config : {name} mise à jour.")