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


# def save_analyzed_document(filename, origin_dir, destination_dir, date):
#   """
#   Moves a specified file from the origin directory to the destination directory.

#   This function is generalized to handle any file movement by taking 
#   the full source and destination directories as arguments.

#   Args:
#       filename (str): The name of the file to move (e.g., 'invoice_1234.pdf').
#       origin_dir (str): The full path to the directory where the file currently resides.
#                         Example: 'vendors/sysco/inputs'
#       destination_dir (str): The full path to the directory where the file should be moved.
#                               Example: 'inputs/processed'
#   """
  
#   # Construct the full source path: origin_dir/filename
#   source_path = os.path.join(origin_dir, filename)

#   # Construct the full destination path: destination_dir/filename
#   destination_path = os.path.join(destination_dir, filename)

#   # Ensure the destination directory exists
#   if not os.path.exists(destination_dir):
#     # Use exist_ok=True to prevent an error if the directory already exists 
#     # (though the check above handles that), and parents=True to create 
#     # any necessary parent directories.
#     os.makedirs(destination_dir, exist_ok=True)
#     print(f"Created destination directory: {destination_dir}")

#   try:
#     # Move the file using shutil.move()
#     shutil.move(source_path, destination_path)
#     print(f"Successfully moved: {filename}")
#     print(f"From: {source_path}")
#     print(f"To: {destination_path}")

#   except FileNotFoundError:
#     print(f"Error: Source file not found at {source_path}")
#   except Exception as e:
#     print(f"An unexpected error occurred while moving the file: {e}")

#   print("")

#   return




def move_and_archive_document(filename, origin_dir, destination_dir):
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
        # Use shutil.copy2() to copy the file (including metadata)
        # The file remains in source_path (origin_dir)
        shutil.copy2(source_path, destination_path)
        
        print(f"Successfully archived: {filename}")
        print(f"Original file saved in: {origin_dir}")
        print(f"Archived copy moved to: {destination_dir}")
        print(f"New archived filename: {new_filename}")

    except FileNotFoundError:
        print(f"Error: Source file not found at {source_path}")
    except Exception as e:
        print(f"An unexpected error occurred while archiving the file: {e}")

    print("")
    return



def main():

  # --- Read in master list ---
  # Get the current datetime in a safe format (e.g., YYYYMMDD_HHMMSS)
  timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
  master = pd.read_csv("deliverables/master_inventory_list.csv", dtype={'VENDOR_CODE': int})
  # make sure LAST_UPDATE is datetime
  master["LAST_UPDATE"] = pd.to_datetime(master["LAST_UPDATE"])  

  # --- Read in all new input files ---
  input_folder = "master\\inputs"
  output_folder = "master\\archive"
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
          master.loc[idx, "UNIT_PRICE"] = item["UNIT_PRICE"]
          master.loc[idx, "LAST_UPDATE"] = new_date
        
        master.loc[idx, "ACCOUNT"] = item["ACCOUNT"]

      else:
        # New item → add to master + flag
        item_dict = item.to_dict()
        item_dict["FLAG"] = "Needs Review"
        master = pd.concat([master, pd.DataFrame([item_dict])], ignore_index=True)

    # move invoice
    move_and_archive_document(file, input_folder, output_folder)

  # --- Save updated master list ---
  master.to_csv("deliverables/master_inventory.csv", index=False)
    # --- 2. ENSURE DESTINATION DIRECTORY EXISTS ---
  if not os.path.exists("master\\archive\\"):
      # Create destination and any necessary parent directories
      os.makedirs("master\\archive\\", exist_ok=True)
      print(f"Created destination directory: {"master\\archive\\"}")
  new_filename = f"{"master\\archive\\master_inventory"}_{timestamp}{"csv"}"
  master.to_csv(new_filename, index = False)
  # move invoice

  return





if __name__ == "__main__":
  main()







