import xml.etree.ElementTree as ET
import pandas as pd

# Load the .twb file (Tableau Workbook)
twb_file = "D:\EProjects\TB2PBI\POC\extracted_twbx_old\helloworld.twb"  # Change to your .twb path
tree = ET.parse(twb_file)
root = tree.getroot()


# Utility to extract XML safely
def get_attr(element, key, default=None):
    return element.attrib.get(key, default)


# --- 1. Datasources: Relations and Columns ---
datasources_info = []
for datasource in root.findall(".//datasource"):
    ds_name = get_attr(datasource, "name", "Unnamed Datasource")

    # Extract relations
    for relation in datasource.findall(".//relation"):
        relation_text = relation.text.strip() if relation.text else "None"
        relation_type = get_attr(relation, "type", "None")
        datasources_info.append({
            "Datasource": ds_name,
            "Type": "Relation",
            "Detail": f"{relation_type}: {relation_text}"
        })

    # Extract columns
    for column in datasource.findall(".//column"):
        col_name = get_attr(column, "name")
        col_datatype = get_attr(column, "datatype")
        datasources_info.append({
            "Datasource": ds_name,
            "Type": "Column",
            "Detail": f"{col_name} ({col_datatype})"
        })

# --- 2. Actions ---
actions_info = []
for action in root.findall(".//action"):
    action_type = action.tag
    name = get_attr(action, "name")
    src = get_attr(action, "source-sheet")
    tgt = get_attr(action, "target-sheet")
    actions_info.append({
        "Action Name": name,
        "Type": action_type,
        "From": src,
        "To": tgt
    })

# --- 3. Worksheets ---
worksheets = [get_attr(ws, "name") for ws in root.findall(".//worksheet")]

# --- 4. Dashboards ---
dashboards = [get_attr(db, "name") for db in root.findall(".//dashboard")]

# --- 5. Windows (dashboard containers/layouts) ---
windows = []
for db in root.findall(".//dashboard"):
    db_name = get_attr(db, "name")
    for window in db.findall(".//window"):
        zone_type = get_attr(window, "zone-type", "Unknown")
        windows.append({
            "Dashboard": db_name,
            "Window Type": zone_type
        })

# --- Print or Export Summary ---
print("\n=== 📦 Datasources (Relations & Columns) ===")
print(pd.DataFrame(datasources_info).head())

print("\n=== 🔄 Actions ===")
print(pd.DataFrame(actions_info).head())

print("\n=== 📊 Worksheets ===")
print(worksheets)

print("\n=== 🧩 Dashboards ===")
print(dashboards)

print("\n=== 🪟 Windows (Layout Elements) ===")
print(pd.DataFrame(windows).head())
