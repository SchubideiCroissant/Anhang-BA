import './style.css';
import "github-markdown-css";
import { marked } from "marked";


declare global {
  interface Window {
    showPage: (id: string) => void;
    pywebview: any;
  }
}

function showPage(pageId: string) {
  // Seiten umschalten
  document.querySelectorAll<HTMLElement>('.page').forEach((el) => {
    el.classList.remove('active');
  });

  document.getElementById(pageId)?.classList.add('active');

  // Sidebar Aktiv Klasse setzen
  document.querySelectorAll('.sidebar-item').forEach((el) => {
    el.classList.remove('sidebar-item-active');
  });

  const clicked = Array.from(document.querySelectorAll('.sidebar-item')).find(
  (el) => el.getAttribute('data-page') === pageId);
  clicked?.classList.add('sidebar-item-active');
}

const toggleButton = document.getElementById("toggle-menu");
const sidebar = document.querySelector(".sidebar");

toggleButton?.addEventListener("click", () => {
  sidebar?.classList.toggle("collapsed");
});


// Python Backend Buttons
window.addEventListener('pywebviewready', () => {
  const buttons = document.querySelectorAll('button[data-action]');

  buttons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.getAttribute('data-action');
      const output = document.getElementById("number-output"); // aus HTML Element holen
      switch (action) {
        case 'number':
          let number = await pywebview.api.backend.return_number() ;
          output.textContent = number.toString() // Element schreiben
          console.log(number); 
          break;
        case 'create_ds':
          let answer = await pywebview.api.backend.generate_datastructure();
          managerStats = await pywebview.api.backend.get_component_stats();
          if (managerStats && managerStats.length > 0) { // Diagramm aktualisieren
            refreshCharts(managerStats);
          }
          //output.textContent = answer.toString();
          alert(answer);
          break;
        case 'directory1':        
          await handleDirectorySelection("folder-output1", "input"); // Ordner mit Leeren Template Dateien
          await updateFileDropdown(); // Dropdown für Main-Funktion
          break;
        case 'directory2':        
          await handleDirectorySelection("folder-output2", "output"); // Ordner wo befüllte Template Dateien landen
          break;
        case "inputFile":
          await handleFileSelection("input-file-output", "profibus");
          break;

        case "btnCreateSchema": {
          const name = document.getElementById("schemaName").value.trim();
          const variant = document.getElementById("schemaVariant").value.trim();
          const aliasesRaw = document.getElementById("schemaAliases").value.trim();

          if (!name || !variant || !aliasesRaw) {
            alert("Schema-Name, Variante und Aliase sind Pflichtfelder");
            return;
          }

          const aliases = aliasesRaw
          .split(",")
          .map(a => a.trim())
          .filter(Boolean);

          if (aliases.length === 0) {
            alert("Mindestens ein Alias ist erforderlich");
            return;
          }

          try {
            const res = await pywebview.api.backend.create_schema(
              name,
              variant,
              aliases
            );
            //output.textContent = res ?? "Schema erstellt";
            
            // Tabelle neu laden
            await loadSchemas();
            updateSchemaVariantDropdown();

            // Felder leeren
            (document.getElementById("schemaName") as HTMLInputElement).value = "";
            (document.getElementById("schemaVariant") as HTMLInputElement).value = "";
            (document.getElementById("schemaAliases") as HTMLInputElement).value = ""; 

          } catch (e) {
            output.textContent = "Fehler: " + (e?.message ?? e);
          }
          break;
        }
        case "start-generator":
          await generateTemplates();
      }
    });
  });
});


// Hilfsfunktion zum Füllen des Dropdowns
async function updateFileDropdown() {
    const selectElement = document.getElementById("mimic-file-select") as HTMLSelectElement;
    
    try {
        const files: string[] = await pywebview.api.backend.get_input_files();
        
        selectElement.innerHTML = "";
        
        if (files.length === 0) {
            const opt = document.createElement("option");
            opt.text = "Keine Dateien gefunden";
            selectElement.add(opt);
            return;
        }

        files.forEach(fileName => {
            const option = document.createElement("option");
            option.value = fileName; // an Python gesendet
            option.text = fileName;  
            selectElement.add(option);
        });

        console.log("Dropdown wurde mit " + files.length + " Dateien aktualisiert.");
        
    } catch (error) {
        console.error("Fehler beim Laden der Dateien:", error);
    }
}

async function updateSchemaVariantDropdown() {
    const select = document.getElementById("schema-file-select") as HTMLSelectElement;
    if (!select) return;

    const allEntries = await (window as any).pywebview.api.backend.get_all_variants_for_ui();
    select.innerHTML = '<option value="">-- Variante wählen --</option>'; // Dropdown leeren

    allEntries.forEach((item: {schema: string, variant: string}) => {
        const option = document.createElement("option");

        option.value = `${item.schema}|${item.variant}`; 
        option.text = `${item.schema}: ${item.variant}`;
        
        select.add(option);
    });
}

