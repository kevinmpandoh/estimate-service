from .mapping_damage import damage_map

def normalize_damage(text: str) -> str:
    text = text.lower().strip()
    for raw, normalized in damage_map.items():
        if raw in text:
            return normalized
    return text
