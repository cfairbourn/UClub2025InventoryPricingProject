


This project was created by Colin W Fairbourn (he/him) during the Fall of 2025. Purpose is to assist the admin at the University Club of MSU in maintaining accurate and up to date information on their inventory by analyzing invoices given to us by Sysco, gathering the information on any and all items purchased and their price, so that when inventory is counted, they have accurate and recent prices on any items are in inventory.


___


- Process - This is a multi step process. Where each step requires manual action / input.
  1. Place a scanned Sysco invoice into 'inputs\\invoices\\' where the every page that is a tabular invoice of all items purchased is rotated so that the top of the landscape page would be on the right hand side in portrait.
  2. Run 'read_invoice_update_master.py'
  3. With access to an account to log into Sysco's shopping website, open the updated file 'deliverables\\master_inventory.csv', for any item that is flagged for review, or that lacks important information, input that item code into Sysco's search bar, find the item, and enter the information from the website, like vendor, item desc, unit, pack size, quantity per pack, etc.
  4. Assuming an older inventory has been placed in 'inputs\\inventories\\', and that no major change has been made to the format of the excel document, such as no changing the order of columns, or the number of columns, either by removing or adding more, run 'generate_inventory_sheet.py'
  5. In 'deliverables\\printable_inventory_sheet.xlsx', hide any columns that might be deemed unnecessary for the counter. Recommended columns include 'VENDOR_CODE', 'EST_PRICE', 'TOTAL_EST_PRICE', and then by printing the sheet.
  6. When inventory has been counted, and it's time to enter the counts, it is recommended that a copy of the 'printable_inventory_sheet.xlsx' is created and that the counts are entered into this copy, along with any minor changes (like adding, removing, or moving items and/or rows). This filled out and new inventory sheet is what can be used the next time this program is run and a new inventory sheet is created.

___

- Directories:
  - deliverables\\:
    - This directory exists as an outputs, or as the deliverables of this project
  - inputs\\:
    - This directory exists as a location for new inputs to be placed, as well as an organization structure that moves older used and processed files into their respective processed folder within that specific input type directory
    - inventories\\:
      - Whenever an old inventory needs to be used as a structure template for the new inventory to be created, the old inventory must be placed in this directory, with the name of it being unimportant, so long as it is a '.xlsx' file type. It is recommended that the old excel sheet being used for inventory is a copy of the original inventory. 
    - invoices\\:
      - Whenever a new sysco invoice is scanned, it should go into this folder. The name of it is unimportant, so long as it is a '.pdf' file type.
  - master\\:
    - archive\\:
      - This directory exists to contain any and all old iterations of the 'master_inventory_list.csv'
    - inputs\\:
      - This directory exists as the destination for where info collected from scanned pdf files will be found. It also contains within it the directory for all old input files.
    - schemas\\:
      - This directory exists as a location for stored information about inventory's structure that is necessary beyond the master_inventory.csv, including:
        - misc_item_locs.json
          - .json file containing information about items that we don't have as specific vendor codes and vendor information for
        - section_order_info.json
          - .json file containing information about what sections contain which items as well as recording and preserving their order
        - vcode_locs.json
          - .json file containing information about items that we specifically have vendor code and vendor information for
      - archive\\:
        - This directory has 3 subdirectories, all of which exist as the respective archived files of old structures
    - master_inventory.csv
      - This file is an editable file that is a list containing every item we've ever purchased from Sysco as well as it's details such as vendor information and pricing. 
    - deliverable_creation.py
      - This is a program, step 4 and final step in the process. This program reads in the structure '.json' files, then creates and formats the excel spreadsheet that would be printed and used for counting inventory at end of month.
    - reading_inventory.py
      - This is a program, step 3 in the overall process, that reads in the previous inventory excel spreadsheet, gathers the information about what sections have what items, what sections are specific items in, and what sections are specific vendor codes in, as well as the order that all of this shows up in.
    - update_pricing.py
      - This is a program, step 2 in the overall process, that contains information gathered from 'reading_sysco_invoice.py', in the '.csv' file that is placed in 'master\\inputs' and updates the already existing 'master_inventory_list.csv' as well as archiving the old file.
  - sysco
    - references\\:
      - This directory exists to contain images of example Sysco Invoice sheets, the purpose of which is to help 'reading_sysco_invoice.py' identify which images in the '.pdf' file are pages with information worth extracting. 
    - sysco_source\\:
      - This is a directory containing only the source file for 'reading_sysco_invoice.py' containing a lot of functions and variables that are used in that program.
    - reading_sysco_invoice.py:
      - This is a program, step 1 in the overall process, that intakes a '.pdf' file inside the directory 'inputs\\invoices', assuming it's a sysco invoice, analyzes each page for it's textual information, and builds a '.csv' file with all of the items present on that invoice. 
- Programs
  - generate_inventory_sheet.py
    - This is a two step program, where each step is handled by another program.
      1. reading_inventory.py
      2. deliverable_creation.py
  - read_invoice_update_master.py
    - This is another two step program, where each step is handled by another program.
      1. reading_sysco_invoice.py
      2. update_pricing.py


___

