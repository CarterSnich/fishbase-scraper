import json

from scraper import FishBasePageScraper

fishes = (
    ["Chanos chanos", "bangus"],
    ["Neostethus thessa", "bolinao"],
    ["Katsuwonus pelamis", "budlis"],
    ["Sardinella lemuru", "tamban"],
    ["Oreochromis niloticus", "tilapia"],
    ["Nemipterus celebicus", "sagision"],
    ["Rastrelliger faughni", "burao"],
    ["Saurida undosquamis", "talho"],
    ["Leiognathus equula", "sapsap"],
    ["Mene maculata", "moonfish"],
)

data = {}

for fish in fishes:
    genus, species = fish[0].split(" ")

    print(fish)
    fb = FishBasePageScraper(genus, species)

    print(f"Scraping page: {fb.source_url}")
    fb.scrape_all()

    data[fish[1]] = {
        "binomial_name": fish[0],
        "english_name": fb.english_name,
        "popular_name": fish[1].capitalize(),
        "local_names": fb.local_names,
        "description": fb.description,
        "nutrients": fb.nutrients,
        "health_checks": fb.health_checks,
        "health_risks": fb.health_risks,
        "source": fb.source_url
    }

    print("Done.")

with open("fish-data.json", "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

print("Scraping done!")
