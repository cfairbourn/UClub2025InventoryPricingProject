"""

Plan
Not necessarily chain the programs together, but to consolidate the 4 programs I 
have into as small of a number I can make it.

The order of operations, really is that someone inputs a new invoice pdf into

STEP 1: An invoice that needs to be analyzed is placed into the directory
    inputs/new_invoices

STEP 2: Analyze invoice for item codes and prices and dates

STEP 3: Update master pricing with information from analyzed invoice
  STEP 3.5: 
    Any new items that are found will need to have their information
      filled out manually by looking up the item code on Sysco.
    Further, any additional pricing information from other vendors will have
      to be entered manually

STEP 4: Read in old inventory

STEP 5: Generate Deliverable

Then read in old inventory

Then generate new deliverable inventory sheet

"""


# check if new invoice is in inputs/new_invoices

import sysco.reading_sysco_invoice as sysco_inv
import master.deliverable_creation as create
import master.reading_inventory as read_inv
import master.update_pricing as update_pricing



def main():


  # run analysis of invoice
  print("Analyzing any sysco invoices")
  sysco_inv.main()

  # update master pricing doc using info gathered from invoice analysis
  print("Updating the master pricing list with info from invoice")
  update_pricing.main()

  # read old inventory to get a schema of how it's laid out
  print("Reading in old inventory information as structure for new sheet")
  read_inv.main()

  # create new inventory using schema of old inventory updated with newer pricing
  print("Creating new inventory sheet")
  create.main()


  return




if __name__ == "__main__":
  main()











