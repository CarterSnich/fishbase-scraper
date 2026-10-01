import json

from scraper import FishBasePageScraper

fishes = (
    "Chanos chanos",
    "Neostethus thessa",
    "Thunnus albacares",
    "Sardinella lemuru",
    "Oreochromis niloticus",
    "Nemipterus celebicus",
    "Rastrelliger Faughni",
    "Saurida Undosquamis"
)

data = {}

for fish in fishes:
    genus, species = fish.split(" ")

    print(fish)
    fb = FishBasePageScraper(genus, species)
    print(f"Scraping page: {fb.page_url}")
    fb.scrape_all()

    data[fish] = {
        "english_name": fb.english_name,
        "local_names": fb.local_names,
        "description": fb.description,
        "nutrients": fb.nutrients,
        "health_checks": fb.health_checks,
        "health_risks": fb.health_risks
    }

    print("Done.")

with open("fish-data.json", "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

print("Scraping done!")
