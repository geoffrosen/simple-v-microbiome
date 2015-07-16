#!/usr/bin/env python

'''
 This script will take a fastq file and a mapping file
 It will then check if the barcode and primer are correct

 Inputs:
 - Mapping file #SampleID\t#BarcodeSequence#LinkerPrimerSequence
 - fastq file
   
'''

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i','--input-fastq',help='concatenated fastq file', type=str, required=True)
	parser.add_argument('-o','--output-fp',help='Location for information to be written to', type=str, required=True)
	parser.add_argument('-s','--separator',help='Character/string that marks separation of sample name from sequence name', type=str, default=".")
	parser.add_argument('-m','--mapping-fp',help='Mapping file path (#SampleID\tBarcodeSequence\tLinkerPrimerSequence)', type=str, required=True)
	parser.add_argument('-w','--warning-threshold',help='Print warning about a sequence when proportion correct barcode or primer less than this amount', type=float, default=0.5)
	args = parser.parse_args()
	rats = {}
	map_info = {}
	with open(args.mapping_fp, 'rU') as f:
		r = csv.reader(f, delimiter='\t')
		map_contents = [r.next()]
		for row in r:
			rats[row[0]] = {'barcode_correct': 0.0, 'primer_correct': 0.0, 'total_seqs': 0.0}
			map_info[row[0]] = {'barcode': row[1], 'primer': row[2]}
			map_contents.append(row)
	with open(args.input_fastq, 'rU') as f:
		for line in f:
			if line.startswith('@'):
				this_samp = line[1:].split(args.separator)[0]
			elif line.startswith('+'):
				this_samp = None
			elif this_samp:
				this_map = map_info[this_samp]
				barc_as_seen = line[0:len(this_map['barcode'])]
				primer_as_seen = line[len(this_map['barcode']):len(this_map['barcode']) + len(this_map['primer'])]
				if barc_as_seen == this_map['barcode']:
					rats[this_samp]['barcode_correct'] += 1
				if primer_as_seen == this_map['primer']:
					rats[this_samp]['primer_correct'] += 1
				rats[this_samp]['total_seqs'] += 1
	for samp, samp_info in rats.iteritems():
		if samp_info['total_seqs'] != 0:
			samp_info['barcode_correct'] = samp_info['barcode_correct']/samp_info['total_seqs']
			if samp_info['barcode_correct'] < args.warning_threshold:
				print 'Barcode issue for sequence "%s" with correct proportion only: %s (which is less than %s)' % (samp, samp_info['barcode_correct'], args.warning_threshold)
			samp_info['primer_correct'] = samp_info['primer_correct']/samp_info['total_seqs']
			if samp_info['primer_correct'] < args.warning_threshold:
				print 'Primer issue for sequence "%s" with correct proportion only: %s (which is less than %s)' % (samp, samp_info['primer_correct'], args.warning_threshold)
	with open(args.output_fp, 'wb') as f:
		w = csv.writer(f, delimiter='\t')
		w.writerow(map_contents[0] + ['CorrectBarcodeProp','CorrectPrimerProp','TotalSeqs'])
		for row in map_contents[1:]:
			addnl_info = rats[row[0]]
			addnl_info = [addnl_info['barcode_correct'], addnl_info['primer_correct'], addnl_info['total_seqs']]
			w.writerow(row + addnl_info)

				
			
if __name__ == '__main__':
	main()