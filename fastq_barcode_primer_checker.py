#!/usr/bin/env python

__version__ = "0.1.0"
__status__ = "Development"
__email__ = "http://geoffrosen.com/contact.html"
__maintainer__ = "Geoff Rosen"
__author__ = "Geoff Rosen"

__doc__ = ''' fastq_barcode_primer_checker.py: Check your barcodes and primers, replace them if necessary

 This script will take a fastq file and a mapping file
 It will then check if the barcode and primer are correct
 It will also check to see what the best barcode (of the set) is
 And can write that to an output mapping file
 
 For help, contact: %s (%s)

 Inputs:
 - Mapping file. Example (whitespaces are tabs in real file):
 #SampleID     BarcodeSequence     LinkerPrimerSequence
 Samp1           ACTGACT              ACTGNNNGGC
 Samp2           ACTGGCTT             ACTGNNNGGC 
 - fastq file
 
 Output:
 - New mapping file
''' % (__maintainer__, __email__)

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=__doc__)
	parser.add_argument('-i','--input-fastq',help='concatenated fastq file', type=str, required=True)
	parser.add_argument('-o','--output-fp',help='Location for information to be written to', type=str, required=True)
	parser.add_argument('-s','--separator',help='Character/string that marks separation of sample name from sequence name', type=str, default=".")
	parser.add_argument('-m','--mapping-fp',help='Mapping file path (#SampleID\tBarcodeSequence\tLinkerPrimerSequence)', type=str, required=True)
	parser.add_argument('-r','--replace-with-best',help='replace BarcodeSequence and LinkerPrimerSequence with the best',action='store_true',default=False)
	parser.add_argument('-t','--type-of-measure',help='the measure you would like to use to score best. options ["set", "barcode", "primer"]', default='barcode')
	args = parser.parse_args()
	sample_holder = {}
	barcode_primers = {}
	with open(args.mapping_fp, 'rU') as f:
		r = csv.reader(f, delimiter='\t')
		map_contents = [r.next()]
		for row in r:
			this_barc = row[1]
			this_primer = row[2]
			sample_holder[row[0]] = Sample(this_barc, this_primer)
			if this_barc not in barcode_primers:
				barcode_primers[this_barc] = set()
			barcode_primers[this_barc].add(this_primer)
			map_contents.append(row)
	for samp_name, sample in sample_holder.iteritems():
		sample.add_other_barcode_primers(barcode_primers)
	with open(args.input_fastq, 'rU') as f:
		for line in f:
			if line.startswith('@'):
				this_samp = line[1:].split(args.separator)[0]
			elif line.startswith('+'):
				this_samp = None
			elif this_samp:
				this_samp = sample_holder[this_samp]
				this_samp.test_seq(line)
	for samp_name, sample in sample_holder.iteritems():
		sample.get_best()
	with open(args.output_fp, 'wb') as f:
		w = csv.writer(f, delimiter='\t')
		if args.replace_with_best:
			h = map_contents[0][0:-1] + \
				['BestSetBarcodeProp',
				'BestSetPrimerProp',
				'TotalSeqs',
				'OriginalBC',
				'OriginalPrimer',
				'OriginalBC_score',
				'OriginalPrimer_score'] + \
				[map_contents[0][-1]]
			w.writerow(h)
			for row in map_contents[1:]:
				this_samp = sample_holder[row[0]]
				this_best = this_samp.bests[args.type_of_measure]
				this_orig = this_samp.barc_primers[0]
				this = [row[0]] + \
					[this_best.barcode, 
					this_best.primer] + \
					row[3:-1] + \
					[this_best.barcode_score,
					this_best.primer_score,
					this_samp.total_seqs,
					this_orig.barcode,
					this_orig.primer,
					this_orig.barcode_score,
					this_orig.primer_score] + \
					[row[-1]]
				w.writerow(this)
		else:
			h = map_contents[0][0:-1] + \
				['OriginalBC_score',
				'OriginalPrimer_score',
				'TotalSeqs'] + \
				[map_contents[-1]]
			w.writerow(h)
			for row in map_contents[1:]:
				this_samp = sample_holder[row[0]]
				this_orig = this_samp.barc_primers[0]
				this = row[0-1] + \
					[this_orig.barcode_score,
					this_orig.primer_score,
					this_samp.total_seqs] + \
					[row[-1]]
				w.writerow(this)

