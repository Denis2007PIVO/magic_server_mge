from difflib import SequenceMatcher
from math import radians, sin, cos, sqrt, atan2


# ======================================================
# 1. ТРАНСЛИТЕРАЦИЯ
# ======================================================

def transliterate(text):

    mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',

        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    return ''.join(
        mapping.get(char, char)
        for char in text
    )



# ======================================================
# 2. СРАВНЕНИЕ НАЗВАНИЙ
# ======================================================

def similarity(a, b):

    a = transliterate(a).lower()
    b = transliterate(b).lower()

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()



# ======================================================
# 3. РАССТОЯНИЕ HAVERSINE
# ======================================================

def haversine(lat1, lon1, lat2, lon2):

    R = 6371

    lat1, lon1, lat2, lon2 = map(
        radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2 +
        cos(lat1) *
        cos(lat2) *
        sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c



# ======================================================
# 4. ГЕО-ФИЛЬТР
# ======================================================

def is_within_bbox(
        lat,
        lon,
        center_lat,
        center_lon,
        radius_km
):

    lat_delta = radius_km / 111

    lon_delta = radius_km / (
        111 * cos(radians(center_lat))
    )

    return (
        center_lat - lat_delta <= lat <= center_lat + lat_delta
        and
        center_lon - lon_delta <= lon <= center_lon + lon_delta
    )



# ======================================================
# 5. ОСНОВНОЙ МАТЧИНГ
# ======================================================

def match_hotel(
        external_hotel,
        base_hotels,
        radius_km=10
):

    best_score = -1
    best_match = None
    best_distance = None


    for hotel in base_hotels:


        # быстрый фильтр координат

        if not is_within_bbox(
                hotel["lat"],
                hotel["lon"],
                external_hotel["lat"],
                external_hotel["lon"],
                radius_km
        ):
            continue



        # точное расстояние

        distance = haversine(
            external_hotel["lat"],
            external_hotel["lon"],
            hotel["lat"],
            hotel["lon"]
        )


        if distance > radius_km:
            continue



        # сравнение названий

        text_score = similarity(
            external_hotel["name"],
            hotel["name"]
        )



        # гео оценка

        geo_score = max(
            0,
            1 - distance / radius_km
        )



        # итоговый рейтинг

        final_score = (
            0.7 * text_score +
            0.3 * geo_score
        )


        if final_score > best_score:

            best_score = final_score
            best_match = hotel
            best_distance = distance

    if best_match:
        return {
            "external_id": external_hotel.get("external_id"),
            "hotel_id": best_match["hotel_id"],
            "score": round(best_score, 3)
        }

    return {
        "external_id": external_hotel.get("external_id"),
        "hotel_id": None,
        "score": 0
    }