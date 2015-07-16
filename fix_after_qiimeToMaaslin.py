#!/usr/bin/env python

'''
 This script will take a file that has gone through qiimeToMaaslin.py
 and will remove the heading that is added (usually added when qiimeToMaaslin doesn't know type)
 
 Inputs:
 - Abundance table filepath
 - Output filepath
   
'''

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i','--input-fp',help='qiimeToMaaslin.py output file', type=str, required=True)
	parser.add_argument('-o','--output-fp',help='Location for file to be written to', type=str, required=True)
	args = parser.parse_args()
	with open(args.input_fp, 'rU') as input_file, open(args.output_fp, 'wb') as output_file:
		input_reader = csv.reader(input_file, delimiter='\t')
		output_writer = csv.writer(output_file, delimiter='\t')
		start = False
		while not start:
			row = input_reader.next()
			if row[0].find("sample") != -1:
				start = True
				output_writer.writerow(row)
		for row in input_reader:
			output_writer.writerow(row)

if __name__ == '__main__':
	main()