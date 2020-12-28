# bird-record-collect
This code helps you collect data from eBird Needs Alerts into a table. This code is in use by the [Pennsylvania Ornithological Records Committee](https://pabirds.org/records).

# Create needs alert
To use the code, set up an eBird needs alert. In our case, we set up an eBird account with one historical checklist containing all of the regular (non-review species) in Pennsylvania. Then we set up the account to send daily emails containing life needs alerts for the state of Pennsylvania. This effectively emails us any records of any state-level review list species.

# Download emails
Download the emails in .eml format. In Gmail, this can be accomplished with the following steps.
1. Select the emails you want to download
2. Press the three dots "menu" button
3. Select "Forward as attachment"
4. Forward to yourself
5. Download the attached emails.

# Assess emails using script
Clone this repository. Create a folder within the repository and move the attached emails into the folder. Then, assess the emails by typing the following into the terminal:
```
python collect.py
```
The program will prompt you to type the name of the folder. Type it exactly and press enter. Then, the program will collect the URLs from the emails, extract information from each URL, and print its progress as it goes. Once it is done collecting these data, it will save the data to a .CSV named with the date of the first email assessed and the date of the last email assessed, e.g., `records_2020-10-28_2020-11-11.csv`.

The columns of the CSV are:
* `species`: the species
* `url`: the url of the eBird checklist
* `individuals`: the number of individuals reported on the checklist
* `county`: the county from which the observation was submitted
* `hotspot`: the hotspot from which the observation was submitted, if any
* `date`: the observation date of the checklist
* `submitter`: the eBird display name of the person submitting the checklist
* `has_media`: whether the species observation has media associated with it.
