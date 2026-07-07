from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from matcher import match_hotel
import csv
import io


app = FastAPI()


# ======================================================
# ЗАГРУЗКА НАШЕЙ БАЗЫ
# ======================================================

def load_base_hotels(filename):

    with open(filename, encoding="utf-8-sig") as f:
        hotels = list(csv.DictReader(f))

    for hotel in hotels:
        hotel["lat"] = float(hotel["lat"])
        hotel["lon"] = float(hotel["lon"])

    return hotels


# Загружаем базу один раз при запуске сервера

BASE_HOTELS = load_base_hotels(
    "01_hotels_base.csv"
)


print(f"Loaded hotels: {len(BASE_HOTELS)}")



# ======================================================
# ПРОВЕРКА API
# ======================================================

@app.get("/")
def home():
    return {
        "message": "Hotel matcher API works"
    }



# ======================================================
# CSV -> CSV
# ======================================================

@app.post("/match")
def match(file: UploadFile = File(...)):

    # читаем загруженный CSV

    content = file.file.read().decode("utf-8-sig")

    reader = csv.DictReader(
        io.StringIO(content)
    )


    results = []


    # обработка каждого внешнего отеля

    for external_hotel in reader:


        # если колонка называется id,
        # создаём external_id

        if "external_id" not in external_hotel:
            external_hotel["external_id"] = external_hotel["id"]


        external_hotel["lat"] = float(
            external_hotel["lat"]
        )

        external_hotel["lon"] = float(
            external_hotel["lon"]
        )


        result = match_hotel(
            external_hotel,
            BASE_HOTELS
        )


        results.append(result)



    # создаём CSV ответ

    output = io.StringIO()


    writer = csv.DictWriter(
        output,
        fieldnames=[
            "external_id",
            "hotel_id",
            "score"
        ]
    )


    writer.writeheader()
    writer.writerows(results)


    output.seek(0)



    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=matches.csv"
        }
    )



# ======================================================
# ЗАПУСК
# ======================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )