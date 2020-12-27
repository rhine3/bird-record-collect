import pandas as pd
from pathlib import Path
import time
import numpy as np
from datetime import datetime
import email
import re
import requests
from bs4 import BeautifulSoup

class eBirdRecord():
    def __init__(self, url, species):
        assert(url[:4] == "http")
        # Get text from url
        self.species = species
        self.url = url
        self.html = self.set_html()
        self.record = self.set_record()
        self.individuals = self.set_individuals()
        self.county = self.set_county()
        self.hotspot = self.set_hotspot()
        self.date = self.set_date()
        self.submitter = self.set_submitter()
        self.has_media = self.set_has_media()

    def __repr__(self):
        return f"eBirdRecord('{self.url}', '{self.species}')"

    def set_record(self):
        results = self.html.find_all('li')
        for result in results:
            birds = result.find_all('span', {'class':'Heading-main'})
            for bird in birds:
                if bird.contents[0] == self.species:
                    record = result.contents
        return record

    def set_html(self):
        r = requests.get(self.url)
        return BeautifulSoup(r.text, features="lxml")

    def set_individuals(self):
        # Number observed
        return self.record[1].find('div', {'class':"Observation-numberObserved"}).contents[1].contents[3].contents[0]

    def set_county(self):
        return self.html.find_all('a', {"title":re.compile("^Region page for.*County")})[0].contents[0]

    def set_hotspot(self):
        # Searching for "a" because hotspots have links
        location = self.html.find_all('div', {"class":"Heading Heading--h3 u-margin-none"})[0].find('a')
        if location != None:
            return location['href']
        else:
            return None

    def set_date(self):
        string = self.html.title.contents[0].split('-')[1].strip()
        return datetime.strptime(string, "%d %b %Y")

    def set_submitter(self):
        return self.html.find_all("meta", {"name":"author"})[0]["content"]

    def set_has_media(self):
        return self.record[1].find("div", {"data-media-commonname":self.species}) != None

    def get_row(self):
        return {
            "species" : self.species,
            "url": self.url,
            "individuals" : self.individuals,
            "county" : self.county,
            "hotspot" : self.hotspot,
            "date" : self.date,
            "submitter" : self.submitter,
            "has_media" : self.has_media,
        }

def get_email(path_to_email):
    """Return email.Message
    """
    with open(path_to_email, 'r') as f:
        msg = email.message_from_file(f)
    return msg

def get_dates(paths_to_emails):
    """Finds the earliest and latest dates of the collected emails
    """
    early_date = None
    late_date = None
    for path_to_email in paths_to_emails:
        msg = get_email(path_to_email)
        email_date = datetime.fromtimestamp(
            time.mktime(
                email.utils.parsedate(
                    msg['date']
                )
            )
        )
        if early_date is None or email_date < early_date:
            early_date = email_date
        if late_date is None or email_date > late_date:
            late_date = email_date
    return early_date, late_date

def url_and_species_from_email(path_to_email):
    # Get body from email
    body = get_email(path_to_email).get_payload()
    records = body.split('\n\n')

    # Get summmary of reports
    # A species might appear twice in this summary due to subspecies reports
    summary = records[1]
    species = [sp.split('(')[0].strip() for sp in summary.split('\n')]

    # Get counts for reports
    # Reports from multiple counties are in the format 'Sedge Wren (8 Chester, 2 Luzerne)'
    counts = []
    for ssp in summary.split('\n'):
        number_of_this_ssp = 0
        for ssp_num in ssp.split(' '):
            stripped = ssp_num.strip('(')
            if stripped.isdigit():
                number_of_this_ssp += int(stripped)
        counts.append(number_of_this_ssp)

    # Get URL for each report
    reports = []
    species_unique = np.unique(np.array(species))
    for idx, record in enumerate(records):
        for sp in species_unique:
            length = len(sp)
            if record[:length] == sp and "Reported" in record:
                url = record.split("Checklist")[1].strip(": ").split('\n')[0]
                reports.append((url, sp))


    # Get the number of counts that should be there
    desired_count_dict = {}
    for idx, sp in enumerate(species):
        # This method accounts for a species appearing multiple times in `species` array
        if sp in desired_count_dict.keys():
            desired_count_dict[sp] += counts[idx]
        else:
            desired_count_dict[sp] = counts[idx]

    # Get the number of counts actually there
    true_count_dict = {}
    for report in reports:
        sp = report[1]
        if sp in true_count_dict.keys():
            true_count_dict[sp] += 1
        else:
            true_count_dict[sp] = 1

    assert(true_count_dict == desired_count_dict)
    return reports

if __name__ == '__main__':
    paths_to_emails = list(Path().glob("**/*.eml"))

    # Get URLs and species from the email
    urls_and_species = []
    for path_to_email in paths_to_emails:
        email_pairs = url_and_species_from_email(path_to_email)
        urls_and_species.extend(email_pairs)

    # Create list of eBirdRecords
    records = []
    for url_and_species in urls_and_species:
        url, species = url_and_species
        records.append(eBirdRecord(url, species))

    # Make dataframe of info about records
    df = pd.DataFrame()
    for record in records:
        df = df.append(record.get_row(), ignore_index=True)

    # Save this information
    early_date, late_date = get_dates(paths_to_emails)
    df.to_csv(f"records_{early_date.date()}_{late_date.date()}.csv", index=False)
