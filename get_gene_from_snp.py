import requests
import time

# ===== Step 1: Read SNP list from file =====
input_file_path = "/home/piyali/Piyali/Data/SNP/snp_names3.txt"

with open(input_file_path, "r") as f:
    snp_list = [line.strip() for line in f if line.strip()]

# ===== Step 2: Setup =====
server = "https://rest.ensembl.org"
ext = "/vep/human/id/"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

output_file_path = "/home/piyali/Piyali/Data/SNP/snp_to_gene_mapping3.txt"
with open(output_file_path, "w") as out_file:

    # ===== Step 3: Query and handle retries =====
    for snp in snp_list:
        success = False
        retries = 0
        max_retries = 5

        while not success and retries < max_retries:
            url = server + ext + snp
            response = requests.get(url, headers=headers)

            if response.ok:
                data = response.json()

                gene_name = None
                if data:
                    most_relevant = data[0]

                    if 'transcript_consequences' in most_relevant:
                        for consequence in most_relevant['transcript_consequences']:
                            if 'gene_symbol' in consequence:
                                gene_name = consequence['gene_symbol']
                                break

                if gene_name:
                    print(f"{snp} => {gene_name}")
                    out_file.write(f"{snp}\t{gene_name}\n")
                else:
                    print(f"{snp} => No gene found")
                    out_file.write(f"{snp}\tNo gene found\n")

                out_file.flush()
                success = True
                time.sleep(0.5)

            else:
                retries += 1
                wait_time = retries * 5  # Wait longer each retry: 5s, 10s, 15s...
                print(f"Error fetching {snp}. Retry {retries}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)

        if not success:
            print(f"Failed to fetch {snp} after {max_retries} retries.")
            out_file.write(f"{snp}\tFetch failed\n")
            out_file.flush()

print("Finished mapping!")

