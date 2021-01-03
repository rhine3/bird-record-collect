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
        if self.html == None:
            self.record = None
            self.individuals = np.nan
            self.county = None
            self.hotspot = None
            self.date = None
            self.submitter = None
            self.has_media = None
            self.media_confirmed = None
        else:
            self.record = self.set_record()
            self.individuals = self.set_individuals()
            self.county = self.set_county()
            self.hotspot = self.set_hotspot()
            self.date = self.set_date()
            self.submitter = self.set_submitter()
            self.has_media = self.set_has_media()
            self.media_confirmed = self.set_media_confirmed()

    def __repr__(self):
        return f"eBirdRecord('{self.url}', '{self.species}')"

    def set_html(self):
        r = requests.get(self.url)
        # Handle deleted checklists
        if r.status_code == 400:
            return None
        return BeautifulSoup(r.text, features="html.parser")

    def set_record(self):
        results = self.html.find_all('li')
        record = None
        for result in results:
            birds = result.find_all('span', {'class':'Heading-main'})
            for bird in birds:
                if bird.contents[0] == self.species:
                    record = result.contents
        return record

    def set_individuals(self):
        if self.record == None:
            return np.nan
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
            return np.nan

    def set_date(self):
        string = self.html.find_all("span", {"class":"Heading-main"})[0].contents[-1].strip()
        return datetime.strptime(string, "%d %b %Y").date()

    def set_submitter(self):
        return self.html.find_all("meta", {"name":"author"})[0]["content"]

    def set_has_media(self):
        if self.record == None:
            return False
        return self.record[1].find("div", {"data-media-commonname":self.species}) != None

    def set_media_confirmed(self):
        if self.record == None:
            return False
        else:
            # Check the ML page for the first media to see if it's confirmed
            # (eBird checklists no longer show confirmation)
            asset_url = "https://macaulaylibrary.org/asset/" + self.record[1].find('div', {"data-media-commonname":self.species})['data-media-id']
            r = requests.get(asset_url)
            if r.status_code == 400:
                return False
            if BeautifulSoup(r.text, features='html.parser').find("span", {"title":"Unconfirmed"}):
                return False
            else:
                return True
    
    def get_row(self):
        return pd.DataFrame(
            {
                "species" : pd.Series([self.species], dtype='str'),
                "url": pd.Series([self.url], dtype='str'),
                "individuals" : pd.Series([self.individuals], dtype='str'),
                "county" : pd.Series([self.county], dtype='str'),
                "hotspot" : pd.Series([self.hotspot], dtype='str'),
                "date" : pd.Series([self.date], dtype='str'),
                "submitter" : pd.Series([self.submitter], dtype='str'),
                "has_media" : pd.Series([self.has_media], dtype='bool'),
                "media_confirmed" : pd.Series([self.media_confirmed], dtype='bool'),
            },
        )

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
    folder = input("Type name of folder containing emails: ")
    if not Path(folder).exists():
        print("Folder not found. Exiting.")
        exit()

    paths_to_emails = list(Path(folder).glob("**/*.eml"))
    print(f"Assessing {len(paths_to_emails)} emails from {folder}")

    # Get URLs and species from the email
    urls_and_species = []
    for path_to_email in paths_to_emails:
        email_pairs = url_and_species_from_email(path_to_email)
        urls_and_species.extend(email_pairs)
    urls_and_species = list(set(urls_and_species))

    # Create filename
    print()
    save_path = input("Type name of results csv, or press Enter to use default filename: ")
    if not save_path:
        early_date, late_date = get_dates(paths_to_emails)
        save_path = Path(f"records_{early_date.date()}_{late_date.date()}.csv")
    elif save_path[-4:] != '.csv':
        save_path += '.csv'
        save_path = Path(save_path)
    print(f"Saving results to {save_path}")

    # Decide what to do when spreadsheet by the chosen name already exists
    if save_path.exists():
        print()
        print(f"File {str(save_path)} already exists.")
        delete = input("Overwrite (o), exit without analyzing files (e), or append new records to file (a)? ")
        while delete.lower() not in ['o', 'e', 'a']:
            delete = input('  Type "o" to overwrite file, "e" to exit, or "a" to append new records to file: ')
        if delete.lower() == 'o':
            print("Deleting.")
            save_path.unlink()
        elif delete.lower() == 'a':
            original_df = pd.read_csv(save_path)
            original_urls_and_species = list(zip(original_df['url'],original_df['species']))
            overlap = set(urls_and_species).intersection(set(original_urls_and_species))
            urls_and_species = list(set(urls_and_species) - overlap)
            print(f"Skipping {len(overlap)} records that are already in {str(save_path)}")
        else:
            print("Exiting.")
            exit()


    # Assess each record and save it to file
    print()
    print(f"Assessing {len(urls_and_species)} new records")
    for idx, url_and_species in enumerate(urls_and_species):
        url, species = url_and_species
        print(f"{idx+1} Assessing {url} - {species}")
        record = eBirdRecord(url, species).get_row()
        if save_path.exists():
            record.to_csv(save_path, header=None, mode="a", index=False)
        else:
            record.to_csv(save_path, index=False)
    print("Done collecting records.")

    # Sort and organize records
    records = pd.read_csv(save_path, parse_dates=['date'])
    records = records[records['has_media']]
    records = records.sort_values(["species", "county", "hotspot", "date"]).reset_index(drop=True)
    records.to_csv(save_path, index=False)
    print("Sorted records by species, county, hotspot, and date.")
    print(f"Records are now saved in {save_path}")

    # Give option to save new file of records without media
    print()
    delete_without_media = input("Save a version of spreadsheet only containing records with media? (y/n) ")
    while delete_without_media.lower() not in ['y', 'n']:
            delete_without_media = input('  Type "y" to create a new spreadsheet only containing records with media or "n" to exit: ')
    if delete_without_media.lower() == 'y':
        records = records[records['has_media']]
        new_save_path = 'has_media_' + str(save_path)
        records.reset_index(drop=True).to_csv(new_save_path, index=False)
        print(f"Records containing media saved to {new_save_path}")
