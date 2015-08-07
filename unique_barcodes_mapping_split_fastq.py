#!/usr/bin/env python

'''
 This script will take a fastq file and a mapping file
 It will split the mapping file into unique mapping files
 It will split the fastq files to match the mapping files
 
 Inputs:
 - fastq file
 - mapping file
   
'''

import argparse, csv, os

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i','--input-fastq',help='fastq file', type=str, required=True)
	parser.add_argument('-o','--output-folder',help='Location for information to be written to', type=str, required=True)
	parser.add_argument('-s','--separator',help='Character/string that marks separation of sample name from sequence name', type=str, default=".")
	parser.add_argument('-m','--mapping-fp',help='Mapping file path (#SampleID\tBarcodeSequence\tLinkerPrimerSequence)', type=str, required=True)
	args = parser.parse_args()
	with open(args.mapping_fp, 'rU') as f:
		r = csv.reader(f, delimiter='\t')
		mapping_files = MappingFilesHolder(r.next())
		for line in r:
			mapping_files.add_line(line)
	base_mfn = args.output_folder + '/' + os.path.basename(os.path.splitext(args.mapping_fp)[0])
	samp_id_file_dict = mapping_files.export_to_tsvs_and_return_samp_id_file_dict(base_mfn)
	fastq_files = FastqSplitter(samp_id_file_dict)
	with open(args.input_fastq, 'rU') as f:
		i = 0
		for line in f:
			if i%4 == 0:
				this_samp = line[1:].split(args.separator)[0]
			i += 1
			fastq_files.add_line(line, this_samp)
	fastq_files.close_files()

class FastqSplitter:
	def __init__(self, samp_id_file_dict):
		self.fastqfilegetter = {}
		self.fastqfiles = []
		for map_fp, sample_ids in samp_id_file_dict.iteritems():
			this_fastq = FastqFileContents(map_fp)
			for samp_id in sample_ids:
				self.fastqfilegetter[samp_id] = this_fastq
			self.fastqfiles.append(this_fastq)
	def add_line(self, line, samp_id):
		self.fastqfilegetter[samp_id].write_line(line)
	def close_files(self):
		for ff in self.fastqfiles:
			ff.close()
		

class FastqFileContents:
	def __init__(self, map_fp):
		self.lines = []
		self.fp = map_fp[0:-4] + '.fastq'
		self.f = open(self.fp, 'wb')
	def write_line(self, line):
		self.f.write(line)
	def close(self):
		self.f.close()

class MappingFilesHolder:
	def __init__(self, header_line):
		self.mapping_files = []
		self.header = header_line
	def add_line(self, row, barcode_index = 1, sample_id_index = 0):
		for mapping_file in self.mapping_files:
			if mapping_file.add_line_to(row, barcode_index, sample_id_index):
				return None
		new_mapping_file = UniqueMappingFile(self.header)
		new_mapping_file.add_line_to(row, barcode_index, sample_id_index)
		self.mapping_files.append(new_mapping_file)
	def export_to_tsvs_and_return_samp_id_file_dict(self, base_mapping_file_name):
		i = 1
		matcher = {}
		for mf in self.mapping_files:
			this_fp = base_mapping_file_name + '_' + str(i) + '.tsv'
			with open(this_fp, 'wb') as f:
				w = csv.writer(f, delimiter='\t')
				for row in mf.export():
					w.writerow(row)
			i += 1
			matcher[this_fp] = mf.samp_ids
		return matcher
	
	
class UniqueMappingFile:
	def __init__(self, header):
		self.header = header
		self.barcs = set()
		self.rows = []
		self.samp_ids = []
	def add_line_to(self, row, barcode_index, sample_id_index):
		this_barc = row[barcode_index]
		if this_barc in self.barcs:
			return False
		self.rows.append(row)
		self.barcs.add(this_barc)
		self.samp_ids.append(row[sample_id_index]) 
		return True
	def export(self):
		return [self.header] + self.rows

				
			
if __name__ == '__main__':
	main()