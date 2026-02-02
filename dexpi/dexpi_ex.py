from pydexpi.dexpi_classes import equipment, instrumentation, piping
from pydexpi.loaders import *
from pydexpi.toolkits.piping_toolkit import *
from pydexpi.toolkits.base_model_utils import *
from pydexpi.loaders.graph_loader import *
import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
from pydexpi.loaders.ml_graph_loader import MLGraphLoader, _add_positions
import networkx as nx
import math
import textwrap


class MyGraphLoader(MLGraphLoader):

    COLOR_MAP = {
        "GlobeValve": "#8A2BE2",
        "ButterflyValve": "#E377C2",
        "SwingCheckValve": "#E377C2",
        "BallValve": "#E377C2",
        "PipeTee": "#CF1717",
        "FlowInPipeOffPageConnector": "#000000",
        "FlowOutPipeOffPageConnector": "#222222",
    }
    def get_color(self, class_name):
        return self.COLOR_MAP.get(class_name)

    def draw_process_matplotlib(self) -> Figure:
        """Draw the process graph using matplotlib.pyplot.

        Returns
        -------
        go.Figure
            Figure object for Plotly.
        """
        

        draw_info = {"node_labels": {}, "node_colors": [], "edge_labels": {}}
        for node in self.plant_graph.nodes:
            attributes = self.plant_graph.nodes[node]
            label = self._get_node_label(attributes) # Um "echte" Namen auf die Nodes zu schreiben
            label = self.wrap_label(label, width=8) # Für Darstellung
            draw_info["node_labels"][node] = label 
            class_name = attributes["dexpi_class"]

            # Custom Colors
            color = self.get_color(class_name)
            if color is not None:
                # Custom Farbe gefunden
                draw_info["node_colors"].append(color)
            else:
                if class_name in dir(piping):
                    draw_info["node_colors"].append("red")
                elif class_name in dir(instrumentation):
                    draw_info["node_colors"].append("blue")
                elif class_name in dir(equipment):
                    draw_info["node_colors"].append("green")
        for edge in self.plant_graph.edges:
            draw_info["edge_labels"][edge] = self.plant_graph.edges[edge]["dexpi_class"]
        self.plant_graph = _add_positions(self.plant_graph, len(self.plant_graph.nodes))

        pos = nx.get_node_attributes(self.plant_graph, "pos")
        fig = plt.figure(figsize=(16,9))
        nx.draw(
            self.plant_graph,
            pos,
            node_color=draw_info["node_colors"],
            node_size=1400,
            alpha=0.9
        )

        # draws Knoten/Node Labels
        nx.draw_networkx_labels(
            self.plant_graph,
            pos,
            labels=draw_info["node_labels"],
            verticalalignment="center_baseline",
            font_color="white",
            font_size=7    )
        
        #nx.draw_networkx_edge_labels(
        #    self.plant_graph,
        #    pos,
        #    edge_labels=draw_info["edge_labels"],
        #    font_size=3)
        return fig

    def wrap_label(self, text, width):
        return "\n".join(textwrap.wrap(text, width=width))
    def _get_node_label(self, attributes):
        for key in ["tagName","processInstrumentationFunctionNumber", "subTagName", "pipingComponentName", "actuatingSystemNumber"]:
            if key in attributes and attributes[key]:
                return str(attributes[key])
        return attributes.get("dexpi_class", "")
    
def init():
    #directory_path = "Dexpi"
    filename = "C01V04-VER.EX01.xml"
    my_loader = ProteusSerializer()
    dexpi_model = my_loader.load("",filename)
    return dexpi_model

def print_standard_info(cm):
    print("Rohrleitungssysteme:", len(cm.pipingNetworkSystems))
    print("Instrumente:", len(cm.processInstrumentationFunctions))
    print("Aktoren:", len(cm.actuatingSystems))
    print("Schleifen:", len(cm.instrumentationLoopFunctions))
    print("Plant Items:", len(cm.plantStructureItems))
    print("Signal-Generatoren:", len(cm.processSignalGeneratingSystems))
    print("Getaggte Items:", len(cm.taggedPlantItems))

