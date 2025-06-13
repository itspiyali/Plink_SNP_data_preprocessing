#!/bin/sh

# Define Paths (Change Accordingly)
# If any variable is not needed comment them out
DATA_DIR="</path/to/your/data/dir>"
BASE_NAME="</name/of/your/snp/folder>"
PLINK="</path/to/folder/where/plink-1.9/is/saved>"
FILE1="</path/to/the/first/file>"
FILE2="</path/to/the/second/file>"
MERGED="</path/to/the/merged/file>/<filename>_merged"
MERGING_LIST="</path/to/the/merging/list>" 


# set the thresholds :
SNP_CALL_RATE=0.0001
MAF_THRESHOLD=0.1
MIND_THRESHOLD=0.05
HWE_THRESHOLD=0.001
HWE2_THRESHOLD=0.001
P_VALE=0.001 #(=1e-3)
LD_WINDOW_SIZE=50


# Change the current directory into the plink directory :
cd $PLINK
"
In all the subsequent commands will use the flag '--bfile' if the SNP files are int .bed+.bim+.fam format. 
For the .ped+.map format, use --file
"
# 1) Merging two files of FILE1 and FILE2 : 
# -----------------------------------------
$PLINK/plink --bfile $DATA_DIR/$FILE1 --bmerge $DATA_DIR/$FILE2 --make-bed --out $DATA_DIR/$MERGED
"
use '--merge' for .ped+.map format
"

# Suppose file1 needs to be merged with file2, file3, file4, then create a .txt file called merge_list.txt. 
# Then merge them using the command: 
$PLINK/plink --bfile file1 --merge-list merge_list.txt --make-bed --out $MERGED
' 
where the merge_list.txt is in the format : 
</path/to/file2.txt>
</path/to/file3.txt>
</path/to/file4.txt>
'

# 2) Taking SNPs corresponding to the chromosome 1-23:
# ----------------------------------------------------
$PLINK/plink --bfile $DATA_DIR/$MERGED --chr 1-22, xy --make-bed --out $DATA_DIR/step_1_chr-1-23
'
In case only chromosome 1-22 are to be considered, use --chr 1-22, 
if only chromosome 1, 14, 19, 21 are to be considered, use --chr 1,14,19,21
'

# The following steps are preprocessing steps:

# 3) Step-1: filtering SNPs out with call rate > "SNP_CALL_RATE" :
# ----------------------------------------------------------------
$PLINK/plink --bfile $DATA_DIR/step_1_chr-1-23 --geno $SNP_CALL_RATE --missing --make-bed --out $DATA_DIR/step_2_geno_${SNP_CALL_RATE}

# 4) Step-2: filtering SNPs with minor allele frequency(maf) < "MAF_THRESHOLD" :
# ------------------------------------------------------------------------------
$PLINK/plink --bfile $DATA_DIR/step_2_geno_${SNP_CALL_RATE} --maf $MAF_THRESHOLD --missing --make-bed --out $DATA_DIR/step_3_maf_${MAF_THRESHOLD}

# 5) Step-3: filtering out samples with missing SNPs > "$MIND_THRESHOLD" :
# ------------------------------------------------------------------------
$PLINK/plink --bfile $DATA_DIR/step_3_maf_${MAF_THRESHOLD} --mind $MIND_THRESHOLD --missing --make-bed --out $DATA_DIR/step_4_mind_${MIND_THRESHOLD}

# 6) Step-4: filtering the data with > "HWE_THRESHOLD" :
$PLINK/plink --bfile $DATA_DIR/step_4_mind_${MIND_THRESHOLD} --hwe $HWE_THRESHOLD --missing --make-bed --out $DATA_DIR/step_5_hwe_${HWE_THRESHOLD}
"
The Hardy-Weinberg Equilibrium (HWE) principle states that, In the absence of selection, mutation, genetic drift, or other forces,
allele and genotype frequencies in a population will remain constant from generation to generation in the absence of other evolutionary influences.
Formula:
p^2 + 2pq + q^2 = 1
p^2	= 	dominant homozygous frequency (AA)
2pq	= 	heterozygous frequency (Aa)
q^2	= 	recessive homozygous frequency (aa)

