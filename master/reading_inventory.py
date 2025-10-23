"""
This is a program that will read in our current excel document that we're 
  using for inventory purposes, and to analyze it for each specific item, 
  note duplicate items, note vendor codes, and note which sections of our 
  inventory these items are stored in

"""



import pandas as pd
import json

import os
import shutil
import datetime

def move_and_archive_document(filename, origin_dir, destination_dir, remove = False):
    """
    Copies a specified file from the origin directory to the destination directory,
    appending a datetime stamp to the copied file's name. The original file
    remains in the origin directory.

    Args:
        filename (str): The name of the file to move (e.g., 'invoice_1234.pdf').
        origin_dir (str): The full path to the directory where the file currently resides.
                          Example: 'vendors/sysco/inputs'
        destination_dir (str): The full path to the directory where the file should be moved.
                               Example: 'inputs/processed'
    """
    
    # --- 1. PREPARE PATHS AND TIMESTAMP ---

    # Get the current datetime in a safe format (e.g., YYYYMMDD_HHMMSS)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Separate the filename into name and extension
    name, ext = os.path.splitext(filename)
    
    # Create the new filename: name_timestamp.ext
    new_filename = f"{name}_{timestamp}{ext}"

    # Construct the full source path (the original file)
    source_path = os.path.join(origin_dir, filename)

    # Construct the full destination path with the new filename
    destination_path = os.path.join(destination_dir, new_filename)


    # --- 2. ENSURE DESTINATION DIRECTORY EXISTS ---
    if not os.path.exists(destination_dir):
        # Create destination and any necessary parent directories
        os.makedirs(destination_dir, exist_ok=True)
        print(f"Created destination directory: {destination_dir}")

     # --- 3. COPY THE FILE ---
    try:
        shutil.copy2(source_path, destination_path)
        print(f"Archived: {filename} → {destination_path}")

        # --- 4. OPTIONALLY REMOVE ORIGINAL ---
        if remove:
            os.remove(source_path)
            print(f"Removed original file from: {origin_dir}")
        else:
            print(f"Original file retained in: {origin_dir}")

    except FileNotFoundError:
        print(f"Error: Source file not found at {source_path}")
    except Exception as e:
        print(f"Unexpected error while archiving {filename}: {e}")

    print("")
    return



# initializing dictionaries
master_dict = {}
misc_dict = {}


def update_master(master_key, row, curr_section, order):
  # have we seen this item code before?
  if master_key not in master_dict:
    # if not, add this as a new item to master_dict
    master_dict[master_key] = {
      "ITEM_DESC": [str(row["ITEM_DESC"]).upper()],
      "SECTIONS": [[curr_section, order]],
      "PRICES": [row["PRICE"]],
      "UNITS": [row["UNIT"]],
      "QUANTITY": [row["QUANTITY"]],
    }

  else: 
    # we have seen this item code before, append it's information
    vcode_info = master_dict[master_key]
    vcode_info['ITEM_DESC'].append(str(row["ITEM_DESC"]).upper())
    vcode_info['SECTIONS'].append([curr_section, order])
    vcode_info['PRICES'].append(row["PRICE"])
    vcode_info['UNITS'].append(row["UNIT"])
    vcode_info['QUANTITY'].append(row["QUANTITY"])
  
  return

def update_misc(misc_key, row, curr_section, order):
  # check to see if this item description is in misc_dict
  if misc_key not in misc_dict:
    # add new item description to dict
    misc_dict[misc_key] = {
      "SECTIONS": [[curr_section, order]],
      "PRICES": [row["PRICE"]],
      "UNITS": [row["UNIT"]],
      "QUANTITY": [row["QUANTITY"]],
    }

  else:
    # we've seen this item desc before, append info
    item_info = misc_dict[misc_key]
    item_info['SECTIONS'].append([curr_section, order])
    item_info['PRICES'].append(row["PRICE"])
    item_info['UNITS'].append(row["UNIT"])
    item_info['QUANTITY'].append(row["QUANTITY"])

  return



