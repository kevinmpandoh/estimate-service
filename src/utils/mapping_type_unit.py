from .entry_map import entry_map

def get_entry_category(merek, tipe):
    merek = str(merek).upper()
    tipe = str(tipe).upper()

    if merek in entry_map:
        for level, tipe_list in entry_map[merek].items():
            for t in tipe_list:
                if t in tipe:
                    return level
    return "Unknown"
