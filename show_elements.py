#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyPDF2",
#   "camelot-py[cv]",
# ]
# ///

import PyPDF2
import camelot
import pandas as pd
import numpy as np


def list_pdf_elements(pdf_path):
    """
    Extract and list various elements from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
    """
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # 1. Basic PDF Information
            print("\n--- PDF Metadata ---")
            metadata = pdf_reader.metadata
            if metadata:
                for key, value in metadata.items():
                    print(f"{key}: {value}")
            
            # 2. Page Count
            print(f"\n--- Total Pages: {len(pdf_reader.pages)} ---")
            
            # 3. Text Extraction
            print("\n--- Page Contents ---")
            for page_num, page in enumerate(pdf_reader.pages, 1):
                print(f"\nPage {page_num} Text:")
                print(page.extract_text())
            
            # 4. List Embedded Images (if any)
            print("\n--- Embedded Images ---")
            for page_num, page in enumerate(pdf_reader.pages, 1):
                images = page.images
                if images:
                    print(f"Page {page_num} contains {len(images)} image(s)")
                    for img_num, img in enumerate(images, 1):
                        print(f"  Image {img_num}: {img}")
                else:
                    print(f"Page {page_num} contains no images")
    
    except FileNotFoundError:
        print(f"Error: File not found at {pdf_path}")
    except PyPDF2.errors.PdfReadError:
        print("Error: Unable to read the PDF file. It might be encrypted or corrupted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def extract_cells_with_camelot(pdf_path):
      """
      Extract cells using Camelot library
      
      Returns:
         list: List of extracted cell dataframes
      """
      print("\n--- Camelot Cell Extraction ---")
      try:
         # Read tables from PDF
         tables = camelot.read_pdf(pdf_path, pages='all')
         
         cell_collections = []
         for i, table in enumerate(tables, 1):
               print(f"\n<b>Table {i} Cells:</b>")
               
               # Convert table to numpy array
               cell_array = table.df.to_numpy()
               
               # List all cells
               for row_idx, row in enumerate(cell_array):
                  for col_idx, cell_value in enumerate(row):
                     if cell_value and cell_value.strip():  # Non-empty cells
                           print(f"Cell [{row_idx},{col_idx}]: {cell_value}")
               
               cell_collections.append(cell_array)
         
         return cell_collections
      
      except Exception as e:
         print(f"Camelot cell extraction error: {e}")
         return []


pdf_path = '/Users/tom/Documents/Projects/Charlie/2025-03-03-invoices/Tim_Healy__Melinda_Fields_invoice_866.pdf' 
# list_pdf_elements(pdf_path)
extract_cells_with_camelot(pdf_path)