def main():


  # read in file
  # focus only on first 8 columns
  # look for files in inputs/inventories
  input_folder = "inputs\\inventories\\"
  input_files = [f for f in os.listdir(input_folder) if f.endswith(".xlsx")]
  # if xlsx file is found in inventories, open that filename and run
  if len(input_files) < 1:
    return 0

  ## FILE OPENING
  df = pd.read_excel("".join([input_folder, input_files[0]]))

  df.columns = [
    "INDEX", "VENDOR/BRAND", "VENDOR_CODE", "ITEM_DESC", "UNIT", "PACK", 
    "PER_PACK", "PRICE", "QUANTITY", "EST_PRICE", "TOTAL_EST_VALUE"
    ]

  section_areas = [
    "MK WALK IN", "MK BLUE RACK", "MK 4 DOOR FREEZER", "MK HOT LINE", 
    "MK HOT LINE FREEZER", "MK BACK SHELF", "UPSTAIRS ICE CREAM FREEZER", 
    "GARDE MANGER COOLER", "GARDE MANGER STATION", "BASEMENT FREEZER", 
    "BASEMENT WALK IN", "BASEMENT ICE CREAM FREEZER", "BASEMENT PROTEIN FREEZER",
    "STOREROOM", "HENRY CENTER FREEZER - SPEED RACK", "HENRY CENTER FREEZER"
  ]

  curr_section = "MK WALK IN" # first section read with excel sheet

  all_sections_info = {section: [] for section in section_areas}

  order = 0

  for i in range(df.shape[0]):

    row = df.iloc[i, :]
    # creation of keys for dictionaries
    master_key = "".join([
      str(row["VENDOR/BRAND"]), ", ", str(row["VENDOR_CODE"])]).upper()
    misc_key = "".join([
      str(row["VENDOR/BRAND"]), ", ", str(row["ITEM_DESC"])]).upper()
    
    # is this item in fact a section name?
    if row["ITEM_DESC"] in section_areas:
      curr_section = row["ITEM_DESC"]
      curr_section = curr_section.strip()
      order = 0

      continue

    

    # is this not an item, either an empty row or a column header name "ITEM_DESC"
    elif row["ITEM_DESC"] == "ITEM_DESC" or pd.isna(row["ITEM_DESC"]):
      # ignore this non-item row
      continue


    # if the row made it past this point, it is an item
    # regardless if the item code is valid or not, add the keys of the item to the 
    all_sections_info[curr_section].append([master_key, misc_key])
    order += 1
    
    # is the item code valid?
    if pd.isna(row["VENDOR_CODE"]):
      # valid item, invalid item code, add to misc_dict
      update_misc(misc_key, row, curr_section, order)
        
    else:
      update_master(master_key, row, curr_section, order)



  for filename in [
    "sections_order_info.json",
    "misc_item_locs.json",
    "vcode_locs.json"]:
    folder_name = filename.split(".")[0]
    move_and_archive_document(
      filename, "master\\schemas\\", 
      "".join(["master\\schemas\\archive\\", folder_name]))

  # save all_sections_info
  with open("master\\archive\\sections_order_info.json", "w") as file:
    json.dump(all_sections_info, file, indent = 2, ensure_ascii = False)
  
  # vcode info
  with open("master\\archive\\vcode_locs.json", "w") as file:
    json.dump(master_dict, file, indent = 2, ensure_ascii = False)

  # misc items
  with open("master\\archive\\misc_item_locs.json", "w") as file:
    json.dump(misc_dict, file, indent = 2, ensure_ascii = False)

  # move and archive the read inventory into processed_inventories
  move_and_archive_document(
    input_files[0],
    input_folder,
    "inputs\\inventories\\processed_inventories\\",
    remove = True
  )




  return




if __name__ == "__main__":
  main()
