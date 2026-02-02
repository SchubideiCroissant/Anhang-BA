# pyDEXPI Untersuchung
**Setup**:
- `cd /dexpi`
- create Python-Environment `python -m venv venv311`
- run environment ` .\venv311\Scripts\activate`
- `pip install pydexpi`

**Start**
`python dexpi_ex.py` in `/dexpi`

## Projektziel

Dieses Projekt erweitert pyDEXPI, um DEXPI-Modelle präzise zu
visualisieren und Prozessflüsse zu analysieren.\
Der Fokus liegt auf:

-   Rückführung von Graph-Knoten auf echte Modellobjekte
-   Traversieren des Prozessflusses (Upstream/Downstream bis zum
    nächsten Equipment)
-   Aufbau einer Datenstruktur, die alle Pfade pro Equipment speichert
-   einer anpassbaren Matplotlib-Visualisierung mit echten Tags und
    Farben

------------------------------------------------------------------------

## Modellzugriff und Rückführung

Die DEXPI-Datei wird mit `ProteusSerializer` geladen.
Eine `id_map` ordnet alle Knoten wieder ihren Modellobjekten zu:

    id_map[node_id] -> DexpiObject

Eine `nozzle_map` stellt Nozzle → Equipment sicher.

Für konsistente Labels existiert:

    get_tag_name(node, id_map, nozzle_map)

Damit werden Equipment, Instrumente, Piping-Komponenten und Nozzles
einheitlich benannt.

------------------------------------------------------------------------

## Visualisierung über MyGraphLoader

Die Klasse `MyGraphLoader` erweitert `MLGraphLoader`:

-   echte Labels (TagName, Instrumentnummer, PipingComponentName), statt IDs
-   Farbcodierung pro Klasse (z. B. GlobeValve, PipeTee)

Die Positionierung erfolgt über:

    _add_positions(self.plant_graph)

Rendering:

    nx.draw(...)
    nx.draw_networkx_labels(...)

------------------------------------------------------------------------

## Traversieren des Prozessflusses

Ziel: Für jedes Equipment alle Wege zum nächsten Equipment finden.

Funktionen:

    downstream_paths_until_equipment()
    upstream_paths_until_equipment()

Beide stoppen erst am nächsten Equipment, nicht am Startpunkt.\
Die Ausgabe sind Listen von Strings:

    ['P4711', 'Valve12', 'H1008']

------------------------------------------------------------------------

## Pfad-Datenbank

Für jedes Equipment wird eine vollständige Struktur erzeugt:

    {
      "H1007": {
        "downstream": [...],
        "upstream": [...]
      }
    }

Erzeugung:

    path_db = build_path_database(G, id_map, nozzle_map)

Damit ist eine vollständige Analyse aller Fließwege speziell um Komponenten möglich.

------------------------------------------------------------------------

## Ergebnis

Der Code liefert:

-   eine bereinigte Graph-Darstellung des DEXPI-Modells
-   echte aussagekräftige Labels im Graph
-   Up/Downstream-Verbindungen anzeigen
-   strukturierte Pfad-"Datenbank" pro Equipment 

Es bildet damit eine Grundlage für Flussanalyse,
Validierung und weiterführende Modellverarbeitung, speziell im Hinblick auf Relationen zwischen Komponenten.
