# VARTA Storage (GhostCHS)

Home Assistant integration for VARTA energy storage systems using Modbus and Web (CGI) interface.

Based on: https://github.com/Vip0r/varta_storage

---

## 🇩🇪 Installation

### 🧩 Installation über HACS (empfohlen)

1. Öffne HACS:


HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories


2. Repository hinzufügen:


Repository: https://github.com/GhostCHS/varta_storage_ha

Typ: Integration


3. Installation:


HACS → Integrationen → Suche nach "VARTA Storage"
→ Installieren


4. Home Assistant neu starten:


Einstellungen → System → Neustart


5. Integration hinzufügen:


Einstellungen → Geräte & Dienste → Integration hinzufügen


Suche nach:


VARTA Storage


👉 Die Konfiguration erfolgt komplett über die Weboberfläche.

---

### ⚙️ Manuelle Installation

1. Öffne dein Home Assistant Config-Verzeichnis  
(dort wo `configuration.yaml` liegt)

2. Erstelle (falls nicht vorhanden):


/config/custom_components/


3. Erstelle den Ordner:


/config/custom_components/varta_storage/


4. Kopiere alle Dateien aus:


custom_components/varta_storage/


in den neuen Ordner

5. Home Assistant neu starten

6. Integration hinzufügen:


Einstellungen → Geräte & Dienste → Integration hinzufügen


Suche nach:


VARTA Storage


---

## 🇬🇧 Installation

### 🧩 Installation via HACS (recommended)

1. Open HACS:


HACS → Integrations → ⋮ → Custom repositories


2. Add repository:


Repository: https://github.com/GhostCHS/varta_storage_ha

Category: Integration


3. Install integration:


HACS → Integrations → Search for "VARTA Storage"
→ Download


4. Restart Home Assistant:


Settings → System → Restart


5. Add integration:


Settings → Devices & Services → Add Integration


Search for:


VARTA Storage


👉 Configure everything via the UI.

---

### ⚙️ Manual Installation

1. Open your Home Assistant config directory  
(where `configuration.yaml` is located)

2. Create (if missing):


/config/custom_components/


3. Create folder:


/config/custom_components/varta_storage/


4. Copy all files from:


custom_components/varta_storage/


5. Restart Home Assistant

6. Add integration:


Settings → Devices & Services → Add Integration


Search for:


VARTA Storage


---

## ⚙️ Features

- Local Modbus communication
- Optional Web (CGI) data integration
- Home Assistant Config Flow support
- No YAML configuration required
- Works fully locally (no cloud)

---

## ⚠️ Notes

- Make sure Modbus is enabled on your VARTA system
- Default Modbus port: `502`
- CGI/Web interface may require login credentials

---

## 🛠️ Development

This fork improves:

- Config Flow stability
- Options handling
- Data update reliability
- Compatibility with newer Home Assistant versions

---

## 📄 License

Same as original project.
