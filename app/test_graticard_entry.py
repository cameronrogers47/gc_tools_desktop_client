"""
Created by Cameron Rogers
"""
import csv
import json
import pytest
from graticard_entry import GratiCardEntry
from process_files import CsvDocumentParser


def test_graticard_entry():
    entry = GratiCardEntry()
    entry.set_entry(recipient_name='John Doe',
                    address_line_1='123 Abc St',
                    address_line_2='Suite 101',
                    city='New York',
                    state='New York',
                    postal_code='12345',
                    gift='Nice bowls')
    assert entry.get_entry_json() == json.dumps({
        "recipient_name": 'John Doe',
        "address_line_1": '123 Abc St',
        "address_line_2": 'Suite 101',
        "city": 'New York',
        "state": 'New York',
        "postal_code": '12345',
        "gift": 'Nice bowls'
    })
    return entry


def test_graticard_entry_parse():
    entry = test_graticard_entry()
    entry.parse_address()
    print(entry.get_parsed_address())


def test_graticard_entry_parse_off_nominal_1():
    entry = test_graticard_entry()
    entry.set_postal_code(None)
    # with pytest.raises(Exception):
    entry.parse_address()
    assert entry.get_parsed_address() is None
    print(entry.get_parsed_address())


def test_graticard_entry_parse_external():
    entry = GratiCardEntry()
    entry.parse_external_address('123 Abc st new york ny 12345')
    print(entry.get_parsed_address())


def test_deserie():
    with open("data/Desirae_Sindelar_list.csv", 'r', encoding='latin-1') as fh:
        data = [row for row in csv.reader(fh)]
    all_items = []
    for item in data:
        entry = GratiCardEntry()
        entry.set_entry(recipient_name=item[0],
                        address_line_1=item[2],
                        city=item[3],
                        state=item[6],
                        postal_code=item[4],
                        gift=item[10])
        all_items.append(entry)
    print(all_items[12])
