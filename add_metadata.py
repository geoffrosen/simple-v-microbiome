#!/usr/bin/env python

__doc__ = ''' add_metadata.py: This will add metadata to a tsv file

It will match the element in the top row of the tsv file
with one in the leftmost column of the mapping file.
It has options that will allow you to select whether to remove
samples that are not listed in the mapping file (-r), to select
which columns from the mapping file should make their way into
the output (-c), and what values of those columns should be
allowed (-a). It will list for you the excluded samples (-w).
It can read from the stdin or use a specified filepath (-i).
It can output to stdout or use a specified filepath (-o).

Please direct questions to %s

Sample:

Say you have an otu table (otu_table.tsv) that looks like this:

#OTU ID    Sample_1  Sample_2  Sample_3
Bact_1       5          6        8

And a mapping file (mapping_file.tsv) that looks like this:
#SampleID  Meta_1    Meta_2
Sample_1     1          2
Sample_2     2          1

If you run: 
python add_metadata.py -i otu_table.tsv -m mapping_file.tsv
	-o output.tsv

This will be the output:
#OTU ID    Sample_1  Sample_2  Sample_3
Meta_1       1          2        NA
Meta_2       2          1        NA
Bact_1       5          6        8

If you run:
python add_metadata.py -i otu_table.tsv -m mapping_file.tsv
	-o output.tsv -r

This will be the output:
#OTU ID    Sample_1  Sample_2
Meta_1       1          2
Meta_2       2          1
Bact_1       5          6

If you run: 
python add_metadata.py -i otu_table.tsv -m mapping_file.tsv
	-o output.tsv -c "Meta_1"

This will be the output:
#OTU ID    Sample_1  Sample_2  Sample_3
Meta_1       1          2        NA
Bact_1       5          6        8

If you run:
python add_metadata.py -i otu_table.tsv -m mapping_file.tsv
	-o output.tsv -c "Meta_1" -a "1"

This will be the output:
#OTU ID    Sample_1
Meta_1       1
Bact_1       5

If you run:
python add_metadata.py -i otu_table.tsv -m mapping_file.tsv
	-o output.tsv -c "Meta_1,Meta_2" -a "1,2;2"

This will be the output:
#OTU ID    Sample_1
Meta_1       1
Meta_2       2
Bact_1       5
''' % 'geoff.rosen@gmail.com'

__author__ = "Geoff Rosen"
__maintainer__ = "Geoff Rosen"
__email__ = "geoff.rosen@gmail.com"
__version__ = "0.1.0"

import argparse, csv, sys

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=__doc__)
	parser.add_argument('-i',help='tsv formatted otu table', default=None)
	parser.add_argument('-m',help='mapping filepath. left-most column should be the same as the line headers of the tsv file.',required=True)
	parser.add_argument('-o',help='output filepath', default=None)
	parser.add_argument('-r',help='remove samples without metadata',action='store_true')
	parser.add_argument('-c', help='categories to add (if not whole set, comma separated)', default=False)
	parser.add_argument('-a', help='allowed values in categories. (semi-colon separated between variables, comma separate between values)', default=False)
	parser.add_argument('-w', help='write error(s)/removed sample(s) to stderr', action='store_true', default=False)
	args = parser.parse_args()
	opened_files = []
	if args.c:
		args.c = args.c.split(',')
	if args.a:
		args.r = True
		args.a = args.a.split(';')
		while len(args.a) != len(args.c):
			args.a.append('')
		args.a = dict(zip(args.c, args.a))
		for cat, opts in args.a.iteritems():
			args.a[cat] = opts.split(',')
	if args.c:
		args.c = set(args.c)
	with open(args.m, 'rU') as mapping_file:
		r = csv.reader(mapping_file, delimiter='\t')
		header = r.next()[1:]
		mapper = {row[0]: {header[i]: row[i + 1] for i in range(len(header))} for row in r}
	if not sys.stdin.isatty():
		if args.i != None:
			sys.exit('It seems that you are passing in a file from stdin and using the -i argument. Please only use one.')
		input_file = sys.stdin
	else:
		input_file = open(args.i, 'rU')
		opened_files.append(input_file)
	if args.o == None:
		output_file = sys.stdout
	else:
		output_file = open(args.o, 'wb')
		opened_files.append(output_file)
	r = csv.reader(input_file, delimiter='\t')
	w = csv.writer(output_file, delimiter='\t')
	top = r.next()
	lineholder = []
	nheader = []
	for item in header:
		if args.c and item not in args.c:
			continue
		else:
			lineholder.append([item])
			nheader.append(item)
	headeritems = len(header)
	errs = set()
	errs_samples = set()
	for m in range(1,len(top)):
		for i in range(len(nheader)):
			if args.c and nheader[i] not in args.c:
				continue
			try:
				if args.a and args.a[nheader[i]] != [''] and mapper[top[m]][nheader[i]] not in args.a[nheader[i]]:
					lineholder[i].append('NA')
					errs.add(m)
					errs_samples.add(top[m])
				else:
					lineholder[i].append(mapper[top[m]][nheader[i]])
			except:
				lineholder[i].append('NA')
				errs.add(m)
				errs_samples.add(top[m])
	if args.r:
		w.writerow(get_rid_of_cols(top, errs))
		for item in lineholder:
			w.writerow(get_rid_of_cols(item, errs))
		for remrow in r:
			w.writerow(get_rid_of_cols(remrow, errs))
	else:
		w.writerow(top)
		for item in lineholder:
			w.writerow(item)
		for remrow in r:
			w.writerow(remrow)
	for f in opened_files:
		f.close()
	if args.w:
		sys.stderr.write('No removed samples\n')
		for samp in errs_samples:
			sys.stderr.write(samp + '\n')
		sys.exit("Finished with %s error(s)/removed sample(s)" % len(errs))
	else:
		sys.exit('Finished with %s error(s)/removed sample(s). If you would like to see them, use the "-w" flag.' % len(errs))
	
def get_rid_of_cols(row, bad_cols):
	keep = []
	for i in range(len(row)):
		if i not in bad_cols:
			keep.append(row[i])
	return keep
	
if __name__ == '__main__':
	main()