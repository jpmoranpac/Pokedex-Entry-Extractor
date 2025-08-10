import requests
import csv
from io import StringIO
from collections import defaultdict

# Raw CSV URLs from veekun GitHub
FLAVOR_TEXT_URL = (
    "https://raw.githubusercontent.com/veekun/pokedex/master/"
    "pokedex/data/csv/pokemon_species_flavor_text.csv"
)
SPECIES_URL = (
    "https://raw.githubusercontent.com/veekun/pokedex/master/"
    "pokedex/data/csv/pokemon_species.csv"
)

def fetch_csv(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return StringIO(resp.text)

def extract_all_species_with_names(output_path):
    # --- Step 1: Load species names ---
    species_names = {}
    species_file = fetch_csv(SPECIES_URL)
    species_reader = csv.DictReader(species_file)
    for row in species_reader:
        species_id = int(row["id"])
        species_names[species_id] = row["identifier"]  # lowercase name

    # --- Step 2: Load flavor texts ---
    species_texts = defaultdict(set)
    flavor_file = fetch_csv(FLAVOR_TEXT_URL)
    flavor_reader = csv.DictReader(flavor_file)
    for row in flavor_reader:
        if int(row["language_id"]) == 9:  # English only
            species_id = int(row["species_id"])
            text = row["flavor_text"].replace("\n", " ").replace("\f", " ").strip()
            species_texts[species_id].add(text)

    # --- Step 3: Write combined output ---
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["species_id", "name", "flavor_texts"])
        for species_id in sorted(species_texts.keys()):
            name = species_names.get(species_id, "UNKNOWN")
            combined = " | ".join(sorted(species_texts[species_id]))
            writer.writerow([species_id, name, combined])

    print(f"Wrote {len(species_texts)} species to {output_path}")

if __name__ == "__main__":
    extract_all_species_with_names("pokemon_flavor_texts.csv")
