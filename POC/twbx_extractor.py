import os
import zipfile

def extract_twbx(twbx_path, output_dir="extracted_pbit"):
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"✅ Extracted to {output_dir}")
    return output_dir

extract_twbx('OneLake Files.pbit')