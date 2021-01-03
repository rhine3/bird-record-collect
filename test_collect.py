import numpy as np
import pytest
from collect import eBirdRecord

@pytest.fixture
def eBirdRecordToDict():
    def internal(url, species):
        rec = eBirdRecord(
            url=url,
            species=species,
        )
        return rec.get_row().iloc[0].to_dict()
    return internal


def test_eBirdRecord_unconfirmed_media(eBirdRecordToDict):
    output_dict = eBirdRecordToDict(
        url="https://ebird.org/checklist/S45704143",
        species="Razorbill"
    )
    
    true_dict = {
        'species': 'Razorbill',
        'url': 'https://ebird.org/checklist/S45704143',
        'individuals': '200',
        'county': 'Wexford County',
        'hotspot': '/hotspot/L2154897',
        'date': '2018-05-15',
        'submitter': 'Susan Mac',
        'has_media': True,
        'media_confirmed': False
    }
    
    assert output_dict == true_dict
    
def test_eBirdRecord_confirmed_media(eBirdRecordToDict):
    output_dict = eBirdRecordToDict(
        url="https://ebird.org/checklist/S78396122",
        species="Hoary Redpoll"
    )
    
    true_dict = {
        'species': 'Hoary Redpoll',
        'url': 'https://ebird.org/checklist/S78396122',
        'individuals': '1',
        'county': 'Centre County',
        'hotspot': '/hotspot/L13086405',
        'date': '2021-01-01',
        'submitter': 'Matt Kello',
        'has_media': True,
        'media_confirmed': True,
    }
    
    assert output_dict == true_dict
    
def test_eBirdRecord_bad_url(eBirdRecordToDict):
    bad_url = "https://ebird.org/checklist/S123456789123456789"
    species = "Razorbill"
    output_dict = eBirdRecordToDict(
        url=bad_url,
        species=species,
    )
    
    true_dict = {
        'species': species,
         'url': bad_url,
         'individuals': np.nan,
         'county': None,
         'hotspot': None,
         'date': None,
         'submitter': None,
         'has_media': False,
         'media_confirmed': False,
    }
    
    assert output_dict == true_dict
    
def test_eBirdRecord_bad_species(eBirdRecordToDict):
    url = "https://ebird.org/checklist/S78396122"
    bad_species = "Andean Cock-of-the-rock"
    
    output_dict = eBirdRecordToDict(
        url=url,
        species=bad_species,
    )
    
    
    true_dict = {
        'species': bad_species,
        'url': url,
        'individuals': np.nan,
        'county': 'Centre County',
        'hotspot': '/hotspot/L13086405',
        'date': '2021-01-01',
        'submitter': 'Matt Kello',
        'has_media': False,
        'media_confirmed': False,
    }
    
    assert output_dict == true_dict
    
