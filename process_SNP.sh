#!/bin/sh

# Define Paths (Change Accordingly)
DATA_DIR="</path/to/your/data/dir>"
BASE_NAME="</name/of/your/snp/folder>"
PLINK_DIR="</path/to/folder/where/plink-1.9/is/saved>"
FILE1="</path/to/the/first/file>"
FILE2="</path/to/the/second/file>"
MERGED="</path/to/the/merged/file>/<filename>_merged"

# set the thresholds :
SNP_CALL_RATE=0.0001
MAF_THRESHOLD=0.1
MIND_THRESHOLD=0.05
HWE_THRESHOLD=0.001
HWE2_THRESHOLD=0.001
P_VALE=0.001 #(=1e-3)
LD_WINDOW_SIZE=50


# Change the current directory into the plink directory :
cd $PLINK_DIR

# 1) Merging two files of FILE1 and FILE2 : 
./plink --bfile $DATA_DIR/$FILE1 --bmerge $DATA_DIR/$FILE2 --make-bed --out $DATA_DIR/$MERGED

# 2) Step-1: filtering SNPs with call rate "SNP_CALL_RATE" :
./plink --bfile $DATA_DIR/$MERGED --geno $SNP_CALL_RATE --missing --make-bed --out $DATA_DIR/step_1_geno_${SNP_CALL_RATE}

# 3) Step-2: filtering minor allele frequency(maf) with threshold "MAF_THRESHOLD" :
./plink --bfile $DATA_DIR/step_1_geno_${SNP_CALL_RATE} --maf $MAF_THRESHOLD --missing --make-bed --out $DATA_DIR/step_2_maf_${MAF_THRESHOLD}

# 4) Step-3: filtering out samples with missing SNPs "$MIND_THRESHOLD" :
./plink --bfile $DATA_DIR/step_2_maf_${MAF_THRESHOLD} --mind $MIND_THRESHOLD --missing --make-bed --out $DATA_DIR/step_3_mind_${MIND_THRESHOLD}

# 6) Step-4: filtering the data with HWE "HWE_THRESHOLD" :
./plink --bfile $DATA_DIR/step_3_mind_${MIND_THRESHOLD} --hwe $HWE_THRESHOLD --missing --make-bed --out $DATA_DIR/step_4_hwe_${HWE_THRESHOLD}

# 7) Step-5: excluding all SNPs with p-value below "P_VALE" :
./plink --bfile $DATA_DIR/step_4_hwe_${HWE_THRESHOLD} --pfilter $P_VALUE --missing --make-bed --out $DATA_DIR/step_5_p_filter_${P_VALUE}

# 9) Step-6: taking SNPs corresponding to the chromosome 1-23:
./plink --bfile $DATA_DIR/step_5_p_filter_${P_VALUE} --chr 1-22, xy --missing --make-bed --out $DATA_DIR/step_6_chr-1-23

# 10) Step-7: recoding the data with 0,1,2 as the count of minor alleles:
./plink --bfile $DATA_DIR/step_6_chr-1-23 --recodeA --missing --make-bed --out $DATA_DIR/step_7_recoded

# 11) Step-8: Change the name of the '.raw' file into '.csv':
mv $DATA_DIR/step_7_recoded.raw $DATA_DIR/step_7_recoded.csv
# This csv file is the final SNP data file, where the columns are separated by space(" "), but it may contain NaNs or Null values. 
# Use pandas as "df.dropna(how='any', axis=1)" to remove them 
