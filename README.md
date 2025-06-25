# 🧩 Tableau `.twbx` to Power BI `.pbit` Converter

This Python utility converts Tableau workbooks (`.twbx`) into Power BI template files (`.pbit`) by extracting metadata, transforming it into a BIM schema, and compiling it with `pbi-tools`.

---

## 🚀 Features

- Extracts `.twb` files from `.twbx` archives
- Parses Tableau data sources, fields, joins, and calculated fields
- Converts to Power BI-compatible BIM model
- Generates a minimal Power BI project structure
- Compiles `.pbixproj` to `.pbit` using `pbi-tools`

---

## 📦 Requirements

### ✅ Python 3.13.5 (Standard Library Only)

- `zipfile`
- `os`
- `xml.etree.ElementTree`
- `json`
- `subprocess`

> No external Python packages required.

### 🛠️ External Dependency

#### [`pbi-tools`](https://pbi.tools/)

Used to compile Power BI project to `.pbit`. Install it globally:

```bash
dotnet tool install --global pbi-tools
