#!/usr/bin/env python

'''
 This script will take a file that will be going to qiimeToMaaslin
 and will fix it to prevent errors from qiimeToMaaslin

 Inputs:
 - Abundance table filepath
 - Output filepath
   
'''

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i','--input-fp',help='File that will be going to qiimeToMaaslin.py', type=str, required=True)
	parser.add_argument('-o','--output-fp',help='Location for file to be written to', type=str, required=True)
	args = parser.parse_args()
	with open(args.input_fp, 'rU') as input_file, open(args.output_fp, 'wb') as output_file:
		input_reader = csv.reader(input_file, delimiter='\t')
		output_writer = csv.writer(output_file, delimiter='\t')
		output_writer.writerow(input_reader.next())
		base_addition = "Script Added "
		current_zero = 0
		last_addition = "None"
		for row in input_reader:
			if row[0].strip() == "":
				row[0] = base_addition + str(current_zero)
				current_zero += 1
			if row[-1].strip() == "":
				row[-1] = last_addition
			if row[-1].strip().startswith(";"):
				row[-1] = row[-1][row[-1].find(";") + 1:]
			if row[-1].strip().endswith(";"):
				row[-1] = row[-1][:row[-1].rfind(";")]
			row[-1] = row[-1].replace(";","|")
			output_writer.writerow(row)

if __name__ == '__main__':
	main()