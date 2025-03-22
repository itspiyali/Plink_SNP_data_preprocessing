#!/bin/bash

# Define Paths (Change Accordingly)
DATA_DIR="/home/piyali/Research/Data/SNP/PLINKFinal_ADNI_20231107"
BASE_NAME="ADNI3_PLINK_FINAL_2nd"
PLINK_DIR="/home/piyali/Downloads/plink_1.9_linux_x86_64_20241022"

# to show frequency stats:
$PLINK_DIR/plink --bfile $DATA_DIR/$BASE_NAME --assoc --adjust --check-sex --missing --chr 1-22,xy --freq --out $DATA_DIR/assoc_freq_stat

# to check external factors:
$PLINK_DIR/plink --bfile $DATA_DIR/$BASE_NAME --gxe --out external_factors

# to check parent-of-origin effects:
$PLINK_DIR/plink --bfile $DATA_DIR/$BASE_NAME --poo --out parent_of_origin

# Tests for association by analyzing whether an allele is transmitted more often than expected from heterozygous parents to affected offspring:
$PLINK_DIR/plink --bfile $DATA_DIR/$BASE_NAME --tdt --out tdt


# Step 1: Remove SNPs with missing genotype rate > 0.001
$PLINK_DIR/plink --bfile $DATA_DIR/$BASE_NAME --geno 0.001 --make-bed --out $DATA_DIR/step1_qc

# Step 2: Remove SNPs with minor allele frequency < 0.1
$PLINK_DIR/plink --bfile $DATA_DIR/step1_qc --maf 0.1 --make-bed --out $DATA_DIR/step2_qc

# Step 3: Retain only SNPs listed in brain_network_snps.txt
#$PLINK_DIR/plink --bfile $DATA_DIR/step2_qc --extract brain_network_snps.txt --make-bed --out $DATA_DIR/step3_qc

# Step 4: Remove SNPs failing Hardy-Weinberg Equilibrium (HWE) test (p < 0.001)
$PLINK_DIR/plink --bfile $DATA_DIR/step2_qc --hwe 0.001 --make-bed --out $DATA_DIR/step3_qc

# Step 5: Verify SNP count and generate final dataset
#$PLINK_DIR/plink --bfile $DATA_DIR/step3_qc --freq --out $DATA_DIR/step4_qc

# Step 6: Convert SNPs to additive genetic format (0,1,2 encoding)
$PLINK_DIR/plink --bfile $DATA_DIR/step3_qc --recodeA --make-bed --out $DATA_DIR/final_snp_data

# convert into csv:
mv $DATA_DIR/final_snp_data.raw $DATA_DIR/final_snp_data.csv

# Step 7: Remove intermediate files safely
#rm $DATA_DIR/step*_qc.*



echo "SNP QC Pipeline Completed Successfully!"

