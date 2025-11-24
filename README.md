This program opens a CSV file of customer's information (rows) and columns of service to generate a multi-page PDF, where each page is an invoice for a customer.  The PDF will be named the same as the CSV file but with a .pdf extension and will be created in the same directory as the CSV file.

The service columns titles have the format 'MM-DD-YYYY_Plow_N' where N is the number of inches of snow, or 'MM-DD-YYYY_Sand'

The arguments to run the program are:
 - the path to the CSV file
 - a list of dates in the MM-DD-YYYY format.  Column titles will be looked up for each date, if they match then a service line will be put in the invoice.

The program requires a provider.json file in the same directory as the program which has the provider's name and address.  Optionally it can have a phone number and email address.

For each row in the CSV file, if a column title matches one of the dates provided and the cell is not empty, a service line will be added to the invoice.

The cell can be a number, in which case it is the rate for the service, or it can be a string, e.g. 'x' or 'X', in which case the rate will be retrieved from the Plow Rate or Sand Rate column for that customer (row).  If the string is a 'P', that indicates the customer has paid and an invoice will not be generated for that service.  If the string is a '-', that indicates the customer was not plowed.  Empty cells in the _Plow column generate a warning.

Some customers have 2 driveway segments - a Common (shared) driveway and a Private driveway.  For these customers, the cell should be a string, and 2 service lines will be added to the invoice - one for the common driveway and one for the private driveway.  The common driveway service line will use the rate from the CommonRate column.
