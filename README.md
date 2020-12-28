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
python collect.py name_of_folder
```
