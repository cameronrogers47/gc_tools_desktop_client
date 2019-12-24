"""
Created by Cameron Rogers
"""
from graticard_entry import GratiCardEntry

BLANK_FIELD = ""

AVAILABLE_FIELDS = {"Name": "recipient_name",
                    "Street Address": "full_street_address",
                    "City State Postal Code": "city_state_zip",
                    "Address Line 1": "address_line_1",
                    "Address Line 2": "address_line_2",
                    "City": "city",
                    "State": "state",
                    "Postal Code": "postal_code",
                    "Gift": "gift"}

ALL_ADDRESS_FIELDS = ("Street Address", "City State Postal Code", "Address Line 1",
                      "Address Line 2",  "City", "State", "Postal Code")

ADDRESS_SET_1 = ("Street Address", "City State Postal Code")
ADDRESS_SET_2 = ("Street Address", "City", "State", "Postal Code")
ADDRESS_SET_3 = ("Address Line 1", "Address Line 2", "City State Postal Code")
ADDRESS_SET_4 = ("Address Line 1", "Address Line 2", "City", "State", "Postal Code")
ADDRESS_SET_5 = ("Address Line 1", "City State Postal Code")
ADDRESS_SET_6 = ("Address Line 1", "City", "State", "Postal Code")

ALL_ADDRESS_SETS = (ADDRESS_SET_1,
                    ADDRESS_SET_2,
                    ADDRESS_SET_3,
                    ADDRESS_SET_4,
                    ADDRESS_SET_5,
                    ADDRESS_SET_6)


def parse_data_to_graticard_entry(data: list, column_map: list):
    print('parsing')
    fields_contained = [field for field in AVAILABLE_FIELDS if field in column_map]
    entries = []
    for entry in data:
        extract = {AVAILABLE_FIELDS[option]: entry[column_map.index(option)] for option in fields_contained}
        obj = GratiCardEntry()
        obj.set_entry(**extract)
        entries.append(obj)
    print('parsed')
    return entries
        

def validate_column_map(column_map: list):
    """
    Validates the column map or raises an InvalidColumnMapError exception
    
    Notes:
        Column maps must have a "Name" element
    """
    # reduce column map by removing blanks
    for i in range(column_map.count(BLANK_FIELD)):
        column_map.remove(BLANK_FIELD)
    
    # Check for unknown field
    for field in column_map:
        if field not in AVAILABLE_FIELDS:
            raise InvalidColumnMapError("Unknown field '{}' given in column map".format(field) +
                                        " Available fields are {}".format(AVAILABLE_FIELDS))
    
    # Check for Name
    if "Name" not in column_map:
        raise InvalidColumnMapError("The column map must contain 'Name'")
    
    # Check if any single address field is given
    if [True for field in ALL_ADDRESS_FIELDS if field in column_map]:
        address_set_found = False
        for address_set in ALL_ADDRESS_SETS:
            if _address_set_in_column_map(address_set, column_map):
                address_set_found = True
                break
        if not address_set_found:
            raise InvalidColumnMapError("When specifying addresses the column map must contain" +
                                        " at least one of the following sets {}".format(ALL_ADDRESS_SETS))

def _address_set_in_column_map(address_set: tuple, column_map: list):
    """Determines if all elements of the address set are in the column map"""
    for element in address_set:
        if element not in column_map:
            return False
    return True


class InvalidColumnMapError(Exception):
    pass
