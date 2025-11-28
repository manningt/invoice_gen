#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "fpdf2",
# ]
# ///

from fpdf import FPDF
import csv
import json
import argparse
from datetime import datetime
import math
import itertools
import sys

try:
   from fpdf import FPDF
except Exception as e:
   print(e)
   sys.exit(1)

def depth_rate_adjustment(depth, base_rate):
   if depth <= 6:
      return base_rate
   elif depth <= 9:  
      return math.trunc(base_rate * 1.5)
   elif depth <= 12:
      return math.trunc(base_rate * 2.25)
   elif depth <= 18:
      return math.trunc(base_rate * 3.0)
   elif depth <= 24:
      return math.trunc(base_rate * 3.75)
   elif depth <= 32:
      return math.trunc(base_rate * 4.5)
   else:
      return None

class InvoicePDFGenerator:
   def __init__(self):
      self.pdf = FPDF(orientation="P", unit="in", format="Letter")
      self.left_edge = 0.7
      self.pdf.set_margin(self.left_edge)
      self.billing_date = datetime.now().strftime("%m/%d/%Y")

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

   def add_customer_info(self, email=None, account=None, invoice_number=None, \
         name=None, address1=None, city_st_zip=None, terms=None):
      self.pdf.set_y(1.0)
      with self.pdf.table(col_widths=(35,6,11,12), width=5, align="Right", line_height=self.text_14_height, padding=0.04) as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Customer E-mail', 'Acct', 'Date', 'Invoice'])
         self.pdf.set_font('Times')
         customer_info = [email, account, self.billing_date, invoice_number]
         row = table.row(customer_info)
      self.pdf.set_y(2.0)
      with self.pdf.table(width=3, align="Left", line_height=0.16, padding=0.06) as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Bill To:'])
         self.pdf.set_font('Times')
         customer_info = f"{name}\n{address1}\n{city_st_zip}"
         row = table.row([customer_info])
      self.pdf.set_y(2.2)
      with self.pdf.table(width=2, align="Right", line_height=self.text_14_height, padding=0.04, text_align="C") as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Terms'])
         self.pdf.set_font('Times')
         row = table.row([terms])

   def add_line_items(self, line_items, total=0):
      # print(f'Adding line items: {line_items}')
      self.pdf.set_y(3.8)
      with self.pdf.table(col_widths=(10,52,8,10), width=6, align="Center", line_height=self.text_14_height, \
            padding=0.04, text_align="C") as table:
         self.pdf.set_font('Helvetica', size=11)
         row = table.row(['Quantity', 'Description', 'Rate', 'Amount'])
         self.pdf.set_font('Times')
         for item in line_items:
            row = table.row()
            row.cell(item[0], align="R")
            row.cell(item[1], align="L")
            row.cell(item[2], align="R")
            row.cell(str(item[3]), align="R")
         row = table.row()
         self.pdf.set_font('Helvetica', style='B', size=14)
         row.cell('')
         row.cell('Total:', align="R")
         row.cell('')
         row.cell(total, align="R")

   def finish(self, out_pdf_path):
      self.pdf.output(out_pdf_path)

