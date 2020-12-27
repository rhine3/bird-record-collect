import pandas as pd
from pathlib import Path

import time
import numpy as np
from datetime import datetime

import email
from email.message import get_body

class eBirdRecord():
    def __init__(self, url, species):
        # Get text from url
        self.species = species
        self.url = url
        self.html = self.set_html()
        self.individuals = self.set_individuals()
        self.county = self.set_county()
        self.hotspot = self.set_hotspot()
        self.date = self.set_date()
        self.observers = self.set_observers()

    def set_html(self):
        pass

    def set_individuals(self):
        pass

    def set_county(self):
        pass

    def set_hotspot(self):
        pass

    def set_date(self):
        pass

    def set_observers(self):
        pass

    def get_row(self):
        return {
            "species" : self.species,
            "url": self.url,
            "individuals" : self.individuals,
            "county" : self.county,
            "hotspot" : self.hotspot,
            "date" : self.date,
            "observers" : self.observers,
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
    body = my_email.get_payload()
    records = body.split('\n\n')

    # Get summmary of reports
    # A species might appear twice in this summary due to subspecies reports
    summary = records[1]
    species = [sp.split('(')[0].strip() for sp in summary.split('\n')]
    counts = [int(s.split(' ')[0]) for s in summary.split('(') if s.split(' ')[0].isdigit()]

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

if __name___ == __main__:
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
    early_date, late_date = get_dates(emails)
    df.to_csv(f"records_{early_date}-{late_date}.csv")
