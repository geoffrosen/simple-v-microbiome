#!/usr/bin/env python

import argparse, csv, sys

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i',help='tsv formatted otu table', default=None)
	parser.add_argument('-m',help='mapping filepath. left-most column should be the same as the line headers of the tsv file.',required=True)
	parser.add_argument('-o',help='output filepath', default=None)
	parser.add_argument('-r',help='remove samples without metadata',action='store_true')
	parser.add_argument('-c', help='categories to add (if not whole set, comma separated)',default=False)
	args = parser.parse_args()
	opened_files = []
	if args.c:
		args.c = args.c.split(',')
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
		opened_files.apend(output_file)
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
	errs = []
	for m in range(1,len(top)):
		for i in range(len(nheader)):
			if args.c and nheader[i] not in args.c:
				continue
			try:
				lineholder[i].append(mapper[top[m]][nheader[i]])
			except:
				lineholder[i].append('NA')
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
	for f in opened_files:
		f.close()
	sys.exit("finished with %s errors" % len(errs))
	
def get_rid_of_cols(row, bad_cols):
	keep = []
	for i in range(len(row)):
		if i not in bad_cols:
			keep.append(row[i])
	return keep
	
if __name__ == '__main__':
	main()