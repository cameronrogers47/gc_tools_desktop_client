"""
Created by Cameron Rogers
"""
import pytest
import csv
from parser import (parse_data_to_graticard_entry, validate_column_map,
                    InvalidColumnMapError, ALL_ADDRESS_SETS)

TEST_FILE = "/Users/rogecame/test_ui/Desirae_Sindelar_list.csv"


def test_valid_column_map_name():
    column_map = []
    with pytest.raises(InvalidColumnMapError):
        validate_column_map(column_map)
    column_map += ["Name", ""]
    validate_column_map(column_map)

@pytest.mark.parametrize('address_set', list(ALL_ADDRESS_SETS))
def test_valid_column_map_address_variations(address_set):
    column_map = ["Name", "Gift"] + list(address_set) 
    validate_column_map(column_map)
    column_map.pop(-1)
    with pytest.raises(InvalidColumnMapError):
        validate_column_map(column_map)


def test_parse_data_to_graticard_entry():
    with open(TEST_FILE, 'r', encoding='latin-1') as fh:
        data = [row for row in csv.reader(fh)]
    column_map = ["" for i in range(len(data[0]))]
    column_map[0] = "Name"
    entries = parse_data_to_graticard_entry(data, column_map)
    print(len(entries))