def print_tagged_items(cm):
    
    print("=== Instrumente ===")
    for item in cm.processInstrumentationFunctions:
        print(f"{item.processInstrumentationFunctionNumber or 'Unnamed'} | ID: {item.id}")
    print("\n===================\n")

    print("=== Aktoren ===")
    for item in cm.actuatingSystems:
        print(f"{item.actuatingSystemNumber or 'Unnamed'} | ID: {item.id}")
    print("=================\n")

    print("=== Instrumentierungsschleifen ===")
    for loop in cm.instrumentationLoopFunctions:
        print(f"{loop.instrumentationLoopFunctionNumber} | ID: {loop.id}")
    print("==================================\n")

    print("=== Getaggte Items ===")
    for item in cm.taggedPlantItems:
        print(f"{item.tagName or 'Unnamed'}  | ID: {item.id}")
    print("======================\n")

    print("=== PIPING ===")
    for network in cm.pipingNetworkSystems:
        for seg in network.segments:
            for item in seg.items:
                if hasattr(item, "pipingComponentName"):
                    print(f"{item.pipingComponentName} | ID: {item.id}")
    
    print("======================\n")

    print("=====================================\n")

        #print(f"{item.tagNamePrefix}")
        #print(f"{item.tagNameSequenceNumber}")
        #print(f"{item.tagNameSuffix})"

def get_tagged_components(cm):
    components = []
    for item in cm.taggedPlantItems:
        # print(f"{item.tagName or 'Unnamed'}  | ID: {item.id}")
        components.append(item.tagName)    
    return components

def print_nozzles_and_equipment(cm):
# Nozzles und zugehöriges Equipment ausgeben
    for eq in cm.taggedPlantItems:
        if hasattr(eq, "nozzles"):
            for noz in eq.nozzles:
                print(f"Nozzle {noz.id} {noz.subTagName} gehört zu {eq.tagName} ")

def print_pipe_connections(cm):

    nozzle_map = build_nozzle_equipment_map(cm)

    for i, item in enumerate(cm.pipingNetworkSystems, start=1):
        print(f"Network {i}:")
        for x, segment in enumerate(item.segments):
            print("Seg ", x)
            src_item = segment.sourceItem
            trg_item = segment.targetItem
            print(f"sourceItem: {src_item} resolv to { resolve_equipment_for_item(src_item, nozzle_map)}")
            print(f"targetItem: {trg_item} resolv to {resolve_equipment_for_item(trg_item, nozzle_map)}")
 
            #print(f"sourceNode: {segment.sourceNode}")
            #print(f"targetNode: {segment.targetNode} \n")
        print("-------------------------")

### Traversieren/Beziehungen finden im Model, Prototyping
def build_nozzle_equipment_map(cm):
    """Nozzles werden zu Plant Items zugeordnet """
    mapping = {}
    for eq in cm.taggedPlantItems:
        for noz in getattr(eq, "nozzles", []):
            mapping[noz.id] = eq
    return mapping

def resolve_equipment_for_item(item, nozzle_map):
    if item is None:
        return None

    # Wenn es Equipment ist
    if hasattr(item, "tagName") and item.tagName:
        return item.tagName

    # Wenn es eine Nozzle ist → Lookup
    if item.id in nozzle_map:
        return nozzle_map[item.id].tagName

    # Alles andere hat kein Equipment
    return None

def extract_segment_connections(cm):
    nozzle_map = build_nozzle_equipment_map(cm)
    connections = []

    for pns in cm.pipingNetworkSystems:
        for seg in pns.segments:
            src = resolve_equipment_for_item(seg.sourceItem, nozzle_map)
            tgt = resolve_equipment_for_item(seg.targetItem, nozzle_map)
            #print(" sourceItem:", seg.sourceItem)
            #print(" resolved:", src.tagName if src else None)
            #print(" targetItem:", seg.targetItem)
            #print(" resolved:", tgt.tagName if tgt else None)
            #print()

            if src and tgt and src != tgt:
                connections.append((src.tagName, tgt.tagName))

    return connections

def print_simple_equipment_connections(cm):
    connections = extract_segment_connections(cm)

    # doppelte Verbindungen vermeiden: (A,B) und (B,A) als einmal interpretieren
    unique_connections = set()

    for a, b in connections:
        pair = tuple(sorted([a, b]))
        unique_connections.add(pair)

    print("=== Equipment-Verbindungen ===")
    for a, b in sorted(unique_connections):
        print(f"{a} → {b}")

