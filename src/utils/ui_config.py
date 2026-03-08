import json
import os
from settings import Settings


def save_entity_schema( name, raw_data: tuple ):

        st = Settings()

        # On le chemin vers le ficher de config
        filename = st.UI_SCHEMA_PATH

        # Charger l'existant
        data = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f: data = json.load(f)
            except: data = {}

        new_schema = []
        for item in raw_data:
            # On extrait la clé (ex: "BAR") et le label
            ui_key, label, *mapping_values = item
            ui_key = ui_key.upper() # Sécurité : accepte "bar" ou "BAR"

            if ui_key in st.REFERENT:
                tag, ui_class, keys = st.REFERENT[ui_key]

                new_schema.append({
                    "type": tag,
                    "ui_class": ui_class,
                    "label": label,
                    "mapping": dict(zip(keys, mapping_values))
                })

        # Mise à jour et sauvegarde
        data[name] = new_schema
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        # Petit feedback discret dans la console au lancement
        print(f"⚙️  UI Auto-Config : {name} mise à jour.")