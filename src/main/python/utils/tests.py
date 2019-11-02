def test_if_duplicated_first_value_in_line_items_contents(lst):
    """Takes components and amounts as a list of strings and floats, and returns true if there is at least one repeated component name."""
    first_value = lst[0::2]
    duplicated_first_value = [x for x in first_value if first_value.count(x) > 1]
    return bool(len(duplicated_first_value) > 0)


def test_if_empty_string_in_line_items_contents(lst):
    """Takes components and amounts as a list of strings and floats (origninating in line items), and returns true if there is at least one empty string."""
    empty_comps = [x for x in lst if x == ""]
    return bool(empty_comps)
