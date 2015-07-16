#!/usr/bin/env python

import argparse, csv

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-i',help='tsv formatted otu table', required=True)
	parser.add_argument('-m',help='current mapping file path', required=True)
	parser.add_argument('-o',help='output filepath',required=True)
	parser.add_argument('-n',help='otu id to look for presence or absence',required=True)
	parser.add_argument('-c',help='category to compare to', default=False)
	parser.add_argument('-p',help='positive (>0) value in original mapping file')
	args = parser.parse_args()
	with open(args.m, 'rU') as mapping_file:
		r = csv.reader(mapping_file, delimiter='\t')
		map_header = r.next()
		mapper = {row[0]:dict(zip(map_header[1:], row[1:])) for row in r}
	with open(args.i, 'rU') as input_tsv:
		r = csv.reader(input_tsv, delimiter='\t')
		tsv_header = r.next()
		for row in r:
			if row[0] == args.n:
				row_of_cat = row
	tp = 0.0
	tn = 0.0
	fp = 0.0
	fn = 0.0
	
	for i in range(1,len(tsv_header)):
		this_val = row_of_cat[i]
		this_val = unicode(this_val)
		try:
			if args.c:
				prior_val = mapper[tsv_header[i]][args.c] == args.p
			else:
				prior_val = True
			if float(this_val) > 0:
				this_val = "positive"
				if prior_val:
					tp += 1
				else:
					fp += 1
			else:
				this_val = "negative"
				if prior_val:
					fn += 1
				else:
					tn += 1
			mapper[tsv_header[i]][args.n] = this_val
		except:
			continue
	with open(args.o, 'wb') as f:
		w = csv.writer(f,delimiter='\t')
		new_map_header = map_header + [args.n]
		w.writerow(new_map_header)
		for samp_name,samp_info in mapper.iteritems():
			if args.n not in samp_info:
				samp_info[args.n] = "unknown"
			this_row = [samp_name] + [samp_info[thing] for thing in new_map_header[1:]]
			w.writerow(this_row)
	if args.c:
		print 'true pos: %s' % tp
		print 'true neg: %s' % tn
		print 'false pos (type I error): %s' % fp
		print 'false neg (type II error): %s' % fn
		print 'precision: %.4f' % (tp/(tp+fp))
		print 'recall/sensitivity: %.4f' % (tp/(tp+fn))
		print 'specificity: %.4f' % (tn/(tn+fp))
		print 'accuracy: %.4f' % ((tp+tn)/(tp+tn+fp+fn))
		print 'F1 score: %.4f' % ((2*tp)/(2*tp+fp+fn))
	
if __name__ == '__main__':
	main()