### Traversieren m. Dexpi Pipe Toolkit, deprecated? Graph nutzen?
def traverse_segment(seg, start_item):
    items = list(seg.items)
    conns = list(seg.connections)
    print(start_item)
    print(seg)
    print(items)
    print(conns)
    if not items or not conns:
        return []

    return traverse_items_and_connections(
        items,
        conns,
        start_item,
        lambda x: False  # komplettes Segment durchlaufen
    )

def equipment_connections_in_segment(seg, nozzle_map):
    connections = set()

    # Startpunkte: Items, die Equipment zugeordnet sind (z. B. Nozzles)
    start_items = [
        item for item in seg.items
        if resolve_equipment_for_item(item, nozzle_map)
    ]

    for start in start_items:
        path = traverse_segment(seg, start)

        eq_tags = []
        for item in path:
            eq = resolve_equipment_for_item(item, nozzle_map)
            if eq:
                eq_tags.append(eq.tagName)

        # benachbarte Paare extrahieren
        for i in range(len(eq_tags) - 1):
            a, b = eq_tags[i], eq_tags[i+1]
            if a != b:
                pair = tuple(sorted([a, b]))
                connections.add(pair)

    return connections

def get_all_equipment_connections(cm):
    nozzle_map = build_nozzle_equipment_map(cm)
    all_conns = set()

    # Hier über alle Segmente gehen
    for pns in cm.pipingNetworkSystems:
        for seg in pns.segments:
            all_conns |= equipment_connections_in_segment(seg, nozzle_map)

    return all_conns

def print_all_equipment_connections(cm):
    conns = get_all_equipment_connections(cm)

    print("=== Equipment-Verbindungen (Segment-Traversal) ===")
    for a, b in sorted(conns):
        print(f"{a} → {b}")

### Graph methoden Zielführend
def graph(dexpi_model):
    # Main für Grafen
    loader = MyGraphLoader(plant_model=dexpi_model) # MLGraphLoader
    loader.dexpi_to_graph(dexpi_model)
    #loader.parse_equipment_and_piping()
    #loader.parse_instrumentation()
    G = loader.plant_graph
    
    fig= loader.draw_process_matplotlib()
    fig.patch.set_facecolor("#FFFFFF00")

    # plt.show() # ! Graph anzeigen!
    
    return G

    
def print_edges_vertices(G, id_map, nozzle_map):
    print("Kanten")
    for u, v in G.edges:
        print(f"{get_tag_name(u, id_map, nozzle_map)} -> {get_tag_name(v, id_map, nozzle_map)}")
    
    # Knoten
    print("Knoten")
    for n in G:
        print(f"{resolve_graph_node(n, id_map)}")

def neighbors_of_tag(G, cm, id_map, nozzle_map, node):

    print("Downstream:")
    for succ in G.successors(node):
        print("  ->", get_tag_name(succ, id_map, nozzle_map))

    print("Upstream:")
    for pred in G.predecessors(node):
        print("  <-", get_tag_name(pred, id_map, nozzle_map))

def build_id_map(cm):
    id_map = {}

    # Equipment
    for eq in cm.taggedPlantItems:
        id_map[eq.id] = eq

    # Instrumentierungs-Funktionen (Transmitter, Controller, etc.)
    for pif in cm.processInstrumentationFunctions:
        id_map[pif.id] = pif

    # Aktoren
    for akt in cm.actuatingSystems:
        id_map[akt.id] = akt

    # Piping
    for network in cm.pipingNetworkSystems:
        for seg in network.segments:

            for item in seg.items:
                id_map[item.id] = item
    return id_map

def resolve_graph_node(node, id_map):
    # Gibt das "echte" Objekt zurück
    if isinstance(node, str):
        return id_map.get(node, node)  # falls unbekannt: String zurück
    return node