def add_line_items_to_dict(customer_dict, dates_list):
   # the customer_dict is an iterator of csv.DictReader object
   # There can be multiple columns for each date;  each column is a service to be added to the invoice.
   # The column names are:
   #  of the form "MM-DD-YYYY_Plow_N" where N is the number of inches of snow, or "MM-DD-YYYY_Sand"
   #  parsed to extract Plow or Sand, and the number of inches of snow
   # The value of the service can be: (the value is the cell for that customer and column):
   #    a number, in which case it is the rate for the service;  the number has to be > 9
   #    a 'P', in which case the customer has paid and an invoice will not be generated for that service
   #    a '-', or empty string, in which case the customer was not plowed
   #    a string,.e.g. x, in which case the rate will be retrieved from the Plow Rate or Sand Rate column for that customer (row)
   row_count = 0
   for row in customer_dict:
      # print(row)
      items = []
      total_amount = 0
      for date in dates_list:
         services = [key for key in row if key.startswith(date)]
         # if row_count < 3:
         #    print(f'{row["Bill to 1"]} {date=} {services=}')
         for service in services:
            if row[service] == '' or row[service] == '-':
               continue # skip empty cells
            if row[service].lower() == 'p':
               row["Paid"] = True
               continue # skip paid cells
            # if row_count < 3:
            #    print(f'  {row["Bill to 1"]}{service}: {row[service]} type={type(row[service])}')

            # use the rate from the service column if it is a valid number (applies to sanding and plowing columns)
            try:
               rate = float(row[service])
               if rate < 10:  # skip rates that are too low to be valid
                  print(f'Invalid rate {rate} for {row["Bill to 1"]} on {date}, using rate from Plow/Sand Rate column')
                  rate = None
            except:
               rate = None
 
            if 'Plow' in service:
               if rate is None:
                  try:
                     rate = float(row["PlowRate"])
                  except:
                     print(f'Could not parse rate {row["PlowRate"]} in {service} for {row["Bill to 1"]} -> skipping')
                     continue
               
               service_parts = service.split('_')
               try:
                  depth = int(service_parts[2])
               except:
                  print(f'Could not parse snow depth from "{service}" for {row["Bill to 1"]} -> quitting')
                  sys.exit(1)

               description = f'Snow Plowing on {date} @ {depth}" '
               if len(service_parts) > 3:
                  # handle case where there is a note after the snow depth, e.g "Plow_12-25-122x_4_slush"
                  description += service_parts[3]

               # handle case where the customer has a common driveway, if so, then add a line item for the common driveway
               if row["CommonRate"] != '':
                  try:
                     common_driveway_rate = float(row["CommonRate"])
                     # print(f'Using shared_driveway_rate of {common_driveway_rate} for {row["Bill to 1"]} on {date}')
                     common_rate_before_depth_adjust = common_driveway_rate
                     common_driveway_rate = depth_rate_adjustment(depth, common_driveway_rate)
                     if common_driveway_rate is None:
                        print(f'Unusual snow depth of {depth}" for {row["Bill to 1"]} on {date}, using common rate')
                        common_driveway_rate = common_rate_before_depth_adjust
                     # print(f'Adding common driveway line item for {row["Bill to 1"]} on {date} at rate {common_driveway_rate}')
                     items.append(["1", description + "   Common Drive", f'{common_driveway_rate:.2f}', f'{common_driveway_rate:.2f}'])
                     total_amount += common_driveway_rate
                     description += "   Private Drive"
                  except Exception as e:
                     print(f'Exception {e} for {row["Bill to 1"]} on {date} while getting common_driveway_rate')
                     sys.exit(1)

               rate_before_depth_adjust = rate
               rate = depth_rate_adjustment(depth, rate)
               if rate is None:
                  print(f'Unusual snow depth of {depth}" for {row["Bill to 1"]} on {date}, using base rate')
                  rate = rate_before_depth_adjust

            if 'Sand' in service:
               if rate is None:
                  try:
                     rate = float(row["SandRate"])
                  except:
                     print(f'No valid sand rate for {row["Bill to 1"]} on {date}, skipping sanding line item')
                     continue
               description = f'Sanding on {date}'

            rate_str = f"{rate:.2f}"
            items.append(["1", description, rate_str, rate_str])
            total_amount += rate
      
      if len(items) == 0:
         # print(f'No services found for {row["Bill to 1"]}, skipping invoice generation')
         continue
      else:
         row["Line Items"] = items
         row["Total Amount"] = f'{total_amount:.2f}'
         # print(row)
      row_count += 1
      # if row_count < 3:
      #    print(row)
      # if row_count == 2:
      #    return
         

def generate_text_report(customer_dict, filename):
   with open(filename, "w") as f:
      for row in customer_dict:
         f.write(f'{row["Bill to 1"]:30} ')
         if "Total Amount" not in row:
            comment = 'No Invoice'
            if 'Paid' in row and row['Paid']:
               comment += ': Paid'
            f.write(f'{comment:18}\n')
         else:
            f.write(f'Total=${row["Total Amount"]}')
            if 'Main Email' in row and row['Main Email'] == '':
               f.write(f' (No Email)')
            f.write('\n')
               