async function fillTypeDropdown() {
    const select = document.getElementById("type-select") as HTMLSelectElement;
    if (!select) return;

    const types: string[] = await (window as any).pywebview.api.backend.get_component_types();

    types.forEach(typeName => {
        const option = document.createElement("option");
        option.value = typeName; // Der interne Wert 
        option.text = typeName;  // Das was der User sieht
        select.add(option);
    });
}

async function generateTemplates() {
    // Alle selecteded Elemente auslesen
    const fileSelect= document.getElementById("mimic-file-select") as HTMLSelectElement;
    const schemaSelect = document.getElementById("schema-file-select") as HTMLSelectElement;
    const node = (document.getElementById("input-node") as HTMLInputElement).value;
    const area = (document.getElementById("input-area") as HTMLInputElement).value;
    const type = (document.getElementById("type-select") as HTMLInputElement).value;
    
    // checkbox für erweit. Einstellungen
    const useAdvanced = (document.getElementById("use-advanced") as HTMLInputElement).checked;
    let dataType = null;
    let varName = null;
    if (useAdvanced) {
        dataType = (document.getElementById("datatype-select") as HTMLSelectElement).value;
        varName = (document.getElementById("input-variable") as HTMLInputElement).value;
        if(!dataType || !varName)
          alert("Unvollständige Einstellung, erw. Sortierung wird ignoriert")
    }

    // aktuellen ausgewählten Wert auslesen
    const selectedFile = fileSelect.value;
    const selectedSchema = schemaSelect.value;

    if (!selectedFile || !selectedSchema || !node || !area || !type) {
        alert("Bitte alle Felder ausfüllen!");
        return;
    }

    // Hauptfunktion starten
    console.log("Starte Generierung für:", selectedFile);
    let output = await pywebview.api.backend.template_generator(selectedFile, selectedSchema, node, area, type, dataType, varName);
    alert(output);
}


// outputId: Name des Text-Divs
async function handleDirectorySelection(outputId: string, key: string) {
  const folder_name = await pywebview.api.backend.set_directory(key);
  const output = document.getElementById(outputId);
  if (output && folder_name) {
    output.textContent = folder_name.toString();
  }
}

async function handleFileSelection(outputId: string, key: string) {
    const file_name = await pywebview.api.backend.set_file(key);
    const output = document.getElementById(outputId);
    if (output && file_name) {
      output.textContent = file_name.toString();
      console.log(`[${key}] Datei gewählt:`, file_name);
    }
  }

// Schema Tabelle laden
async function loadSchemas() {
  updateSchemaVariantDropdown()
  const container = document.getElementById("schemaList");
  if (!container) return;

  container.innerHTML = "";

  const schemas = await window.pywebview.api.backend.list_schemas();

  for (const schemaName of schemas) {
    const schemaDiv = document.createElement("div");
    schemaDiv.className = "schema";

    const header = document.createElement("div");
    header.className = "schema-header";

    const titleSpan = document.createElement("span");
    titleSpan.className = "schema-title"; // Falls Sie eigene Titel-Stile wollen
    titleSpan.textContent = schemaName;


    const deleteSchemaBtn = document.createElement("button");
    deleteSchemaBtn.className = "variant-delete";
    deleteSchemaBtn.textContent = "✕ Schema löschen";


    deleteSchemaBtn.onclick = async (e) => {
            e.stopPropagation(); 
            const ok = confirm(`Wollen Sie das gesamte Schema '${schemaName}' inklusive aller Varianten wirklich löschen?`);
            if (!ok) return;
            try {
                const res = await window.pywebview.api.backend.delete_schema(schemaName);
                alert(res);
                await loadSchemas();
            } catch (err) {
                alert("Fehler beim Löschen des Schemas: " + (err?.message ?? err));
            }
        };

    header.appendChild(titleSpan);
    header.appendChild(deleteSchemaBtn);

    const variantsDiv = document.createElement("div");
    variantsDiv.className = "variants";

    header.onclick = async () => {
      const open = variantsDiv.style.display === "block";
      variantsDiv.style.display = open ? "none" : "block";
      if (open) return;

      variantsDiv.innerHTML = "Lade...";

      const variants = await window.pywebview.api.backend
        .list_schema_variants(schemaName);

      variantsDiv.innerHTML = "";

      for (const variant of variants) {
        const data = await window.pywebview.api.backend
          .load_schema(schemaName, variant);

        const v = document.createElement("div");
        v.className = "variant";

        // linker Teil: Variantenname
        const nameSpan = document.createElement("span");
        nameSpan.className = "variant-name";
        nameSpan.textContent = variant;

        // rechter Teil: Aliases + Delete
        const right = document.createElement("div");
        right.className = "variant-right";

        const aliasesSpan = document.createElement("span");
        aliasesSpan.className = "variant-aliases";
        aliasesSpan.textContent = data.aliases.join(" , ");

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "variant-delete";
        deleteBtn.textContent = "✕ Variante löschen";

        deleteBtn.onclick = async (e) => {
          e.stopPropagation();

          const ok = confirm(
            `Variante '${variant}' wirklich löschen?`
          );
          if (!ok) return;

          try {
            let res = await window.pywebview.api.backend.delete_schema_variant(schemaName,variant);
            alert(res);
            await loadSchemas(); // neu laden nach Delete
          } catch (err) {
            alert("Fehler beim Löschen: " + (err?.message ?? err));
          }
        };

        right.appendChild(aliasesSpan);
        right.appendChild(deleteBtn);

        v.appendChild(nameSpan);
        v.appendChild(right);

        variantsDiv.appendChild(v);
      }
    };

    schemaDiv.appendChild(header);
    schemaDiv.appendChild(variantsDiv);
    container.appendChild(schemaDiv);
  }
}

