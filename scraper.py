import json, os, requests, re
from urllib.parse import urljoin
from lxml import html, etree


class FishBasePageScraper:
    english_name: str = ""
    local_names: list = []
    description: str = ""
    nutrients: dict = {}
    health_checks: list = []
    health_risks: list = []


    def __init__(self, genus: str, species: str, base_url='https://fishbase.se/'):
        self.page_url = urljoin(base_url, f'summary/{genus}_{species}.html')
        self.tree = self.scrape_page()


    def scrape_page(self):
        response = requests.get(self.page_url, timeout=10)
        response.raise_for_status()

        return html.fromstring(response.content)


    def scrap_names(self):
        href = self.tree.xpath('//*[@id="ss-main"]/div[18]/span/span[3]/a/@href')[0]
        xml_url = urljoin(self.page_url, href)

        xml = requests.get(xml_url, timeout=10)
        xml.raise_for_status()
        xml_root = etree.fromstring(xml.content)

        comnames = xml_root.xpath('//fishbase/comnames[country="Philippines"]')

        local_names = []

        for comname in comnames:
            language = comname.xpath('./language/text()')
            name = comname.xpath('./comname/text()')

            if not language or not name:
                continue

            if language[0] == 'English':
                self.english_name = name[0]
            else:
                local_names.append(name[0])

        self.local_names = sorted(set(local_names))
        return self.english_name, self.local_names


    def scrape_description(self):
        span = self.tree.xpath('//*[@id="ss-main"]/div[5]/span')
        text = ''.join(span[0].xpath('.//text()'))

        prompt = f'''
        Make this description human understandable. Make it a paragraph. Remove any sort of reference number. : 
        \"{text}\"
        '''

        self.description = prompt_ai(prompt.strip())
        return self.description


    def scrape_nutrients(self):
        td = self.tree.xpath('//*[@id="estimates_model"]//tr[9]/td[2]')

        if len(td) == 0:
            return {}

        text = td[0].xpath('./text()')[0]

        pattern = re.compile(r"(\w+)\s*=\s*([\d.]+)\s*\[([\d.]+),\s*([\d.]+)]\s*(.+)")

        for item in text.split(";"):
            match = pattern.match(item.strip())

            if not match:
                continue

            name, value, min_value, max_value, unit = match.groups()

            self.nutrients[name.lower()] = {
                "value": float(value),
                "min": float(min_value),
                "max": float(max_value),
                "unit": unit.strip()
            }

        return self.nutrients


    def scrape_health_checks(self):
        if len(self.nutrients) <= 0:
            return {
                'risks': [],
                'benefits': [],
            }

        prompt = f'''
        Create health checks very brief descriptions (risks and benefits) from the data below,
        without numerical values.
        For example, "High in Protein" as benefit and "Mercury poisoning" for risks. 
        Create an JSON object with keys `risks` and `benefits`. 
        Store the health checks on the corresponding keys.
        Make sure to just return a string of JSON response.

        ```{self.nutrients}```
        '''

        json_string = prompt_ai(prompt)
        parsed = json.loads(json_string)

        self.health_checks = parsed['benefits']
        self.health_risks = parsed['risks']

        return parsed


    def scrape_all(self):
        self.scrap_names()
        self.scrape_description()
        self.scrape_nutrients()
        self.scrape_health_checks()


def prompt_ai(prompt_message: str):
    headers = {
        "Authorization": f"Bearer {os.getenv("OLLAMA_API_KEY")}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-oss:120b-cloud",
        "prompt": prompt_message,
        "stream": False
    }

    response = requests.post("https://ollama.com/api/generate", json=payload, headers=headers)
    response.raise_for_status()
    response_data = response.json()

    return response_data['response']


if __name__ == '__main__':
    fb = FishBasePageScraper("Chanos", "chanos")
    print(fb.scrap_names())
