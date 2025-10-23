"""
algorithm

read in new items information
read in master list

loop through each file found in new_inputs
  loop through each item seen in an invoice
    if item in master list
      if item date is newer than master list update date
        update item price and update date
      else 
        ignore it
    else 
      add it to the list, fill in as much information, flag for manual review
"""









import pandas as pd
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




def main():

  # Read in master list from deliverables
  master = pd.read_csv("deliverables\\master_inventory_list.csv", dtype={'VENDOR_CODE': int})
  # make sure LAST_UPDATE is datetime
  master["LAST_UPDATE"] = pd.to_datetime(master["LAST_UPDATE"])  

  # --- Read in all new input files ---
  input_folder = "master\\inputs"
  output_folder = "master\\inputs\\processed_inputs\\"
  input_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

  for file in input_files:
    new_pricing = pd.read_csv(os.path.join(input_folder, file), dtype={'VENDOR_CODE': int})
    new_pricing["LAST_UPDATE"] = pd.to_datetime(new_pricing["LAST_UPDATE"], errors="coerce")
    new_pricing = new_pricing.drop(["Unnamed: 0","PAGE"], axis = 1)

    # Loop through each row (new item)
    for _, item in new_pricing.iterrows():
      vendor_code = item["VENDOR_CODE"]

      if vendor_code in master["VENDOR_CODE"].values:
        # Get index of master row
        idx = master.index[master["VENDOR_CODE"] == vendor_code][0]
        new_date = item["LAST_UPDATE"]
        old_date = master.loc[idx, "LAST_UPDATE"]

        # Compare dates
        if new_date > old_date:
          # update
          master.loc[idx, "PRICE"] = item["PRICE"]
          master.loc[idx, "LAST_UPDATE"] = new_date
        
        master.loc[idx, "ACCOUNT"] = item["ACCOUNT"]

      else:
        # New item → add to master + flag
        item_dict = item.to_dict()
        item_dict["FLAG"] = "Needs Review"
        master = pd.concat([master, pd.DataFrame([item_dict])], ignore_index=True)

    # move invoice
    move_and_archive_document(file, input_folder, output_folder)

  
    # --- 2. ENSURE DESTINATION DIRECTORY EXISTS ---
  if not os.path.exists("master\\archive\\"):
    # Create destination and any necessary parent directories
    os.makedirs("master\\archive\\", exist_ok=True)
    print(f"Created destination directory: {"master\\archive\\"}")

  # move master list from master file to the archive
  move_and_archive_document(
    "master_inventory_list.csv",
    "deliverables\\",
    "master\\archive\\")

  # Save updated master list 
  master.to_csv("deliverables\\master_inventory_list.csv", index=False)
  


  # move invoice



  return





if __name__ == "__main__":
  main()







