import webview
from pathlib import Path
import pandas as pd
import os
import sys

from core.variable_parser import *
from core.template_gen import TemplateGenerator
from core.model.component import Type, Component
from core.model.component_manager import ComponentManager
from core.schema_manager import SchemaManager

import random

class Controller:
    def __init__(self):
        self.files={"profibus": None, "config1": None, "config2": None, "config3": None} # FM-2, ..
        self.directories = {"input": None, "output": None} # FM-3, FM-4
        #self.directories.items[0] = 1
        self.groups = None # Data Structure
        self.tg = TemplateGenerator()
        self.vp = VariableParser()
         
    # FM-9
    def template_generator(self, mimic_file, schema_file, node_name, area_name, type_name, data_type=None, var_name=None):
        if(self.groups is None):
            return "Datenstruktur wurde noch nicht erzeugt"
        m_filepath = os.path.join(self.directories.get("input"), mimic_file)
        print("Mimic File", m_filepath)

        schema_name, variant_name = schema_file.split('|')
        s_manager = SchemaManager("schemas")
        schema_path = s_manager._schema_file(schema_name, variant_name).resolve() # Absoluter Pfad
        print("Schema File", schema_path)

        print("Node-Name:", node_name)
        print("Area-Name", area_name)

        basename = mimic_file.split(".")[0] 
        print("Mimic Basename", basename)
        selected_type = Type[type_name] # String in Type-Type umwandeln
        print(selected_type)

        if data_type and var_name:
            print(f"Erweiterte Sortierung aktiv: Typ {data_type} für Variable {var_name}")

        #out_filepath = os.path.join(basepath,self.directories.get("output"),f"{basename}_{typename}_out.csv")
        m_out_filepath = os.path.join(self.directories.get("output"), f"{basename}_{type_name}_out.csv")

        
        subset = self.tg.filter_groups_by_type(self.groups, selected_type) # Nach Gerät sortieren
        
        return self.tg.generate_component_lines(subset, schema_path, node_name,
                                  area_name,m_filepath, m_out_filepath,selected_type ,data_type, var_name)

                                  
    # Backend Test
    def return_number(self):
        return random.random()
    
    # returns all files in a directory
    def get_directory_files(self, path_str):
        pfad = Path(path_str)
        files = []
        for datei in pfad.glob("*.*"):
            print(datei)
            files.append(datei)
        return files
    
    # Verzeichnis auswählen (Dialog) und Ordnerpfad zurückbekommen
    def set_directory(self, key):
        folder = webview.windows[0].create_file_dialog(webview.FileDialog.FOLDER)
        if folder:
            self.directories[key] = folder[0]
            print(f"{key} directory set to:", folder[0])

            self.get_directory_files(folder[0])
            #self.files("profibus") = 3
            return folder[0]
        else:
            return None    

    def get_input_files(self):
        path = self.directories.get("input")
        if not path:
            print("Fehler: Input-Verzeichnis ist noch nicht gesetzt!")
            return []

        files = self.get_directory_files(path)
        return [f.name if hasattr(f, 'name') else str(f) for f in files]

    # Datei auswählen (Dialog) und Dateipfad zurückbekommen
    def set_file(self, key:str):
        """
        file_types = (
        'Textdateien (*.txt)',
        'CSV-Dateien (*.csv)',
        'Alle Dateien (*.*)'
        )
        , file_types=file_types
        """

        result = window.create_file_dialog(
        webview.FileDialog.OPEN, allow_multiple=False)

        if result and len(result) > 0:
            file_path = result[0]
            self.files[key] = file_path
            print(f"Key: {key}: Ausgewählte Datei:{file_path}")
            return file_path
        else:
            print("Keine Datei ausgewählt")
            return None

    # FM-8
    def generate_datastructure(self):
        filename = self.files.get("profibus")
        
        if not filename:
            return "Profibus Datei nicht gesetzt!"

        try:
            self.groups = self.vp.sort_groups(self.vp.create_ds(filename))
            output = self.vp.load_components_from_groups(self.groups) # um Funktionen vom Component Manager auszuführen
        except Exception as e:
            return f"Fehler beim Erstellen der Datenstruktur: {e}"

        return output

    # Schema-Manager: FM-5,FM-6, FM-7
    def create_schema(self, name: str, variant: str, aliases: list):
        s = SchemaManager("schemas")
        data = {
            "name": name,
            "aliases": aliases
        }
        s = s.save(name, variant, data)
        print(f"Speichern von {name}:{variant} ... ")
        return s


    def list_schemas(self):
        s = SchemaManager("schemas")
        return s.list_schemas()

    def list_schema_variants(self, schema_name: str):
        s = SchemaManager("schemas")
        return s.list_variants(schema_name)

    def load_schema(self, schema_name: str, variant: str):
        s = SchemaManager("schemas")
        return s.load(schema_name, variant)
    
    def delete_schema_variant(self, schema_name:str, variant:str):
        s = SchemaManager("schemas") 
        return s.delete_variant(schema_name, variant)

    def delete_schema(self, schema_name: str):
        s = SchemaManager("schemas") 
        try:
            return s.delete_schema(schema_name)
        except Exception as e:
            return f"Fehler beim Löschen des Schemas: {e}"

    def get_all_variants_for_ui(self):
        schemas = self.list_schemas()
        all_entries = []

        for s_name in schemas:
            variants = self.list_schema_variants(s_name)
            print(f"Verfügbare Schemata: {variants}")
            for v in variants:
                all_entries.append({"schema": s_name, "variant": v})
        
        return all_entries

    def get_component_types(self):
        return [t.name for t in Type if t != Type.UNKNOWN]

    # FK-1, FK-2
    def get_component_stats(self):
        manager = ComponentManager.get_instance()
        return manager.get_stats_data()

class Api:
    backend = Controller() # verfügbar für Typescript Zugriff
    def on_window_closed(self):
        print("Fenster wurde geschlossen")

# Build Helfer
def get_url():
    # Prüft, ob das Programm als PyInstaller-EXE läuft
    if hasattr(sys, '_MEIPASS'):
        # Pfad zur index.html innerhalb der EXE (genannt "ui")
        return os.path.join(sys._MEIPASS, 'ui', 'index.html')
    
    # Testumgebung
    return "http://localhost:5173"

if __name__ == "__main__":

    api = Api()

    window = webview.create_window("Simulation Tool", url=get_url(),js_api=api, shadow=True)
    # Dist: ../dist/index.html Dev: http://localhost:5173 


    def handle_closing():
        api.on_window_closed()

    window.events.closing += handle_closing
    webview.start()
    #debug=True
