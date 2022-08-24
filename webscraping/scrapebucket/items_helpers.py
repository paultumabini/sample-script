import re

"""The followings are custom item helper functions that filter, extract or clean items."""

# remove char in a string
def remove_char_from_str(val):
    value = val
    char = ['-100x100', 'Stock:', 'Stock #:', '-new', '-167x93', 'thumb_']
    strings = []

    for c in char:
        if c in value:
            strings.append(c)
            for s in strings:
                value = value.replace(s, '')
    return value


# remove new line, tab and spaces
def remove_trailing_spaces(value):
    return re.sub(r'[\n\t]*', '', value).strip() if bool(re.search(r'[\n\t]', value)) else value


#  remove all non-numeric characters in a string (e.g: "Stock:", "Stock#:")
def remove_non_numeric(value):
    if isinstance(value, str) and 'XB' not in value and '.' not in value and 'U' not in value and 'N' not in value:
        return re.sub(r'[^0-9]', '', value) if any(char.isdigit() for char in value) else 0
    return 0 if not value or value == '' else value


# extract vin from a url:
def extract_vin(value):
    value = re.sub(r'[\n\t/]*', '', value).strip() if bool(re.search(r'[\n\t/]', value)) else value
    xtract_vin = value.split('-')[-1] if len(value.split('-')[-1]) == 17 else value

    char = ['VIN', ':']
    strings = []

    for c in char:
        if c in xtract_vin:
            strings.append(c)
            for s in strings:
                xtract_vin = xtract_vin.replace(s, '')
    return xtract_vin


# set category
def set_category(value):
    return 'used' if 'used' in value.lower() else 'new' if 'new' in value.lower() else ''
