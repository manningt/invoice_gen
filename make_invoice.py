#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "fpdf2>=2.7.0",
# ]
# ///

from fpdf import FPDF
from csv import reader
import argparse
# import tkinter as tk
# from tkinter import filedialog
import sys

class InvoicePDFGenerator:
   def __init__(self, out_pdf_path):
      self.out_pdf_path = out_pdf_path
      self.pdf = FPDF(orientation="P", unit="in", format="Letter")
      self.left_edge = 0.7
      self.pdf.set_margin(self.left_edge)
      self.pdf.add_page()
      self.top = self.pdf.get_y()

      self.pdf.set_font('Helvetica', style='B', size=24)
      self.pdf.cell(0,0,text="Invoice", align="R")
      # self.pdf.set_y(top)

      self.pdf.set_font('Helvetica', size=12)
      self.text_top = 0.7
      self.text_14_height = 0.2
      self.pdf.text(self.left_edge, self.text_top,"Charlie Spencer")
      self.pdf.text(self.left_edge, self.text_top + self.text_14_height,"83 Ash St")
      self.pdf.text(self.left_edge, self.text_top + (self.text_14_height * 2),"W. Newbury, MA 01985")


   def add_customer_info(self, customer_info_dict={}):
      self.pdf.set_y(1.0)
      with self.pdf.table(col_widths=(35,9,11,8), width=5, align="Right", line_height=self.text_14_height, padding=0.04) as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Customer E-mail', 'Account', 'Date', 'Invoice'])
         self.pdf.set_font('Times')
         customer_info = ['melinda.fields@cbrealty.com', '163', '12/12/2025', '1024']
         row = table.row(customer_info)

      self.pdf.set_y(2.0)
      with self.pdf.table(width=3, align="Left", line_height=0.16, padding=0.06) as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Bill To:'])
         self.pdf.set_font('Times')
         customer_info = "Charlie Spencer\n83 Ash St\nW. Newbury, MA 01985",
         row = table.row(customer_info)


   def finish(self):
      self.pdf.output(self.out_pdf_path)


if __name__ == "__main__":
   # default_auth_path = "email_credentials.json"

   this_invoice = InvoicePDFGenerator("invoice_blank.pdf")
   this_invoice.add_customer_info()
   this_invoice.finish()
   sys.exit(0)

   argParser = argparse.ArgumentParser()
   argParser.add_argument("input", type=str, help="input CSV filename with path")
   # argParser.add_argument("-c", "--auth_path", help="path to credentails file", nargs='?',
   #             const=default_auth_path, default=default_auth_path, type=str)
   # # store_false will default to True when the command-line argument is not present
   # argParser.add_argument("-p", "--parse_only", action='store_true', help="if false, dont output PDFs or email - parse only")
   # argParser.add_argument("-d", "--dont_email", action='store_true', help="if true, dont send emails")
   args = argParser.parse_args()
   print(f'\n\t{args.input= }')

   # if args.input is None:
   #    pdf_filename = pick_file()
   #    if pdf_filename is None:
   #       sys.exit("No PDF files selected to parse.")
   #    pdf_filename = f'../{pdf_filename}'
   # else:
   #    pdf_filename = args.input
