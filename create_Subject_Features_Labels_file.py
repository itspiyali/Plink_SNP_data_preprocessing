import pandas as pd

# Change accordingly :
snp_file = "/home/piyali/Piyali/Data/SNP/step_7_recoded_MERGED_1_GO.csv"
mri_file = "/home/piyali/Piyali/Data/Imaging/Info/MRI_T1.csv" # this file contains the labels
output_file = "/home/piyali/Piyali/Data/SNP/Subject_feature_label_SNP_final.csv"

# Step 1: Load SNP data
snp_df = pd.read_csv(snp_file, sep=" ") # change the separator if needed
snp_df = snp_df.drop(columns=['FID', 'PAT', 'MAT', 'SEX', 'PHENOTYPE']) # remove the unnecessary columns

# Step 2: Load MRI info
mri_df = pd.read_csv(mri_file, sep=",") # change the separator if needed

# In mri_df all subjcts are in the form '002+AF8-S+AF8-0295', so we need to replace "+AF8-" into "_"
mri_df['Subject ID'] = mri_df['Subject ID'].astype(str).str.replace(r"\+AF8-", "_", regex=True) 
# [Omit this line if the subject IDs in your 'Subject ID' columns are not in this format]

# Step 3: Drop duplicates based on Subject ID + Research Group
mri_df = mri_df.drop_duplicates(subset=['Subject ID', 'Research Group'])

# Step 4: Map label names to integers
label_map = {'CN': 0, 'SMC': 1, 'EMCI': 2, 'MCI': 3, 'LMCI': 4, 'AD': 5}
mri_df['Labels'] = mri_df['Research Group'].map(label_map)

# Step 5: Merge on IID / Subject ID
merged_df = pd.merge(mri_df[['Subject ID', 'Labels']], snp_df, how='inner', left_on='Subject ID', right_on='IID')

# Step 6: Drop redundant IID column
merged_df = merged_df.drop(columns=['IID'])

# Step 7: Drop columns with any NaNs (only feature columns)
feature_cols = [col for col in merged_df.columns if col not in ['Subject ID', 'Labels']]
clean_features = merged_df[feature_cols].dropna(axis=1, how='any')
merged_df = pd.concat([merged_df[['Subject ID']], clean_features, merged_df[['Labels']]], axis=1)

# Step 8: Save final CSV
merged_df.to_csv(output_file, index=False)
print(f"Saved merged data to: {output_file}")

