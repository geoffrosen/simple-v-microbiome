#!/usr/bin/env python

import argparse, os, csv, sys

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-a',help='stirrups assignment file', required=True)
	parser.add_argument('-r',help='stirrups reference fasta file', required=True)
	parser.add_argument('-t',help='stirrups reference taxon heirarchy', required=True)
	parser.add_argument('-o',help='output otu table location', required=True)
	parser.add_argument('-s', help='output rep set location', required=True)
	parser.add_argument('-m',help='minimum identity score required', default = 0.0, type=float)
	args = parser.parse_args()
	tax_map = build_tax_map(args.t)
	string_example = [('domain','k'),
						('phylum','p'),
						('class', 'c'),
						('order', 'o'),
						('family', 'f'),
						('genus', 'g'),
						('species', 's')]
	species_holder = SpeciesHolder(tax_map, string_example)
	make_otu_species_map(args.r, species_holder)
	samps_header = add_counts(args.a, species_holder, args.m)
	samps_header = list(samps_header.keys())
	write_output(args.o, species_holder, samps_header, args.m, args.s)

	
def write_output(output_fp, species_holder, samps_header, min_id_score, rep_set_fp):
	with open(output_fp, 'wb') as f, open(rep_set_fp, 'wb') as rep_set_file:
		w = csv.writer(f, delimiter='\t')
		w.writerow(['#Created from stirrups with minimum identity score: %s' % (min_id_score)])
		w.writerow(['#OTU ID'] + samps_header + ['taxonomy'])
		for species_name, species_object in species_holder.iteritems():
			this_row = [species_object.short_name]
			for samp_name in samps_header:
				this_row.append(species_object[samp_name])
			this_row.append(species_object.long_name)
			w.writerow(this_row)
			rep_set_file.write('>' + species_object.short_name + '\n')
			species_object.seqs.sort(key=len, reverse=True)
			rep_set_file.write(species_object.seqs[0] + '\n')

def add_counts(stirrups_assignment_fp, species_holder, min_id_score):
	samps_seen = {}
	species_number = 0
	with open(stirrups_assignment_fp, 'rU') as f:
		r = csv.reader(f, delimiter='|')
		for row in r:
			sample_name = row[0]
			short_name = row[2]
			identity_score = row[4]
			if float(identity_score) > min_id_score:
				try:
					species_holder.add_count(short_name, sample_name)
				except:
					space_loc = short_name.index(' ')
					genus = short_name[0:space_loc]
					species = short_name[space_loc + 1:]
					species_holder.append(genus, species, 'added_species_%s' % species_number)
					species_number += 1
			if sample_name not in samps_seen:
				samps_seen[sample_name] = True
	return samps_seen

def build_tax_map(taxon_heirarchy_fp):
	tax_map = {}
	with open(taxon_heirarchy_fp, 'rU') as f:
		r = csv.reader(f, delimiter='\t')
		for row in r:
			this_map = {}
			for i in range(len(row)):
				if i%2 == 0:
					this_map[row[i+1]] = row[i]
			tax_map[this_map['genus']] = this_map
	return tax_map

def build_tax_string(genus, species, tax_map, string_example):
	this_one = []
	try:
		this_tax = tax_map[genus].copy()
		this_tax['species'] = species		
		for big_name, abbrev in string_example:
			this_one.append('%s__%s' % (abbrev, this_tax[big_name]))
	except:
		this_one = [genus, species]
	return '; '.join(this_one)

def make_otu_species_map(stirrups_ref_fp, species_holder):
	with open(stirrups_ref_fp, 'rU') as f:
		for line in f:
			if line.startswith('>'):
				split_line = line.split('|')
				seq_number = split_line[1]
				genus_loc = split_line.index('genus')
				species_loc = split_line.index('species')
				seq_genus = split_line[genus_loc + 1].replace('"', '')
				seq_species = split_line[species_loc + 1]
			else:
				species_holder.append(seq_genus, seq_species, line.rstrip())

class SpeciesHolder:
	def __init__(self, tax_map, string_example):
		self.species = {}
		self.tax_map = tax_map
		self.string_example = string_example
	def append(self, genus, species, seq):
		this_name = genus + ' ' + species
		if this_name not in self.species:
			self.species[this_name] = Species(genus, species, self.tax_map, self.string_example)
		self.species[this_name].add_seq(seq)
	def add_count(self, short_name, sample_name):
		self.species[short_name].add_count(sample_name)
	def __getitem__(self, short_name):
		return self.species[short_name]
	def __iter__(self):
		return iter([spec for spec in self.species])
	def iteritems(self, count_zero = False):
		if count_zero == True:
			return self.species.iteritems()
		else:
			this = {}
			for spec, spec_obj in self.species.iteritems():
				if not spec_obj.count_zero:
					this[spec] = spec_obj
			return iter([[spec, spec_obj] for spec, spec_obj in this.iteritems()])
	
class Species:
	def __init__(self, genus, species, tax_map, string_example):
		self.short_name = genus + '_' + species
		self.short_name = self.short_name.replace(' ','_')
		self.long_name = build_tax_string(genus, species, tax_map, string_example)
		self.seqs = []
		self.counts = {}
		self.count_zero = True
	def add_seq(self, seq):
		self.seqs.append(seq)
	def add_count(self, sample_name):
		if sample_name not in self.counts:
			self.counts[sample_name] = 0
		self.counts[sample_name] += 1
		self.count_zero = False
	def __getitem__(self, sample_name):
		try:
			return self.counts[sample_name]
		except:
			return 0
				
if __name__ == '__main__':
	main()