def generate_pdf_report(customer_dict, filename, rows_per_page=22, service_dates=[]):

   # TODO: add service dates to page title; specify number of customers per page
   # build customer list to be used in tables

   table_data = []
   for data_row in customer_dict:
      if "Total Amount" not in data_row:
         amount = "--"
      else:
         amount = "$" + data_row["Total Amount"][:-3]
      if "Paid" in data_row:
         paid = "Y"
      else:
         paid = "N"
      if "Main Email" in data_row and data_row["Main Email"] != '':
         email = "Y"
      else:
         email = ""         
      table_data.append([amount, paid, data_row["Bill to 1"], email])

   current_table_row_number = 0

   pdf = FPDF(orientation="P", unit="pt", format=(612,792))
   pdf.set_margins(12, 12, 12) #left, top, right in points
   pdf.set_auto_page_break(auto=False)
   widths = (36, 32, 160, 36)

   for page_number in range(4):
      pdf.add_page()
      pdf.set_font("Helvetica", "B")
      pdf.cell(0,0, f'Page {page_number+1} of 4     service dates: {', '.join(service_dates)}', align="L")
      pdf.ln(pdf.font_size+4)

      with pdf.table(align="l", line_height=24, padding=2, width=sum(widths), col_widths=widths) as table:
         pdf.set_font("Helvetica", "B") # Arial not available in fpdf2
         row = table.row()
         row.cell("Total")
         row.cell("Paid")
         row.cell("Name")
         row.cell("email")
         pdf.set_font("Helvetica")
         for page_row_count in range(rows_per_page):
            row = table.row()
            for i in range(4):
               row.cell(table_data[current_table_row_number][i])
            current_table_row_number += 1
            if current_table_row_number == len(table_data):
               break
                     
   pdf.output(filename)


if __name__ == "__main__":

   argParser = argparse.ArgumentParser()
   argParser.add_argument("inputCSV", type=str, help="input CSV filename with path")
   argParser.add_argument("dates", nargs='*', type=str, help="service dates (MM-DD-YYYY)")
   args = argParser.parse_args()
   # print(f'\n\t{args.input=} {args.dates=}')

   try:
      provider_dict = json.load(open("provider.json"))
   except Exception as e:
      sys.exit(f"Could not open provider.json file: {e}")

   try:
      customer_dict = csv.DictReader(open(args.inputCSV))
   except Exception as e:
      sys.exit(f"Could not open customer_list.csv: {e}")

   iterator1, iterator2, iterator3, iterator4 = itertools.tee(customer_dict, 4)

   add_line_items_to_dict(iterator1, args.dates)
   # for row in iterator2:
   #    print(row)
   #    break

   current_date = datetime.now()
   date_str = f'{current_date.strftime("%y%m%d")}'

   invoices = InvoicePDFGenerator()
   row_count = 0
   for row in iterator3:
      if "Line Items" not in row or len(row["Line Items"]) == 0:
         # print(f'No Line Items found for {row["Bill to 1"]}, skipping invoice generation')
         continue
      else:
         # print(f'Generating invoice for {row["Bill to 1"]}')
         invoices.new_page(provider_dict)
         invoices.add_customer_info(email=row["Main Email"], account=row["Account No."], 
            invoice_number=f'{date_str}.{row["Account No."]}', 
            name=row["Bill to 1"], address1=row["Bill to 2"], city_st_zip=row["Bill to 3"], 
            terms=row["Terms"])
         invoices.add_line_items(line_items=row["Line Items"], total=row["Total Amount"])
         row_count += 1
 
   pdf_filename = f'{current_date.strftime("%Y-%m-%d")}_invoices.pdf'
   invoices.finish(pdf_filename)

   report_basename = f'{current_date.strftime("%Y-%m-%d")}_report'
   # generate_text_report(iterator4, report_basename + ".txt")
   generate_pdf_report(iterator4, report_basename + ".pdf", service_dates=args.dates)