def get_tag_name(node, id_map, nozzle_map):
    # 1) Falls Node ein String (UUID oder synthetisch)
    node = resolve_graph_node(node, id_map)

    # 2) Equipment
    if hasattr(node, "tagName") and node.tagName:
        return node.tagName

    # 3) Nozzle → Equipment
    if hasattr(node, "id") and node.id in nozzle_map:
        return nozzle_map[node.id].tagName

    # 4) Piping-Komponente

    if hasattr(node, "pipingComponentName"):
        # Rückführung auf Instrument/ActuatingFunction, depr
        #instr_name, af_name = find_instrument_for_valve(node, id_map)
        #if af_name or instr_name:
            #return f"CTRL_VALVE:{af_name or instr_name}"

        # Wenn PipingComponentName gesetzt ist → normal
        if node.pipingComponentName:
            return f"PIPING:{node.pipingComponentName}"

        # Wenn KEIN Name → automatisch typbasierte Labels erzeugen
        cls = node.__class__.__name__
        short_id = getattr(node, "id", "???")[:8]
        return f"PIPING: {cls}:{short_id}"

    # 5) Sensoren / Instrumente
    if hasattr(node, "processInstrumentationFunctionNumber"):
        return f"INST: {node.processInstrumentationFunctionNumber}"

    if hasattr(node, "instrumentationLoopFunctionNumber"):
        return f"INST:{node.instrumentationLoopFunctionNumber}"


    # 6) Aktoren unused
    if hasattr(node, "actuatingSystemNumber"):
        return f"AKT:{node.actuatingSystemNumber}"
    

    # 7) Fallback: ID anzeigen
    if hasattr(node, "id"):
        cls = node.__class__.__name__
        short_id = getattr(node, "id", "???")[:8]
        return f"OBJ: {cls}:{short_id}"


    # 8) letzter Fallback
    return str(node)


def find_instrument_for_valve(valve, id_map):
    """
    Rückführung Ventil -> Instrument, nicht mehr groß nötig, depr
    """
    for obj in id_map.values():
        # Heuristik: ProcessInstrumentationFunction erkennen
        if not hasattr(obj, "processInstrumentationFunctionNumber"):
            continue
        if not hasattr(obj, "actuatingFunctions"):
            continue

        for af in obj.actuatingFunctions:
            sys = getattr(af, "systems", None)
            if not sys:
                continue

            ov_ref = getattr(sys, "operatedValveReference", None)
            if not ov_ref:
                continue

            v = getattr(ov_ref, "valve", None)
            if v is None:
                continue

            if v is valve:
                instr_name = (
                    obj.processInstrumentationFunctionNumber
                    or obj.deviceInformation
                    or f"Instr_{obj.id}"
                )
                af_name = getattr(af, "actuatingFunctionNumber", None)
                return instr_name, af_name

    return None, None

def find_node_by_tag(G, map,nozzle_map, tag):
    """erwartet Node Namen als String"""
    for node in G.nodes:
        # Lesbaren Namen bestimmen
        name = get_tag_name(node, map, nozzle_map)
        # print(name)
        if name == tag:
            return node

    return None

def is_equipment(node, id_map):
    real = resolve_graph_node(node, id_map)

    if real is None:
        return False

    return hasattr(real, "tagName") and real.tagName


def print_downstream_until_equipment(G, node, id_map, nozzle_map, visited=None, depth=0):
    if(node is None):
        return
    
    if visited is None:
        visited = set()

    if node in visited:
        return
    visited.add(node)

    indent = "  " * depth
    for succ in G.successors(node):
        name = get_tag_name(succ, id_map, nozzle_map)
        print(f"{indent}-> {name}")

        if is_equipment(succ, id_map):
            # Hier stoppen wir, weil Equipment erreicht
            continue
        else:
            # weiter tiefer suchen, bis Equipment kommt
            print_downstream_until_equipment(G, succ, id_map, nozzle_map, visited, depth + 1)

def print_upstream_until_equipment(G, node, id_map, nozzle_map, visited=None, depth=0):
    if(node is None):
        return

    if visited is None:
        visited = set()

    if node in visited:
        return
    visited.add(node)

    indent = "  " * depth

    for pred in G.predecessors(node):
        name = get_tag_name(pred, id_map, nozzle_map)
        print(f"{indent}<- {name}")

        if is_equipment(pred, id_map):
            continue
        else:
            # weiter nach oben suchen, bis Equipment kommt
            print_upstream_until_equipment(G, pred, id_map, nozzle_map, visited, depth + 1)