window.addEventListener("pywebviewready", () => {
  loadSchemas();
  updateSchemaVariantDropdown();
  fillTypeDropdown();
});


//Markdown
async function loadMarkdown() {
  try {
    const res = await fetch("/docs.md");
    const text: string = await res.text();
    const container = document.getElementById("docs_md");
    if (container) {
      container.innerHTML = marked(text);
    }
  } catch (error) {
    console.error("Fehler beim Laden der Markdown-Datei:", error);
  }
}

if (window.pywebview) {
  window.addEventListener("pywebviewready", loadMarkdown);
} else {
  window.addEventListener("DOMContentLoaded", loadMarkdown);
}// Auf Pywebview warten


window.showPage = showPage;
let managerStats: any[] = [];

import Chart from "chart.js/auto";
function refreshCharts(data: any[]) {
  const labels = data.map(row => row.type);
  const counts = data.map(row => row.count);

  // Pie Chart aktualisieren
  pieChart.data.labels = labels;
  pieChart.data.datasets[0].data = counts;
  pieChart.data.datasets[0].label = 'Komponentenverteilung'; 
  pieChart.update();

  // Line Chart aktualisieren
  lineChart.data.labels = labels;
  lineChart.data.datasets[0].data = counts;
  lineChart.data.datasets[0].label = 'Häufigkeit';
  lineChart.update();
}

const line_data = [
    { type: 2010, count: 10 },
    { type: 2011, count: 20 },
    { type: 2012, count: 15 },
    { type: 2013, count: 25 },
    { type: 2014, count: 22 },
    { type: 2015, count: 30 },
    { type: 2016, count: 28 },
  ];

const currentData = (managerStats && managerStats.length > 0) ? managerStats : line_data; // ist Profibus Datei geladen worden?

const backgroundColor = [
  '#1f77b4', // Blau
  '#ff7f0e', // Orange
  '#2ca02c', // Grün
  '#d62728', // Rot
  '#9467bd', // Violett
  '#8c564b', // Braun
  '#e377c2', // Pink
  '#7f7f7f', // Grau
  '#bcbd22', // Oliv
  '#17becf', // Türkis

  '#aec7e8', // Hellblau
  '#ffbb78', // Hellorange
  '#98df8a', // Hellgrün
  '#ff9896', // Hellrot
  '#c5b0d5', // Hellviolett
  '#c49c94', // Hellbraun
  '#f7b6d2', // Hellpink
  '#c7c7c7', // Hellgrau
  '#dbdb8d', // Helloliv
  '#9edae5'  // Helltürkis
];


Chart.defaults.animation = false;
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = true;


const lineChart = new Chart(
  document.getElementById('chart1') as HTMLCanvasElement, 
  {
    type: 'bar',
    options: {
      
    },
    data: {
      labels: line_data.map(row => row.type),
      datasets: [{
        label: 'Beispiel-Daten',
        data: line_data.map(row => row.count),
        backgroundColor: backgroundColor,
        borderColor: '#1149a3ff',
        //tension: 0.4
      }]
    }
});


const pieChart= new Chart(
  document.getElementById('pieChart') as HTMLCanvasElement, 
  {
    type: 'pie',
    options: {
    
    },
    data: {
      labels: line_data.map(row => row.type),
      datasets: [{
        label: 'Pizza',
        data: line_data.map(row => row.count),
        backgroundColor: backgroundColor,
      }]
    }
});
