








This is a project that keeps getting longer and better


main process

manual labor part:
invoices will be scanned and sent to AP email
invoices will be downloaded from AP email

(potential automation task) invoices will be identified, renamed, put into respective folders for accounting AP invoices

once invoices have been identified and moved into the correct vendor's folder, when we find that an invoice belongs to a desired vendor, also place that invoice into the inputs directory for the respective vendor's directory

when all inputs have been sorted to their respective vendors, run each vendor's scanning and analysis program for which there is an input (i have just finished this for sysco only)
  and outputs the analyzed data file into the input folder in master
  and moves the specific input into the master processed inputs

then run master inventory pricing updating program
where it will take the info files from inputs and update the master pricing list
then program will move the files into processed inputs






when creating the inventory sheet

schemas






how can I create all_sections

problem is that item order



all_sections = {
  section1 = [item 1, item 2, ...],
  section2 = [item 1, item 2, ...],
  ...
}



for section in all_sections
  grab that section_info from all_sections
  section_info could just be a list of the items in the order that they appear
  for item in section_info
    get that item's master information from master list
    display the key pieces of information from that item
      ITEM NAME / DESCRIPTION - VENDOR/BRAND
      UNIT TYPE - PACK SIZE - Q PER PACK - PRICE - [QUANTITY TO BE FILLED IN]





things I'm currently waiting on
  chef to update the current inventory list and remove the items that we aren't carrying anymore in the locations that he wants them to be
  new invoices