
def convert_dict_area_to_tuple(d: dict) -> tuple:
    res = (d["left"], d["top"], d["width"], d["height"])
    return res

monitor = {"top": 10, "left": 15, "width": 1820, "height": 1050}
print(convert_dict_area_to_tuple(monitor))
