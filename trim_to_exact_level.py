#!/usr/bin/env python

'''
 This script will take a file that has gone through qiimeToMaaslin.py
 and will trim it to exactly a certain number tax levels

 Inputs:
 - Abundance table with levels delineated by a consistent marker
   -- SampleNumber	1	2	3	4
      Metadata		yes	no	yes	yes
      k_Bacteria|f_	1	1	1	1
 - Marker of taxa level division (default = "|")
 - Row number (starting at zero) that contains the last metadata row
 - Output filpath
 - Taxa level requested
 - Indicator of whether to keep full string or just leaf
   
'''

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i','--input-fp',help='qiimeToMaaslin.py output file', type=str, required=True)
	parser.add_argument('-o','--output-fp',help='Location for file to be written to', type=str, required=True)
	parser.add_argument('-s','--separator',help='Character/string that marks separation of taxa levels', type=str, default="|")
	parser.add_argument('-r','--row',help='Row index (starting at zero) that marks the last metadata row', type=int, required=True)
	parser.add_argument('-t','--taxa-level',help='Number of level that you would like to retain (starting from one)', type=int, required=True)
	parser.add_argument('-l','--leaves-only',help='Output only leaves', action='store_true', default=False)
	args = parser.parse_args()
	with open(args.input_fp, 'rU') as input_file, open(args.output_fp, 'wb') as output_file:
		input_reader = csv.reader(input_file, delimiter='\t')
		output_writer = csv.writer(output_file, delimiter='\t')
		for i in range(args.row):
			output_writer.writerow(input_reader.next())
		if args.leaves_only:
			for remaining_row in input_reader:
				this_tax = remaining_row[0].split(args.separator)
				if len(this_tax) == args.taxa_level:
					this_name = this_tax[args.taxa_level -1]
					output_writer.writerow([this_name] + remaining_row[1:])
		else:
			for remaining_row in input_reader:
				this_tax = remaining_row[0].split(args.separator)
				if len(this_tax) == args.taxa_level:
					output_writer.writerow(remaining_row)

if __name__ == '__main__':
	main()