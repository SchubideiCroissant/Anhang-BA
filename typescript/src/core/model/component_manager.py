from typing import List, Optional
from .component import Component, Type
class ComponentManager:
    # Verwaltet alle Component-Instanzen zentral

    # Singleton-Registry für Component-Instanzen
    _instance: Optional["ComponentManager"] = None

    def __init__(self):
        if ComponentManager._instance is not None:
            raise RuntimeError("Bitte ComponentManager.get_instance() verwenden!")
        self._components: List[Component] = []
    
    @classmethod
    def get_instance(cls) -> "ComponentManager":
        if cls._instance is None:
            cls._instance = ComponentManager()
        return cls._instance

    def add(self, comp: Component):
        self._components.append(comp)

    def get_all(self) -> List[Component]:
        return list(self._components)

    def get_by_name(self, name: str) -> Optional[Component]:
        for comp in self._components:
            if comp.name == name:
                return comp
        return None

    def remove_by_name(self, name: str) -> bool:
        comp = self.get_by_name(name)
        if comp:
            self._components.remove(comp)
            return True
        return False
    
    def get_by_type(self, ctype: Type) -> List[Component]:
        return [comp for comp in self._components if comp.ctype == ctype]

    def __repr__(self) -> str:
        return f"ComponentManager({[c.name for c in self._components]})"

    def ask_for_type(self) -> Type:
        print("Wähle den Typ:")
        for t in Type:
            print(f"{t.value}: {t.name}")
        choice = int(input(">> "))
        try:
            return Type(choice)
        except ValueError:
            print("Ungültige Auswahl!")
            return self.ask_for_type()

    def get_stats_data(self) -> List[dict]:
        """Gibt eine Liste von Dicts zurück: [{'type': 'YY', 'count': 10}, ...]"""
        stats = {}
        count = 0
        for comp in self._components:
            type_name = comp.ctype.name 
            if type_name in stats:
                stats[type_name] = stats[type_name] + 1
            else:
                stats[type_name] = 1 # neuer bisher ungezählter Type
            count +=1
        # Umwandeln für Chart
        return [{"type": t, "count": c} for t, c in stats.items()]

    def clear(self):
        # Resetten
        self._components = []

    def run_cli(self):
        manager = ComponentManager.get_instance()

        while True:
            print("\nWähle eine Option:")
            print("0: Get all components")
            print("1: Filter by Type")
            print("2: Get by name")
            print("3: Add component")
            print("4: Remove by name")
            print("9: Exit")

            choice = input(">> ")

            if choice == "0":
                comps = manager.get_all()
                print("Components:", [c.name for c in comps])

            elif choice == "1":
                ctype = self.ask_for_type()
                filtered_comps = manager.get_by_type(ctype)
                
                print(f"{len(filtered_comps)} {ctype}:", [c.name for c in filtered_comps])

            elif choice == "2":
                name = input("Name eingeben: ")
                comp = manager.get_by_name(name)
                if comp:
                    print("Gefunden:", comp)
                else:
                    print("Kein Component mit diesem Namen.")
            
            elif choice == "3":
                # Übernimmt noch nicht in andere Struktur
                name = input("Name für neuen Component: ")
                ctype = self.ask_for_type()
                comp = Component(name, ctype)
                manager.add(comp)
                print("Hinzugefügt:", comp)

            elif choice == "4":
                # Übernimmt noch nicht in andere Struktur
                name = input("Name eingeben: ")
                if manager.remove_by_name(name):
                    print("Entfernt:", name)
                else:
                    print("Kein Component gefunden.")

            elif choice == "9":
                print("Beende CLI.")
                break

            else:
                print("Ungültige Eingabe.")


    