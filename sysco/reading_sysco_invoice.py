"""
Developed by Colin W Fairbourn 2025 October 1

Automated Sysco Invoice Data Extraction and Sanitization Pipeline.

This program processes a multi-page PDF document containing scanned Sysco invoices. 
It uses image processing (OpenCV), visual hashing, and Optical Character Recognition 
(Tesseract) to isolate key data points (Item Codes, Unit Prices, Invoice Date, Account). 
The extracted data is then sanitized for consistency and stored in structured CSV files.

The pipeline ensures data quality through multiple checks:
1. Invoice Page Verification: Uses perceptual hashing to identify actual invoice sheets.
2. Temporal Validation: Sanitizes dates, ensuring chronological order and consistency.
3. Pricing Reconciliation: Cross-validates prices extracted from two separate columns 
   to correct OCR errors, using positional and substring matching.

Outputs include a final inventory DataFrame (`inv_info.csv`) and a separate log of 
any processing errors encountered (`error_info.csv`).

Dependencies:
  - fitz (PyMuPDF)
  - PIL (Pillow)
  - pytesseract
  - pandas
  - imagehash
  - numpy
  - opencv-python (cv2)
  - sysco_source (Local utility module)

Execution:
  - Requires Tesseract OCR to be installed and the path to the executable set correctly.
  - Requires predefined template images for visual hashing and boundary constants 
    in 'sysco_source.py'.
"""


## SETUP
import imagehash
import fitz
from PIL import Image
import pytesseract as tess
import pandas as pd
import io
import os
import sysco_source as ss
import time
import warnings



warnings.filterwarnings(
  "ignore", 
  category=FutureWarning, 
  module="pandas"
) 







