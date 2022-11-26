import json


def load_db():
    with open("data/chemistry_flashcards.json", "r") as f:
        return json.load(f)


def save_db():
    with (open("data/chemistry_flashcards.json", "w")) as f:
        return json.dump(db, f)


db = load_db()
