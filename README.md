# simple-v-microbiome

These are scripts that help make it possible to run an analysis solely from a bash script

1. trim_to_exact_level.py
 - use this script with the output from something like [qiimeToMaaslin](https://bitbucket.org/biobakery/qiimetomaaslin)
 - this will trim the output to an exact level of your choosing
1. heatmap.R
 - use this from the command line to make heatmaps using one category of your choosing
 - uses the output from transpose.py as included with [Maaslin](https://bitbucket.org/biobakery/maaslin/)
1. add_metadata.py
 - use this to add metadata to your tsv otu table without modifying the features
 - requires a tsv formatted otu table (with the top line as sample ids)
1. fastq_barcode_primer_checker.py
 - use this to check if your barcodes and primers look like they match a fastq file
 - I use this when I am taking fastq files, barcodes, and primers from SRA, as I am not confident that all was entered correctly
 - it will output a new mapping file with the values of proportion exact match for both the barcode and the primer
 - it will print a warning if a certain sample matches its barcode under a specified proportion [default: 0.5]
1. fix_after_qiimeToMaaslin.py
 - when qiimeToMaalin.py cannot detect the format of a file, it adds a big header
 - this will sense that and remove it if necessary
1. get_barcodes_from_extracted_barcodes.py
 - use this to help build a mapping file when you are just given fastq files
 - it takes a barcodes.fastq file from extract barcodes.py
 - ```extract_barcodes.py -f compiled.fastq -c barcode_single_end --bc1_len 12 -o extracted_barcodes```
 - it will also print a warning if the best barcode match was below an arbitrary cutoff
1. guess_status_from_otu_table.py
 - use this to add a column to a mapping file indicating presence or absence of a feature
 - it takes in a mapping file, a tsv otu table, and a feature name in all cases
 - optionally, it can take in a category (from the original mapping file) and that category's positive value and will print some standard metrics
1. make_stirrups_otu_table.py
 - use this to make an otu table and a rep set from the assignments file that is the output of running [stirrups](http://sourceforge.net/projects/stirrups/files) [reference](http://www.biomedcentral.com/1471-2164/13/S8/S17)
 - the reference set is helpful for building a tree so that phylogeny based metrics can be calculated


- Some things to note:
 - I will try to get some examples up soon
 - I have only tested these with my data - they have worked so far, but if there is an issue, post it
 - You can contact me [here](http://geoffrosen.com/contact.html)
