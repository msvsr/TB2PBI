import zipfile
import os
import xml.etree.ElementTree as ET
import json
import subprocess

# STEP 1: Extract .twbx and find .twb
def extract_twbx(twbx_path, output_dir="extracted_twbx"):
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"✅ Extracted to {output_dir}")
    return output_dir

def find_twb_file(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".twb"):
                return os.path.join(root, file)
    raise FileNotFoundError("No .twb file found in extracted .twbx.")

# STEP 2: Parse .twb XML
def parse_twb(twb_path):
    tree = ET.parse(twb_path)
    root = tree.getroot()

    workbook_info = {
        "datasources": [],
        "worksheets": [],
        "calculated_fields": [],
        "joins": [],
        "parameters": []
    }

    for ds in root.findall('.//datasource'):
        datasource = {
            "name": ds.get('name'),
            "fields": [],
            "connections": []
        }
        for column in ds.findall('.//column'):
            datasource["fields"].append({
                "name": column.get('name'),
                "datatype": column.get('datatype'),
                "role": column.get('role'),
                "type": column.get('type')
            })
        for conn in ds.findall('.//connection'):
            datasource["connections"].append({
                "class": conn.get('class'),
                "dbname": conn.get('dbname'),
                "server": conn.get('server'),
                "authentication": conn.get('authentication')
            })
        workbook_info["datasources"].append(datasource)

    for calc in root.findall('.//calculation'):
        workbook_info["calculated_fields"].append({
            "name": calc.get('name'),
            "formula": calc.get('formula')
        })

    for relation in root.findall('.//relation'):
        if relation.get('type') == 'join':
            workbook_info["joins"].append({
                "left": relation.get('left'),
                "right": relation.get('right'),
                "operator": relation.get('operator')
            })

    for ws in root.findall('.//worksheet'):
        workbook_info["worksheets"].append({
            "name": ws.get('name')
        })

    for param in root.findall('.//column[@param-domain-type]'):
        workbook_info["parameters"].append({
            "name": param.get('name'),
            "datatype": param.get('datatype'),
            "param-domain-type": param.get('param-domain-type')
        })

    return workbook_info

# STEP 3: Convert to BIM
def map_datatype(tableau_type):
    mapping = {
        "string": "string",
        "real": "double",
        "integer": "int64",
        "boolean": "boolean",
        "date": "datetime"
    }
    return mapping.get(tableau_type.lower(), "string")

def convert_formula_to_dax(formula):
    if not formula:
        return "BLANK()"
    formula = formula.replace("IF ", "IF(")
    return formula  # real conversion would need parsing

def convert_to_bim(tableau_data):
    tables = []
    for ds in tableau_data['datasources']:
        table = {
            "name": ds['name'].replace(" ", "_"),
            "columns": []
        }
        for field in ds.get('fields', []):
            table['columns'].append({
                "name": field['name'].replace("[", "").replace("]", "").replace(" ", "_"),
                "dataType": map_datatype(field.get('datatype', 'string')),
                "isHidden": False
            })
        tables.append(table)

    measures = []
    for calc in tableau_data.get('calculated_fields', []):
        name = calc.get('name')
        if not name:
            continue  # Skip unnamed calculated fields
        measures.append({
            "name": name.replace(" ", "_"),
            "expression": convert_formula_to_dax(calc.get('formula')),
            "isHidden": False
        })

    return {
        "model": {
            "culture": "en-US",
            "dataSources": [],
            "tables": tables,
            "measures": measures
        }
    }

# STEP 4: Save BIM
def save_bim_model(bim_data, path="model.bim"):
    with open(path, 'w') as f:
        json.dump(bim_data, f, indent=2)
    print(f"✅ Saved BIM to {path}")

# STEP 5: Generate PBIT using pbi-tools
import os
import shutil
import json
import subprocess

def generate_pbit_from_bim(bim_path: str, output_path="output.pbit"):
    print("🚧 Converting .bim to .pbit using pbi-tools...")
    try:
        result = subprocess.run([
            "pbi-tools", "convert",
            bim_path,
            output_path,
            "-overwrite"
        ], capture_output=True, text=True, check=True)
        print("✅ .pbit created at:", output_path)
    except subprocess.CalledProcessError as e:
        print("❌ Error creating .pbit:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)


# 🎯 Master Function
def convert_twbx_to_pbit(twbx_file):
    print("🚀 Starting conversion pipeline...")

    extracted = extract_twbx(twbx_file)
    twb = find_twb_file(extracted)
    tableau_data = parse_twb(twb)
    bim = convert_to_bim(tableau_data)
    save_bim_model(bim,"model.bim")
    generate_pbit_from_bim("model.bim")

    print("🎉 Done! Open the generated .pbit in Power BI Desktop.")


# 📌 Call here
if __name__ == "__main__":
    your_twbx = "superstore.twbx"  # 🔁 Replace with your actual file
    convert_twbx_to_pbit(your_twbx)
