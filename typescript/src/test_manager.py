import pytest
from core.schema_manager import SchemaManager  
from core.variable_parser import VariableParser
from main import Controller
from pathlib import Path

# tmp path ist aus Path-Lib

@pytest.fixture
def manager(tmp_path):
    """Erstellt eine SchemaManager-Instanz in einem temporären Verzeichnis."""
    return SchemaManager(tmp_path)

@pytest.fixture
def sample_data():
    return {
        "name": "TestVariant",
        "aliases": ["Water","Earth", "Fire", "Air"]
    }

# Fixtures für Integrationstests
@pytest.fixture
def test_csv(tmp_path):
    # Aus Ventil mit Variablen: ESwitch, Control, STA
    csv_file = tmp_path / "profibus.csv"
    csv_file.write_text(
        "Variable,Component,IO Type\n"
        "1337YY001_ESwitch,M1_IN_BOOL0_0,OUT\n"
        "1337YY001_Control,M1_IN_BOOL0_1,OUT\n"
        "-, -, -\n"
        "1337YY001_STA,M0_OUT_WORD0,IN\n"
        "filler, filler, filler\n"
        "unvollstaendiger, Eintrag, folgt\n"
        "1337YY005_Control,M1_IN_BOOL0_1,OUT\n"
        
    )
    return csv_file

@pytest.fixture
def test_template(tmp_path):
    # CSV-Datei erzeugen
    template_file = tmp_path / "template.csv"
    template_file.write_text(
        "NODE,AREA,MODEL,PARAM1, PARAM2, PARAM3\n"
    )
    return template_file

@pytest.fixture
def emg_data():
    return {
        "name": "emgValve",
        "aliases": ["ESwitch","Control","STA"]
    }

# -- Tests --
# Schemata
def test_save_and_load(manager, sample_data):
    result = manager.save("SchemaA", "Variant1", sample_data)
    assert "gespeichert" in result
    
    loaded_data = manager.load("SchemaA", "Variant1")
    assert loaded_data == sample_data

def test_list_schemas(manager, sample_data):
    manager.save("Schema1", "var", sample_data)
    manager.save("Schema2", "var", sample_data)
    
    schemas = manager.list_schemas()
    assert sorted(schemas) == ["Schema1", "Schema2"]

def test_list_variants(manager, sample_data):
    manager.save("Motor", "Elektro", sample_data)
    manager.save("Motor", "Diesel", sample_data)
    
    variants = manager.list_variants("Motor")
    assert sorted(variants) == ["Diesel", "Elektro"]

def test_delete_variant(manager, sample_data):
    manager.save("Test", "to_delete", sample_data)
    manager.delete_variant("Test", "to_delete")
    
    assert "to_delete" not in manager.list_variants("Test")
    # Prüfen, ob Datei wirklich weg ist
    path = manager._schema_file("Test", "to_delete")
    assert not path.exists()

def test_delete_schema(manager, sample_data):
    manager.save("App", "v1", sample_data)
    manager.save("App", "v2", sample_data)
    
    manager.delete_schema("App")
    assert "App" not in manager.list_schemas()

# Variable Parser Komponententest
def test_update_groups():
    vp = VariableParser()
    groups = {}

    vp.update_groups(
        groups=groups,
        variable="1337YY001",
        suffix="ESwitch",
        comp="M1_IN_BOOL0_0",
        io="IN"
    )

    entry = groups["YY"]["1337YY001"]["ESwitch"]

    assert entry["BT"] == "BOOL"
    assert entry["IO"] == "WRITE"
    assert entry["C"] == ""

# Integrationstest
def test_integration_generate_template(manager, emg_data, test_csv, test_template, tmp_path, monkeypatch):
    controller = Controller()
    controller.files["profibus"] = str(test_csv)
    controller.directories["input"] = str(tmp_path)
    controller.directories["output"] = str(tmp_path)

    monkeypatch.setattr("main.SchemaManager", lambda path=None: manager) # Im HP wird der SM immer mit "schemas" erstellt

    output = controller.generate_datastructure()
    assert "1337YY001" in output

    manager.save("valves", "emgvalve", emg_data)
  
    controller.template_generator(mimic_file=test_template.name,
        schema_file="valves|emgvalve", # Ausgewähltes Schema im Frontend
        node_name="Node1",
        area_name="Valves",
        type_name="YY"
    )

    # Existenzprüfung
    output_file = Path(tmp_path) / f"{test_template.stem}_YY_out.csv"
    print(output_file)  
    print(output_file.read_text(encoding="utf-8")) 
    assert output_file.exists(), "Output-Datei wurde nicht erzeugt"

    content = output_file.read_text(encoding="utf-8")
    # Prüfung auf richtige Filterung
    assert "1337YY001" in content
    assert "1337YY005" not in content

    lines = output_file.read_text(encoding="utf-8").strip().split("\n")

    # Prüfen auf Richtige Reihenfolge
    for i, line in enumerate(lines[1:], start=2):
        columns = [c.strip() for c in line.split(",")]
        var_name = columns[2]

        expected = [f"Node1/{var_name}_{a}" for a in emg_data["aliases"]]
            
        # Vergleich der Spalten ab Index 3
        actual = columns[3:]
        
        assert actual == actual, (
            f"Reihenfolge-Fehler in Zeile {i+2}!\n"
            f"Config-Aliases: {emg_data['aliases']}\n"
            f"Erhaltene Pfade: {actual}"
        )