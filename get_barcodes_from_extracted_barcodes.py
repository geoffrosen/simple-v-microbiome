#!/usr/bin/env python

__version__ = "0.1.0"
__status__ = "Development"
__email__ = "http://geoffrosen.com/contact.html"
__maintainer__ = "Geoff Rosen"
__author__ = "Geoff Rosen"

__doc__ = ''' get_barcodes_from_extracted_barcodes.py: Get barcodes from the ouput of extract_barcodes.py

 This script will take a barcodes.fastq file from extract_barcodes.py
 It will then determine the most likely barcode for each sequence
 It will output a new mapping file with the barcodes added
 
 For help, contact %s (%s)

 Inputs:
 - barcodes.fastq
 - mapping file
 
 Output:
 - mapping file with appended barcodes and stats
   
''' % (__maintainer__, __email__)

import argparse, csv, sys

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=__doc__)
	parser.add_argument('-i','--input-fp',help='barcodes.fastq file', type=str, required=True)
	parser.add_argument('-o','--output-fp',help='Location for new mapping file to be written to', type=str, required=True)
	parser.add_argument('-s','--separator',help='Character/string that marks separation of sample id and sequence', type=str, default=".")
	parser.add_argument('-m','--mapping-fp',help='File path to mapping file', required=True)
	parser.add_argument('-w','--warning-threshold',help='Level at wish you would like a warning about barcode matching', type=float, default=0.8)
	parser.add_argument('-c','--column-samp-id',help='Column header for sample id column', required=True)
	args = parser.parse_args()
	mapping_body = {}
	possible_barcs = {}
	with open(args.mapping_fp, 'rU') as f:
		r = csv.reader(f, delimiter='\t')
		mapping_header = r.next()
		csi_index = mapping_header.index(args.column_samp_id)
		new_mapping_header = ['#SampleID', 'BarcodeSequence'] + mapping_header[0:csi_index] + mapping_header[csi_index + 1:]
		for row in r:
			this_samp_id = row[csi_index]
			mapping_body[this_samp_id] = row[0:csi_index] + row[csi_index + 1:]
			possible_barcs[this_samp_id] = PossibleBarcs(this_samp_id)
	dummy_possible_barcs = DummyPossibleBarcs()
	this_possible_barcs = dummy_possible_barcs
	i = 0
	with open(args.input_fp, 'rU') as f:
		for line in f:
			stripped_line = line.rstrip()
			if i%4 == 0:
				this_samp = line[1:].split(args.separator)[0]
				try:
					this_possible_barcs = possible_barcs[this_samp]
				except:
					print line
					sys.exit(2)
			elif i%4 == 1:
				this_possible_barcs.append(stripped_line)
			i += 1
	with open(args.output_fp, 'wb') as f:
		w = csv.writer(f, delimiter='\t')
		w.writerow(new_mapping_header)
		for samp_id, mapping_content in mapping_body.iteritems():
			this_possible_barcs = possible_barcs[samp_id]
			this_possible_barcs.calc_props()
			this_row = [samp_id, this_possible_barcs.give_res(args.warning_threshold)] + mapping_content
			w.writerow(this_row)
	
	

class DummyPossibleBarcs:
	def append(self, some_string):
		pass
			
class PossibleBarcs:
	def __init__(self, samp_id):
		self.possible_barcs = {}
		self.total = 0.0
		self.samp_id = samp_id
	def append(self, possible_barc):
		if possible_barc not in self.possible_barcs:
			self.possible_barcs[possible_barc] = 0.0
		self.possible_barcs[possible_barc] += 1.0
		self.total += 1.0
	def calc_props(self):
		for pb in self.possible_barcs:
			self.possible_barcs[pb] = self.possible_barcs[pb]/self.total
	def give_res(self, warning_threshold):
		highest_prop = 0.0
		for pb, pbp in self.possible_barcs.iteritems():
			if pbp > highest_prop:
				highest = pb
				highest_prop = pbp
		if highest:
			if highest_prop < warning_threshold:
				print 'Barcode %s on %s does not meet threshold %s. Instead, it is seen %s' % (highest, self.samp_id, warning_threshold, highest_prop)
			return highest
		else:
			return 'NoneFound'
		


if __name__ == '__main__':
	main()