"""
Created by Cameron Rogers
"""
import json
from scourgify import normalize_address_record


class GratiCardEntry:
    """
    Graticard entry that contains all data fields needed for a thank you card
    to be generated.
    """
    def __init__(self):
        self._recipient_name = None
        self._full_street_address = None
        self._city_state_zip = None
        self._address_line_1 = None
        self._address_line_2 = None
        self._city = None
        self._state = None
        self._postal_code = None
        self._gift = None
        self._parsed_address = None

    def get_recipient_name(self):
        return self._recipient_name

    def set_recipient_name(self, name: str):
        self._recipient_name = name

    def get_full_street_address(self):
        return self._full_street_address

    def set_full_street_address(self, street_address: str):
        self._full_street_address = street_address

    def get_city_state_zip(self):
        return self._city_state_zip

    def set_city_state_zip(self, city_state_zip: str):
        self._city_state_zip = city_state_zip

    def get_address_line_1(self):
        return self._address_line_1

    def set_address_line_1(self, address: str):
        self._address_line_1 = address

    def get_address_line_2(self):
        return self._address_line_2

    def set_address_line_2(self, address: str):
        self._address_line_2 = address

    def get_city(self):
        return self._city

    def set_city(self, city: str):
        self._city = city

    def get_state(self):
        return self._state

    def set_state(self, state: str):
        self._state = state

    def get_postal_code(self):
        return self._postal_code

    def set_postal_code(self, postal_code: str):
        self._postal_code = postal_code

    def get_city_state_postal_code(self):
        return "{} {} {}".format(self._city, self._state, self._postal_code)

    def get_gift(self):
        return self._gift

    def set_gift(self, gift: str):
        self._gift = gift

    def get_parsed_address(self):
        return self._parsed_address

    def set_entry(self,
                  recipient_name=None,
                  full_street_address=None,
                  city_state_zip=None,
                  address_line_1=None,
                  address_line_2=None,
                  city=None,
                  state=None,
                  postal_code=None,
                  gift=None):
        if recipient_name is not None:
            self.set_recipient_name(recipient_name)
        if full_street_address is not None:
            self.set_full_street_address(full_street_address)
        if city_state_zip is not None:
            self.set_city_state_zip(city_state_zip)
        if address_line_1 is not None:
            self.set_address_line_1(address_line_1)
        if address_line_2 is not None:
            self.set_address_line_2(address_line_2)
        if city is not None:
            self.set_city(city)
        if state is not None:
            self.set_state(state)
        if postal_code is not None:
            self.set_postal_code(postal_code)
        if gift is not None:
            self.set_gift(gift)

    def set_entry_with_address_dict(self,
                                    recipient_name: str,
                                    address_dict: dict,
                                    gift: str):
        self.set_entry(recipient_name=recipient_name,
                       address_line_1=address_dict['address_line_1'],
                       address_line_2=address_dict['address_line_2'],
                       city=address_dict['city'],
                       state=address_dict['state'],
                       postal_code=address_dict['postal_code'],
                       gift=gift)

    def get_entry_json(self):
        return json.dumps({
            "recipient_name": self.get_recipient_name(),
            "address_line_1": self.get_address_line_1(),
            "address_line_2": self.get_address_line_2(),
            "city": self.get_city(),
            "state": self.get_state(),
            "postal_code": self.get_postal_code(),
            "gift": self.get_gift()
        })

    def parse_address(self):
        address_options = (
            (self.get_full_street_address(),
             self.get_city_state_zip()),
            (self.get_address_line_1(),
             self.get_address_line_2(),
             self.get_city(),
             self.get_state(),
             self.get_postal_code()),
            (self.get_address_line_1(),
             self.get_city(),
             self.get_state(),
             self.get_postal_code()),
        )
        for option_set in address_options:
            if None not in option_set:
                self._parsed_address = normalize_address_record(
                    " ".join(option_set)
                )

    def parse_external_address(self, parsable_complete_address: str):
        self._parsed_address = normalize_address_record(
            parsable_complete_address
        )

    def __str__(self):
        if self.get_address_line_2() is None:
            return "{}\n{}\n{}".format(self.get_recipient_name(),
                                       self.get_address_line_1(),
                                       self.get_city_state_postal_code())
        return "{}\n{}\n{}\n{}".format(self.get_recipient_name(),
                                       self.get_address_line_1(),
                                       self.get_address_line_2(),
                                       self.get_city_state_postal_code())

    def __repr__(self):
        return "GratiCardEntry object for '{}'".format(self.get_recipient_name())
