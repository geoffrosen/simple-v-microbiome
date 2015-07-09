#!/usr/bin/env python

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i',help='tsv formatted otu table', required=True)
	parser.add_argument('-m',help='mapping filepath. left-most column should be the same as the line headers of the tsv file.',required=True)
	parser.add_argument('-o',help='output filepath',required=True)
	parser.add_argument('-r',help='remove samples without metadata',action='store_true')
	args = parser.parse_args()
	with open(args.m, 'rU') as mapping_file:
		r = csv.reader(mapping_file, delimiter='\t')
		header = r.next()[1:]
		mapper = {row[0]:row[1:] for row in r}
	with open(args.i, 'rU') as input_file, open(args.o, 'wb') as output_file:
		r = csv.reader(input_file, delimiter='\t')
		w = csv.writer(output_file, delimiter='\t')
		top = r.next()
		lineholder = []
		for item in header:
			lineholder.append([item])
		headeritems = len(header)
		errs = []
		for m in range(1,len(top)):
			for i in range(headeritems):
				try:
					lineholder[i].append(mapper[top[m]][i])
				except:
					lineholder[i].append('unknown')
					errs.append(m)
		if args.r:
			errs = dict(zip(errs,errs))
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
	print "finished with %s errors" % len(errs)
	
def get_rid_of_cols(row, bad_cols):
	keep = []
	for i in range(len(row)):
		if i not in bad_cols:
			keep.append(row[i])
	return keep
	
if __name__ == '__main__':
	main()