def check_seq_identity(primer, test_seq):
	for i in range(len(primer)):
		if check_letter_identity(primer[i], test_seq[i]) == False:
			return False
	return True

mapper = {'A': set(['A']),
			'T': set(['T']),
			'G': set(['G']),
			'C': set(['C']),
			'K': set(['G','T']),
			'M': set(['A','C']),
			'R': set(['A','G']),
			'Y': set(['C','T']),
			'S': set(['C','G']),
			'W': set(['A','T']),
			'B': set(['C','G','T']),
			'V': set(['A','C','G']),
			'H': set(['A','C','T']),
			'D': set(['A','G','T']),
			'X': set(['A','C','T','G']),
			'N': set(['A','C','T','G'])}

def check_letter_identity(ref, test):
	if test in mapper[ref]:
		return True
	return False
				
class Sample:
	def __init__(self, barcode, primer):
		self.barc_primers = [BarcodePrimer(barcode, primer)]
		self.total_seqs = 0.0
		self.bests = {}
	def add_other_barcode_primers(self, other_barc_primers_set):
		others = []
		self.barc_primers = self.barc_primers + [BarcodePrimer(barc, primer) for barc, primer_set in other_barc_primers_set.iteritems() for primer in primer_set]
	def test_seq(self, seq):
		for barc_primer in self.barc_primers:
			barc_primer.test_seq(seq)
		self.total_seqs += 1
	def score(self):
		for barc_primer in self.barc_primers:
			barc_primer.score(self.total_seqs)
	def get_best(self):
		self.score()
		self.get_best_set()
		self.get_best_barcode()
		self.get_best_primer()
	def get_best_set(self):
		best_set_score = 0.0
		self.bests['set'] = self.barc_primers[0]
		for barc_primer in self.barc_primers:
			if barc_primer.avg_score > best_set_score:
				best_set_score = barc_primer.avg_score
				self.bests['set'] = barc_primer
	def get_best_barcode(self):
		best_barc_score = 0.0
		self.bests['barcode'] = self.barc_primers[0]
		for barc_primer in self.barc_primers:
			if barc_primer.barcode_score > best_barc_score:
				best_barc_score = barc_primer.barcode_score
				self.bests['barcode'] = barc_primer
	def get_best_primer(self):
		best_primer_score = 0.0
		self.bests['primer'] = self.barc_primers[0]
		for barc_primer in self.barc_primers:
			if barc_primer.primer_score > best_primer_score:
				best_primer_score = barc_primer.primer_score
				self.bests['primer'] = barc_primer

class BarcodePrimer:
	def __init__(self, barcode, primer):
		self.barcode = barcode
		self.bc_len = len(barcode)
		self.primer = Primer(primer)
		self.primer_len = len(primer)
		self.barcode_correct = 0.0
		self.primer_correct = 0.0
	def test_seq(self, seq):
		obs_barcode = seq[self.bc_len]
		obs_primer = seq[self.bc_len:self.bc_len + self.primer_len]
		if obs_barcode == self.barcode:
			self.barcode_correct += 1
		if self.primer.seq_match(obs_primer):
			self.primer_correct += 1
	def score(self, total_seqs):
		if total_seqs == 0.0:
			total_seqs = 1.0
		self.barcode_score = self.barcode_correct/total_seqs
		self.primer_score = self.primer_correct/total_seqs
		self.avg_score = (self.barcode_score + self.primer_score)/2

class Primer:
	def __init__(self, primer):
		self.primer = primer
		self.denied = set()
		self.accepted = set()
	def seq_match(self, test_seq):
		if test_seq in self.denied:
			return False
		if test_seq in self.accepted:
			return True
		res = check_seq_identity(self.primer, test_seq)
		if res:
			self.accepted.add(test_seq)
			return True
		else:
			self.denied.add(test_seq)
			return False
			
if __name__ == '__main__':
	main()