#!/bin/bash

# Input .frq file
FRQ_FILE="freq_check.frq"

# Output: SNPs with >2 alleles
OUTPUT="multiallelic_snps.txt"

# Extract SNPs that appear more than once (i.e., multi-allelic)
awk 'NR>1 {count[$2]++} END {for (snp in count) if (count[snp] > 1) print snp}' "$FRQ_FILE" > "$OUTPUT"

echo "Multi-allelic SNPs written to $OUTPUT"
