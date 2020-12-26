import pandas as pd

class eBirdRecord():
    def __init__(self, url, species):
        # Get text from url
        self.species = species
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
            "individuals" : self.individuals,
            "county" : self.county,
            "hotspot" : self.hotspot,
            "date" : self.date,
            "observers" : self.observers,
        }

def get_dates(paths_to_emails):
    """Finds the earliest and latest dates of the collected emails
    """
    early_date = None
    late_date = None
    for path_to_email in paths_to_emails:
        email_date = None
        if email_date < early_date:
            early_date = email_date
        if email_date > late_date:
            late_date = email_date
    return early_date, late_date

def url_and_species_from_email(path_to_email):
    urls = None
    species = None
    return zip(urls, species)


if __name___ == __main__:
    # Get URLs and species from the email
    urls_and_species = []
    for email in emails:
        email_pairs = url_and_species_from_email(email)
        urls_and_species.extend(email_pairs)

    # Create list of eBirdRecords
    records = []
    for url_and_species in urls_and_species:
        url, species = url_and_species
        records.append(eBirdRecord(url, species))

    # Make dataframe of info about records
    df = pd.DataFrame()
    for record in records:
        df = df.append(record.get_row())

    # Save this information
    early_date, late_date = get_dates(emails)
    df.to_csv(f"records_{early_date}-{late_date}.csv")