def main():

  # Set Tesseract path (Should ideally be in main or config file)
  tess.pytesseract.tesseract_cmd = r'C:\\Users\\fairbou2\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

  # Confirm Tesseract is working
  try: 
      tess.get_tesseract_version()
  except Exception as tesseract_error:
      print(f"Tesseract Error: {tesseract_error}")
  
  # sysco reference sheet
  ref_hash = imagehash.average_hash(Image.open(
    "sysco/references/sysco.png"
    ))

  
  ## FILE OPENING
  input_folder = "inputs\\invoices"
  input_files = [f for f in os.listdir(input_folder) if f.endswith(".pdf")]

  if len(input_files) < 1:
    print(f"No '.pdf' documents found in {input_folder}.")
    return 0

  n_docs = len(input_files)
  start_time = time.time()
  error_info = []

  for doc_num, file in enumerate(input_files):
    # opening desired scanned file
    file_path = os.path.join(input_folder, file)    
    doc = fitz.open(
      file_path
    )

    ## INITIALIZATION OF VARIABLES
    date_list = []
    pricing_data = []

    n_pages = len(doc)

    # start timer
    print(f"Analyzing {n_pages} pages in doc {doc_num + 1}/{n_docs}, {file}")
    
    ## MAIN PROCESSING LOOP
    for page_num in range(n_pages):
      
      ## EXTRACTING INDIVIDUAL SHEET FROM PDF FORMAT
      img = doc[page_num].get_images(full = True)[0]
      image_bytes = doc.extract_image(img[0])["image"]
      img_pil = Image.open(io.BytesIO(image_bytes))


      ## ADD ETL AND PROGRESS DISPLAY HERE
      ss.display_time(doc_num, page_num, start_time, n_pages, n_docs)
      

      ## ANALYZE INDIVIDUAL SHEET
      if ss.is_invoice(img_pil, ref_hash):

        ## POLISHING UP IMAGE  
        invoice = ss.polish_image(img_pil)
        height, width = invoice.shape

        # calculating general boundaries for cropping
        icup_area = [ss.table_bounds * height, ss.icup_bounds * width]
        up_area = [ss.table_bounds * height, ss.up_bounds * width]
        date_area = [ss.d_height * height, ss.d_width * width]
        ac_area = [ss.ac_height * height, ss.ac_width * width]

        
        ## Both ItemCodes and UnitPrices (icup) 
        icup_img = ss.crop_image(invoice, icup_area, "icup")
        icup_pairs = ss.extract_text(icup_img, ss.icup_config, ss.icup_regex)
        ## Unit Prices
        up_img = ss.crop_image(invoice, up_area, "up")
        up_list = ss.extract_text(up_img, ss.up_config, ss.up_regex)
        # sanitizing pricing
        pricing_error, new_pricing = ss.sanitize_pricing(icup_pairs, up_list)

        ## Invoice Date
        date_img = ss.crop_image(invoice, date_area, "LAST_UPDATE")
        date_text = ss.extract_text(date_img, ss.date_config, ss.date_regex)
        # sanitizing and updating date_list
        date_error, date_page, date_list = ss.sanitize_date(date_text, date_list)
        
        ## Invoice Account
        account_img = ss.crop_image(invoice, ac_area, "account")
        account_text = ss.extract_text(account_img, ss.account_config, ss.account_regex)
        # sanitizing account
        account_error, account_invoice = ss.sanitize_account(account_text)
      

        # checking for errors on this page
        if any([pricing_error, date_error, account_error]):
          error_print = [
            f"--- ERROR in Document: {file} ---\n", 
            f"Data mismatch on page {int(page_num + 1)}:\n",
            f"\t- Pairs Detected: {len(icup_pairs)}\n",
            f"\t- Prices Detected: {len(up_list)}\n",
            f"\t- Invoice Date: {date_page}\n",
            f"\t- Account: {account_invoice}\n"
            ]
          error_out = {
            "DOC": file,
            "PAGE": int(page_num + 1),
            "PAIRS": len(icup_pairs),
            "PRICES": len(up_list),
            "DATE": date_page,
            "ACCOUNT": account_invoice
          }
          error_info.append(error_out)
          print("".join(error_print))
          print("")

        # add new_pricing to total 
        for row in new_pricing:
          pricing_data.append({
            "VENDOR_CODE": row["VENDOR_CODE"], 
            "UNIT_PRICE": row["UNIT_PRICE"], 
            "LAST_UPDATE": date_page, 
            "ACCOUNT": account_invoice,
            "PAGE": int(page_num + 1)
          })


    ## if we have finished analyzing a document, move that document from 
    # vendors/sysco/inputs into inputs\\processed
    doc.close()
    processed_path = os.path.join('inputs\\invoices','processed_invoices')
    ss.move_analyzed_document(file, input_folder, processed_path)



  ## FINAL OUTPUT PROCESSING
  info_directory = 'master\\inputs'
  error_directory = 'master\\errors'


  if not os.path.exists(info_directory):
    os.makedirs(info_directory)
  if not os.path.exists(error_directory):
    os.makedirs(error_directory)
  

  info_path = os.path.join(info_directory, "sysco_info.csv")
  # error_path = os.path.join(error_directory, "sysco_error.csv")
  
  # save inventory info
  inv_info = pd.DataFrame(
    pricing_data,
    columns = ["VENDOR_CODE", "PRICE", "LAST_UPDATE", "ACCOUNT","PAGE"])

  # --- 4. Group, Sort, and Select the Newest Row per Group (The Python Equivalent) ---

  # The most efficient and idiomatic way in pandas to get the newest row
  # for each group is to sort and then use drop_duplicates.

  newest_prices = inv_info \
    .sort_values(by='LAST_UPDATE', ascending=False) \
    .drop_duplicates(subset=['VENDOR_CODE'], keep='first')

  newest_prices.to_csv(info_path)

  # save error info
  # error_df = pd.DataFrame(
  #   error_info, columns = ["DOC", "PAGE", "PAIRS", "PRICES", "DATE", "ACCOUNT"])

  # error_df.to_csv(error_path)

  # final cleanup message
  print("\nAnalysis complete. Results saved to CSV files.")

  # move file from inputs into processed_inputs

  return 0



## EXECUTION BLOCK
if __name__ == "__main__":
  main()