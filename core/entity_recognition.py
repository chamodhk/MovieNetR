from gliner import GLiNER
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

BLACKLIST = {"movie", "movies"}

def filter_entities(entities):
    clean = set()
    for en in entities:
        name = en["text"].strip().lower() 
        count = 0

        for black in BLACKLIST:
            if black in name:
                count += 1
                break 

        if count > 0:
            continue

        clean.add(name.title())
    return clean 

def get_movies(text, threshold = 0.5):
    entities = model.predict_entities(
        text,
        labels = ["Movie"],
        threshold = threshold 
    )

    movies = filter_entities(entities)

    return movies

