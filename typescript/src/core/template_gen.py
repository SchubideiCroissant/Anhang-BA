#import os
#from enum import Enum
#from typing import List, Optional
import pandas as pd
import csv
import json

from core.model.component import Type, Component
from core.model.component_manager import ComponentManager

class TemplateGenerator:
    """
    Bekommt eine Model.csv die von Mimic erstellt wurde,
    mithilfe von der SIO-Tabelle auto-generated es die CSV Komponente mit SIO Verbindungen.

    """
    def load_config(self,configpath):
        with open(configpath, "r", encoding="utf-8") as f:
            return json.load(f)
    def filter_groups_by_type(self, groups, t: Type):
        key = t.name  # z. B. Type.YY -> "YY"
        return groups.get(key, {})

    def print_config_info(self,config):
        for block in config:
            name = block["name"]           # z. B. "YY"
            aliases = block["aliases"]     # Liste z. B. ["OU1", "FB0", "FB1"]

            print(f"FieldType {name}:")
            for idx, alias in enumerate(aliases):
                print(f"  rest[{idx}] -> {alias}")

    def load_open_line(self,filepath):
        df = pd.read_csv(filepath, sep=",", engine="python", encoding="utf-8", header=None)
        open_line = df.iloc[0].tolist()
        fixe = open_line[:3]
        rest = open_line[3:]
        #print("Anzahl IOS :",len(rest))
        return fixe + rest

    def generate_component_lines(self, groups, configpath, node, area, filepath, out_filepath,
                                 type, data_type = None, check_alias=None):

        #manager = ComponentManager.get_instance()
        open_line = self.load_open_line(filepath)
        count = 0
        config = self.load_config(configpath)

        aliases = config.get("aliases", [])

        """
        if config.get("name") == type.name:
            
        else:
            print(f"Warnung: Typ in Config ({config.get('name')}) stimmt nicht mit gewähltem Typ ({type.name}) überein.")
            return f"Warnung: Typ in Config ({config.get('name')}) stimmt nicht mit gewähltem Typ ({type.name}) überein."
        """
        if not aliases:
            print(f"Keine Aliases für {type.name} in Config gefunden.")
            return f"Keine Aliases für {type.name} in Config gefunden."

        rows = []

        # Über Variablen im Subset
        inc_exk = type in (Type.YF, Type.YT, Type.YL, Type.YP) # inklusive Prüfung

        for var, suffix_dict in groups.items():

            # Fall 1: YF/YT/YL/YP
            if inc_exk:
                if not any(suf in suffix_dict for suf in aliases):
                    continue  # mind. ein Alias, inklusiv, es müssen die mit Protect mitgenommen werden

                # INT/REAL Unterscheidung
                if data_type is not None:
                    if check_alias:
                        entry = suffix_dict.get(check_alias)
                        if not entry or entry.get("BT") != data_type:
                            continue

            # Fall 2: Normale Typen
            else:
                if set(aliases) != set(suffix_dict):
                    continue  # exakte Übereinstimmung nicht erreicht -> überspringen

            # Gemeinsamer Teil: gültiger Eintrag
            line = [node, area, var]
            for suf in aliases:
                line.append(f"{node}/{var}_{suf}")
            rows.append(line)
            count += 1

        # Schreiben in CSV
        with open(out_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(open_line)
            writer.writerows(rows)

        return f"Befülltes Template: {out_filepath}, {count} Komponenten erstellt"
        # return out_filepath




    



