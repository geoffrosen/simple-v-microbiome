#!/usr/bin/env python

'''
 This script will take a fasta file (downloaded from HMP)
 that contains many body sites. It will split the fasta into
 separate fastas for each body site. It will only retain fastas
 of body sites indicated
 
 Inputs:
 - input fasta fp (ex: gunzip http://downloads.hmpdacc.org/data/HMQCP/seqs_v13.fna.gz)
 - input map fp (ex: http://www.hmpdacc.org/doc/ppAll_V13_map.txt)
 - body sites to retain
 
 Why will this not work as a general script:
 - The sequence names are not exactly matched between mapping and fasta
   - Customization had to be done for hmp
   
'''

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i','--input-fp',help='input concatenated fasta from HMP (ex: gunzip http://downloads.hmpdacc.org/data/HMQCP/seqs_v13.fna.gz)', type=str, required=True)
	parser.add_argument('-o','--output-folder',help='Output folder. names will be generated dynamically.', type=str, required=True)
	parser.add_argument('-m','--map-fp',help='Mapping file path (ex for map: http://www.hmpdacc.org/doc/ppAll_V13_map.txt)', type=str, required=True)
	parser.add_argument('-c','--categories',help='Categories to retain (comma separated)', type=str, required=True)
	parser.add_argument('-t','--header',help='Column name to split and retain categories', type=str, required=True)
	parser.add_argument('-s','--splitter',help='Splitter between sample name and seq number', required=True, default=';')
	args = parser.parse_args()
	cat_vals = set(args.categories.split(','))
	samp_ids = {}
	srs_sample_ids = {}
	with open(args.map_fp, 'rU') as f:
		r = csv.reader(f, delimiter='\t')
		map_header = r.next()
		SampleID = map_header.index('SampleID')
		SRS_SampleID = map_header.index('SRS_SampleID')
		header_col = map_header.index(args.header)
		for row in r:
			this_header_col = row[header_col]
			if this_header_col in cat_vals:
				this_samp_id = row[SampleID].split('.')
				this_samp_id = '.'.join(this_samp_id[0:len(this_samp_id) - 1])
				samp_ids[this_samp_id] = this_header_col
				srs_sample_ids[row[SRS_SampleID]] = this_header_col
	files_holder = {}
	with open(args.input_fp, 'rU') as input_fasta:
		dummy_file = DummyFile()
		for cat_val in cat_vals:
			fp = args.output_folder + '/' + cat_val + '.fasta'
			files_holder[cat_val] = open(fp, 'wb')
		current_file = dummy_file
		for line in input_fasta:
			if line.startswith('>'):
				current_file = dummy_file
				this_samp_id = line.split(args.splitter)[0][1:]
				this_srs_samp_id = this_samp_id.split('.')[0]
				if this_samp_id in samp_ids:
					current_file = files_holder[samp_ids[this_samp_id]]
				elif this_srs_samp_id in srs_sample_ids:
					current_file = files_holder[srs_sample_ids[this_srs_samp_id]]
				else:
					current_file = dummy_file
			current_file.write(line)
	for fp, file_obj in files_holder.iteritems():
		file_obj.close()

					
class DummyFile:
	def write(self, text_for_disposal):
		pass
		

if __name__ == '__main__':
	main()