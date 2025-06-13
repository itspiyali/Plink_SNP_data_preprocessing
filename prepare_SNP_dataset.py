import numpy as np
import pandas as pd
import argparse


def arrange(path, classes=4, label_file_path="/home/piyali/Piyali/Data/Imaging/Info/MRI_T1.csv", output_path="/home/piyali/Piyali/Data/SNP/Main_SNP_data_files/mySNP_data.csv"):
    df = pd.read_csv(path, sep=" ")
    df = df.drop(columns=["FID", "PAT", "MAT", "SEX", "PHENOTYPE"])
    df.columns = df.columns.str.replace(r"_(A|C|G|T)", "", regex=True)
    
    # Remove duplicate columns based on identical values 
    df = df.loc[:, ~df.T.duplicated()]

    # Load the label file
    labels_df = pd.read_csv(label_file_path, sep=",")  
    labels_df = labels_df.rename(columns={"Subject ID": "IID", "Research Group": "labels"})
    labels_df["IID"] = labels_df["IID"].str.replace(r"\+AF8-", "_", regex=True)
    
    df_new = df.merge(labels_df[["IID", "labels"]], on="IID", how="left")
    

    if classes == 6:
        label_map = {
        "CN": 0,
        "SMC": 1,
        "EMCI": 2,
        "MCI": 3,
        "LMCI": 4,
        "AD": 5
    }
        df_new["labels"] = df_new["labels"].map(label_map)
        
    elif classes == 4:
        label_map = {
        "CN": 0,
        "SMC": 1,
        "EMCI": 1,
        "MCI": 2,
        "LMCI": 3,
        "AD": 3
    }
        df_new["labels"] = df_new["labels"].map(label_map)
        
    elif classes == 3:
        label_map = {
        "CN": 0,
        "SMC": 1,
        "EMCI": 1,
        "MCI": 1,
        "LMCI": 2,
        "AD": 2
    }
        df_new["labels"] = df_new["labels"].map(label_map)

    df_new.to_csv(output_path, index=False)  


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--data", type=str, required=True, help="path to the dataset")
    parser.add_argument("--classes", type=int, default=4, help="Number of classes- either 3, 4 or 6")
    parser.add_argument("--labels", type=str, default="/home/piyali/Piyali/Data/Imaging/Info/MRI_T1.csv", help="path for the labels corresponding to each subject")
    parser.add_argument("--output", type=str, default="/home/piyali/Piyali/Data/SNP/Main_SNP_data_files/mySNP_data.csv", help="path where output file is to be saved")
    
    args = parser.parse_args()

    arrange(path=args.data, classes=args.classes, label_file_path=args.labels, output_path=args.output)

