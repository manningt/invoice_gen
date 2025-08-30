#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "fpdf2>=2.7.0",
# ]
# ///

from fpdf import FPDF
import csv
import json
import argparse
from datetime import datetime
# import tkinter as tk
# from tkinter import filedialog
import sys

class InvoicePDFGenerator:
   def __init__(self):
      self.pdf = FPDF(orientation="P", unit="in", format="Letter")
      self.left_edge = 0.7
      self.pdf.set_margin(self.left_edge)

   def new_page(self, provider_dict):
      self.pdf.add_page()
      self.top = self.pdf.get_y()

      self.pdf.set_font('Helvetica', style='B', size=24)
      self.pdf.cell(0,0,text="Invoice", align="R")
      # self.pdf.set_y(top)

      self.pdf.set_font('Helvetica', size=12)
      self.text_top = 0.7
      self.text_14_height = 0.2
      self.pdf.text(self.left_edge, self.text_top, provider_dict["name"])
      self.pdf.text(self.left_edge, self.text_top + self.text_14_height, provider_dict["address1"])
      city_state_zip = f'{provider_dict["city"]}, {provider_dict["state"]} {provider_dict["postalCode"]}'
      self.pdf.text(self.left_edge, self.text_top + (self.text_14_height * 2), city_state_zip)

   def add_customer_info(self, email=None, account=None, date=None, invoice_number=None, \
         name=None, address1=None, city_st_zip=None):
      self.pdf.set_y(1.0)
      with self.pdf.table(col_widths=(35,9,11,8), width=5, align="Right", line_height=self.text_14_height, padding=0.04) as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Customer E-mail', 'Account', 'Date', 'Invoice'])
         self.pdf.set_font('Times')
         customer_info = [email, account, date, invoice_number]
         row = table.row(customer_info)
      self.pdf.set_y(2.0)
      with self.pdf.table(width=3, align="Left", line_height=0.16, padding=0.06) as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Bill To:'])
         self.pdf.set_font('Times')
         customer_info = f"{name}\n{address1}\n{city_st_zip}"
         # row = table.row(customer_info) # this gives an error
         row = table.row()
         row.cell(customer_info)         


   def finish(self, out_pdf_path):
      self.pdf.output(out_pdf_path)


if __name__ == "__main__":
   # default_auth_path = "email_credentials.json"
   current_date = datetime.now()
   billing_date = current_date.strftime("%m/%d/%Y")

   try:
      provider_dict = json.load(open("provider.json"))
   except Exception as e:
      sys.exit(f"Could not open provider.json file: {e}")

   try:
      customer_dict = csv.DictReader(open('2025-09-03-customer_list.csv'))
   except Exception as e:
      sys.exit(f"Could not open customer_list.csv: {e}")

   invoices = InvoicePDFGenerator()

   page_count = 0
   for row in customer_dict:
      invoices.new_page(provider_dict)
      # print(row)
      invoices.add_customer_info(email=row["Main Email"], account=row["Account No."], date=billing_date, \
         invoice_number="TBD", name=row["Bill to 1"], address1=row["Bill to 2"], city_st_zip=row["Bill to 3"])
      page_count += 1
      if page_count > 2:
         break
   
   invoices.finish("invoice_blank.pdf")
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