By default the flag '--hwe' uses Fisher's exact test, to request a chi-squared test, use the option '--hwe2'
"
# To perform chi-squared test for HWE:
# ------------------------------------
$PLINK/plink --bfile $DATA_DIR/step_4_mind_${MIND_THRESHOLD} --hwe2 $HWE_THRESHOLD --missing --make-bed --out $DATA_DIR/step_5_hwe_${HWE_THRESHOLD}

# 7) Step-5: excluding all SNPs with p-value < "P_VALE" :
# -----------------------------------------------------------
$PLINK/plink --bfile $DATA_DIR/step_5_hwe_${HWE_THRESHOLD} --pfilter $P_VALUE --missing --make-bed --out $DATA_DIR/step_6_p_filter_${P_VALUE}


# 8) Step-6: recoding the data with 0,1,2 as the count of minor alleles:
# ----------------------------------------------------------------------
$PLINK/plink --bfile $DATA_DIR/step_6_p_filter_${P_VALUE} --recodeA --missing --make-bed --out $DATA_DIR/step_7_recoded

# 9) Step-7: Change the name of the '.raw' file into '.csv':
# ----------------------------------------------------------
mv $DATA_DIR/step_7_recoded.raw $DATA_DIR/step_7_recoded.csv
# This csv file is the final SNP data file, where the columns are separated by space(" "), but it may contain NaNs or Null values. 
# Use pandas as "df.dropna(how='any', axis=1)" to remove them 

"
Apart from the above standard preprocessing steps, there are another steps, to reduce the dimensionality of SNP data.
If the following steps are performed, then step-6 and step-7 are to be performed in the end, when all preprocessing 
steps are done.
"
# Linkage disequilibrium based SNP pruning (in case of reducing large number of SNPs):
# ------------------------------------------------------------------------------------
"
Linkage disequilibrium (LD) in the context of SNPs refers to the non-random association of alleles at different SNP 
sites within a population. It means that the alleles at two different SNPs tend to be inherited together more often 
than would be expected if they were independent.
"
$PLINK/plink --bfile $DATA_DIR/step_6_p_filter_${P_VALUE} --indep 50 5 2 
# or,
$PLINK/plink --bfile $DATA_DIR/step_6_p_filter_${P_VALUE} --indep 50 5 0.5 
"	
This command will create files : 
plink.prune.in
plink.prune.out
									 
Then apply the pruning with the command :
"
$PLINK/plink --bfile $DATA_DIR/step_6_p_filter_${P_VALUE} --extract $DATA_DIR/plink.prune.in --make-bed --out $DATA_DIR/LD_based_pruned
#	or,
$PLINK/plink --bfile $DATA_DIR/step_6_p_filter_${P_VALUE} --exclude $DATA_DIR/plink.prune.out --make-bed --out $DATA_DIR/LD_based_pruned

# To remove SNPs with Mendelian errors(not used for my data because the parent info is missing):
# ----------------------------------------------------------------------------------------------
"	
 Mendelian inheritance dictates that offspring inherit one allele of a gene from each parent. A Mendelian error occurs
when a child's genotype doesn't match the possible combinations of parental genotypes
"
$PLINK/plink --bfile $DATA_DIR/LD_based_pruned --mendel
"
This command will create files : 
plink.mendel
plink.imendel
plink.fmendel
plink.lmendel

The *.mendel file contains all Mendel errors (i.e. one line per error); the *.imendel file contains a
summary of per-individual error rates; the *.fmendel file contains a summary of per-family error rates; the
*.lmendel file contains a summary of per-SNP error rates.

This command works only if the PHENOTYPE(S) of the data is/are are present.
"


" 
NOTE:
-----
To check the number of SNPs in the data :       cat $DATA_DIR/step_1*.fam|wc -l
To check the number of samples in the data :    cat $DATA_DIR/step_1*.bim|wc -l

"
