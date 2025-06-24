import zipfile
import os
import xml.etree.ElementTree as ET
import json
import subprocess

# ========== STEP 1: Extract TWBX and Find TWB ==========
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

# ========== STEP 2: Parse TWB XML ==========
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

# ========== STEP 3: Convert to BIM ==========
def map_datatype(tableau_type):
    mapping = {
        "string": "string",
        "real": "double",
        "integer": "int64",
        "boolean": "boolean",
        "date": "DateTime"
    }
    return mapping.get(tableau_type.lower(), "string")

def convert_formula_to_dax(formula):
    if not formula:
        return "BLANK()"
    formula = formula.replace("IF ", "IF(")
    return formula  # Placeholder

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
            continue
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

# ========== STEP 4: Write PbixProj Layout ==========
def save_bim_model(bim_data, pbixproj_dir="pbixproj_model"):
    dms_dir = os.path.join(pbixproj_dir, "DataModelSchema")
    os.makedirs(dms_dir, exist_ok=True)
    bim_path = os.path.join(dms_dir, "Model.bim")
    with open(bim_path, 'w') as f:
        json.dump(bim_data, f, indent=2)
    print(f"✅ Saved BIM to {bim_path}")

def write_version_file(pbixproj_dir):
    version_path = os.path.join(pbixproj_dir, "Version.txt")
    with open(version_path, 'w') as f:
        f.write("3")
    print(f"📝 Added {version_path}")

def write_minimal_layout(pbixproj_dir):
    layout_dir = os.path.join(pbixproj_dir, "Report")
    os.makedirs(layout_dir, exist_ok=True)
    layout_path = os.path.join(layout_dir, "Layout")
    with open(layout_path, 'wb') as f:
        f.write(b'{}')  # Minimal stub
    print(f"📝 Added stub Report/Layout")

def write_static_resources(pbixproj_dir):
    layout_dir = os.path.join(pbixproj_dir, "Report")
    os.makedirs(layout_dir, exist_ok=True)
    static_path = os.path.join(layout_dir, "StaticResources.json")
    with open(static_path, 'w') as f:
        json.dump({}, f)
    print(f"📝 Added stub Report/StaticResources.json")

# ========== STEP 5: Compile to .pbit ==========
def generate_pbit_from_pbixproj(pbixproj_path, output_path="output.pbit"):
    print("🏗️  Compiling .pbit using pbi-tools...")
    try:
        result = subprocess.run([
            "pbi-tools", "compile",
            pbixproj_path,          # required
            output_path,            # outPath
            "PBIT",                 # format
            "True"                  # overwrite
        ], capture_output=True, text=True, check=True)
        print(f"✅ .pbit created at: {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ Error creating .pbit:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)


# ========== STEP 6: Master Function ==========
def convert_twbx_to_pbit(twbx_file):
    print("🚀 Starting conversion pipeline...")

    extracted = extract_twbx(twbx_file)
    twb = find_twb_file(extracted)
    tableau_data = parse_twb(twb)

    bim = convert_to_bim(tableau_data)
    pbixproj = "pbixproj_model"

    save_bim_model(bim, pbixproj)
    write_version_file(pbixproj)
    write_minimal_layout(pbixproj)
    write_static_resources(pbixproj)
    generate_pbit_from_pbixproj(pbixproj)

    print("🎉 Done! Open the generated .pbit in Power BI Desktop.")

# ========== MAIN ==========
if __name__ == "__main__":
    your_twbx = "helloworld.twbx"  # Replace with your file
    convert_twbx_to_pbit(your_twbx)
