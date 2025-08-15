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

def word_similarity(text1, text2):
    """Return the proportion of words in the shorter text that are also in the longer one."""
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    set1, set2 = set(words1), set(words2)
    common = len(set1 & set2)
    shorter_len = min(len(set1), len(set2))
    if shorter_len == 0:
        return 0
    return common / shorter_len

def remove_near_duplicates(texts, threshold=0.4):
    """Given a list of texts, remove near duplicates based on word overlap."""
    unique_texts = []
    for text in texts:
        is_duplicate = False
        for kept in unique_texts:
            if word_similarity(text, kept) >= threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_texts.append(text)
    return unique_texts

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

    # --- Step 3: Remove near duplicates ---
    for species_id in species_texts:
        species_texts[species_id] = remove_near_duplicates(species_texts[species_id], threshold=0.8)

    # --- Step 4: Write combined output ---
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
