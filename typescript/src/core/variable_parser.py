import pandas as pd
import re
from .model.component import Type
from .model.component_manager import Component, ComponentManager
 
class VariableParser:

    def get_field_type(self, variable: str) -> str:
        m = re.search(r"Y([A-Z]{1,2})", variable.upper())
        if not m:
            return "Unknown"
        return m.group()

    def get_base_type(self, component: str) -> str:
        if not isinstance(component, str):
            return "Unknown"
        s = component.upper()
        for t in ["BOOL", "INT", "REAL", "WORD", "BYTE"]:
            if t in s:
                return t
        return "Unknown"

    def update_groups(self, groups, variable, suffix, comp, io):
        """Aktualisiere groups-Dict mit einer neuen Zeile aus der CSV"""
        base_type = self.get_base_type(comp)
        new_io = "WRITE" if (io =="IN") else "READ" # Mimic Anpassung
        fieldtype = self.get_field_type(variable)  # z.B. "YF", "YY", ...

        groups.setdefault(fieldtype, {}).setdefault(variable, {})

        comment =""
        if(new_io == "WRITE" ):
            if(base_type == "REAL" ):
                comment =  "%"
            elif(base_type == "INT" ):
                comment = "Integer"
            else: 
                comment = ""
        
        # Suffix-Eintrag aktualisieren/neu anlegen
        entry = {
            "BT": base_type,
            "IO": new_io,
            "C": comment
        }

        groups[fieldtype][variable][suffix] = entry

        return groups

    def is_full_groups(self, groups: dict) -> bool:
        return bool(groups) and all(
            isinstance(k, str) and (k == "Unknown" or re.fullmatch(r"Y[A-Z]{1,2}", k))
            for k in groups
        )
    def print_groups(self,groups):
        # Wenn die Keys wie typische FieldTypes aussehen (z. B. "YY", "YF", "YP")
        print(self.is_full_groups(groups ))
        if self.is_full_groups(groups):
            # Vollstruktur: FieldType -> Variable -> Suffix
            for ft, vars_dict in sorted(groups.items()):
                print(f"{ft}:")
                for var, suffix_dict in sorted(vars_dict.items()):
                    print(f"    {var}:")
                    for suf, info in sorted(suffix_dict.items()):
                        #print(f"    {suf}")
                        bt = info.get("BT", "?")
                        io = info.get("IO", "?")
                        comment = info.get("C", "?")
                        print(f"        {suf}: BaseType={bt}, IO={io}, Comment={comment}")
        else:
            # Subset: Variable -> Suffix
            for var, suffix_dict in sorted(groups.items()):
                print(f"{var}:")
                for suf, info in sorted(suffix_dict.items()):
                    bt = info.get("BT", "?")
                    io = info.get("IO", "?")
                    comment = info.get("C", "?")
                    print(f"    {suf}: BaseType={bt}, IO={io}, Comment={comment}")

    def sort_groups(self, groups: dict) -> dict:
        """Sortiert groups alphabetisch: erst FieldTypes, dann Variablen, dann Suffixe."""
        sorted_groups = {}
        for ft in sorted(groups.keys()):  # FieldTypes sortieren
            vars_dict = groups[ft]
            sorted_vars = {}
            for var in sorted(vars_dict.keys()):  # Variablen sortieren
                suffix_dict = vars_dict[var]
                # Suffixe sortieren
                sorted_suffixes = {suf: suffix_dict[suf] for suf in sorted(suffix_dict.keys())}
                sorted_vars[var] = sorted_suffixes
            sorted_groups[ft] = sorted_vars
        return sorted_groups


    def create_ds(self, filename):
        groups = {}
        df = pd.read_csv(filename, sep=",", engine="python", encoding="utf-8", quotechar='"')

        for v, comp, io in zip(df["Variable"], df["Component"], df["IO Type"]):
            if pd.isna(v):
                continue
            s = str(v).strip()
            if "_" in s:
                variable, suffix = s.split("_", 1) 
                #m = re.match(r"(\d+)([A-Z]+)", suffix) schwedt
                #num, text = m.groups()
            else:
                variable, suffix = s, ""
            variable.split()
            groups = self.update_groups(groups, variable, suffix, comp, io)
            #print(f"{variable} : {suffix}, BaseType={get_base_type(comp)} IO={io}")
        return groups


    def get_component_type(self, fieldtype: str) -> Type:
        """Wandelt den FieldType-String (z.B. 'YY') in den Enum Type um."""
        try:
            return Type[fieldtype.upper()]
        except KeyError:
            return Type.UNKNOWN

    def load_components_from_groups(self, groups: dict):
        """
        Durchläuft das 'groups'-Dictionary, erstellt Component-Instanzen 
        (Name und Type) und fügt sie dem ComponentManager hinzu.
        """
        manager = ComponentManager.get_instance()

        print("Starte Datenstruktur Aufbau")
        count = 0
        manager.clear()

        for ft, vars_dict in groups.items():

            c_type = self.get_component_type(ft)
            # Iteration über die Variable-Ebene
            for var_name in vars_dict.keys():
                
                new_component = Component(
                    name=var_name,
                    ctype=c_type,
                )
                print(f"{var_name} {c_type}")
                manager.add(new_component)
                count += 1
        
        return f"Datenstruktur erstellt. {count} Komponenten zum ComponentManager hinzugefügt."
        # {manager.get_all()}

    #if __name__ == "__main__":
        #main()
