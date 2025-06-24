import json
from collections import defaultdict

# Path to your Model.bim file
model_path = "Model.bim"

# Load the file
with open(model_path, "r", encoding="utf-8") as f:
    model = json.load(f)

tables = model["model"]["tables"]

for table in tables:
    table_name = table.get("name", "<unnamed>")

    # Clean columns
    seen = set()
    clean_columns = []
    for col in table.get("columns", []):
        if col["name"] not in seen:
            clean_columns.append(col)
            seen.add(col["name"])
        else:
            print(f"🧹 Removed duplicate column '{col['name']}' from table '{table_name}'")

    table["columns"] = clean_columns

    # Clean measures
    seen = set()
    clean_measures = []
    for m in table.get("measures", []):
        if m["name"] not in seen:
            clean_measures.append(m)
            seen.add(m["name"])
        else:
            print(f"🧹 Removed duplicate measure '{m['name']}' from table '{table_name}'")

    table["measures"] = clean_measures

# Optionally: deduplicate table names too
seen_tables = set()
unique_tables = []
for table in tables:
    name = table["name"]
    if name not in seen_tables:
        unique_tables.append(table)
        seen_tables.add(name)
    else:
        print(f"🧹 Removed entire duplicate table '{name}'")

model["model"]["tables"] = unique_tables

# Save cleaned file
with open(model_path, "w", encoding="utf-8") as f:
    json.dump(model, f, indent=2)

print("✅ Cleaned and saved Model.bim")