def up_downstream_formatted(G, id_map, nozzle_map, node_name):
    node_name = node_name
    node1 = find_node_by_tag(G, id_map, nozzle_map, node_name)    
    print(f"{node_name} gefunden") if  node1 is not None else print("!no match")

    print("Downstream bis zum nächsten Equipment:")
    print_downstream_until_equipment(G, node1, id_map, nozzle_map)
    print("-----------------\n")

    print("Upstream bis zum nächsten Equipment:")
    print_upstream_until_equipment(G, node1, id_map, nozzle_map)
    print("-----------------\n")

# Baut Datenstruktur für Pfade
def build_path_database(G, id_map, nozzle_map):
    database = {}

    components = get_tagged_components(cm)
    print(components)
    for tag in components:
        node = find_node_by_tag(G, id_map, nozzle_map, tag)

        ds = downstream_paths_until_equipment(G, node, id_map, nozzle_map)
        us = upstream_paths_until_equipment(G, node, id_map, nozzle_map)
        
        database[tag] = {
            "downstream": ds,
            "upstream": us
        }

    return database
def downstream_paths_until_equipment(G, node, id_map, nozzle_map, visited=None, depth=0):
    if node is None:
        return []

    if visited is None:
        visited = set()

    if node in visited:
        return []
    visited.add(node)

    current_name = get_tag_name(node, id_map, nozzle_map)

    # Equipment = Endpunkt, ABER NICHT am Start
    if depth > 0 and is_equipment(node, id_map):
        return [[current_name]]

    successors = list(G.successors(node))
    if not successors:
        return [[current_name]]

    paths = []
    for succ in successors:
        subpaths = downstream_paths_until_equipment(
            G, succ, id_map, nozzle_map, visited.copy(), depth + 1
        )
        for sp in subpaths:
            paths.append([current_name] + sp)

    return paths
def upstream_paths_until_equipment(G, node, id_map, nozzle_map, visited=None, depth=0):
    if node is None:
        return []

    if visited is None:
        visited = set()

    if node in visited:
        return []
    visited.add(node)

    current_name = get_tag_name(node, id_map, nozzle_map)

    # Equipment nur stoppen, wenn NICHT Startknoten
    if depth > 0 and is_equipment(node, id_map):
        return [[current_name]]

    predecessors = list(G.predecessors(node))
    if not predecessors:
        return [[current_name]]

    paths = []
    for pred in predecessors:
        subpaths = upstream_paths_until_equipment(
            G, pred, id_map, nozzle_map, visited.copy(), depth + 1
        )
        for sp in subpaths:
            paths.append(sp + [current_name])

    return paths


def get_instrument_name(pif):
    return (
        pif.processInstrumentationFunctionNumber
        or pif.deviceInformation
        or f"Instrument_{pif.id}"
    )

def get_valve_name(v):
    name = getattr(v, "pipingComponentName", None)
    if name:
        return name

    # Fallback über CustomAttributes (zB PipingComponentNameAssignmentClass)
    for attr in getattr(v, "customAttributes", []):
        if "Name" in attr.attributeName or "Name" in (attr.attributeURI or ""):
            if attr.value:
                return str(attr.value)

    return v.id


dexpi_model= init()
cm = dexpi_model.conceptualModel
id_map = build_id_map(cm)
nozzle_map = build_nozzle_equipment_map(cm)
G = graph(dexpi_model)

print_tagged_items(cm)

path_db = build_path_database(G, id_map, nozzle_map)
for tag in get_tagged_components(cm):
    print(f"\n{tag}")
    print("Downstream", path_db[tag]["downstream"])
    print("Upstream", path_db[tag]["upstream"])


# Andere Pfad Darstellung:
#components = get_tagged_components(cm)
#for comp in components:
#    print(f"- {comp}")
#    up_downstream_formatted(G, id_map, nozzle_map, comp)


# depr
#print_instrument_control_connections(cm)
#print_loop_connections(cm)
#print_pipe_connections(cm)
#print_all_equipment_connections(cm)
#print_standard_info(cm)
#print_nozzles_and_equipment(cm)
#print_pipe_connections(cm)



        