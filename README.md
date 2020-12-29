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

# Collect records into one file: `collect.py`
Clone this repository. Create a folder within the repository and move the attached emails into the folder. Assess the emails by typing the following into the terminal:
```
python collect.py
```

The program will prompt you for some information:
* The name of the folder. Type it exactly and press Enter. If the folder does not exist, the program will exit.
* What you want to name the spreadsheet.
  * If you press Enter without typing anything, the program will save the data to a CSV named with the send date of the first email assessed and the send date of the last email assessed, e.g., `records_2020-10-28_2020-11-11.csv`.
* If you select a name of a spreadsheet that already exists, you will be prompted to select one of the following options. Type the letter and press enter to select the optiono:
  * 'o': Overwrite previous spreadsheet. Deletes old spreadsheet and creates a new one.
  * 'e': Exit without analyzing any emails or changing anything about the old spreadsheet.
  * 'a': Append new records. Searches through the pre-existing spreadsheet and analyzes any records in the emails that that haven't been assessed yet. This option is helpful if the script exits while assessing files.

### Results of `collect.py`
The program will collect the URLs from the emails, extract information from each URL, and print its progress as it goes. Once it is done collecting these data, it will sort the results by species, hotspot, and date, and finally save them to a CSV. The columns of the CSV are:

* `species`: the species
* `url`: the url of the eBird checklist
* `individuals`: the number of individuals reported on the checklist
* `county`: the county from which the observation was submitted
* `hotspot`: the hotspot from which the observation was submitted, if any
* `date`: the observation date of the checklist
* `submitter`: the eBird display name of the person submitting the checklist
* `has_media`: whether the species observation has media associated with it.

You will have the option to save a copy of the CSV that contains only the records that had media associated with them. Type "y" and press Enter when prompted.
