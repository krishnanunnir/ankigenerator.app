import genanki
from typing import List
from pydantic import BaseModel, Field


class Card(BaseModel):
    question: str = Field(None, description="The question in the Anki deck")
    answer: str = Field(None, description="The answer to the question")


class Deck(BaseModel):
    name: str = Field(None, description="The name of the Anki deck")
    cards: List[Card] = Field(None, description="The cards in the Anki deck")


def generate_anki_deck(deck: Deck):
    model_id = genanki.Model.random_id()
    deck_id = genanki.Deck.random_id()

    anki_model = genanki.Model(
        model_id,
        "Simple Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
    )

    anki_deck = genanki.Deck(deck_id, deck.name)

    for card in deck.cards:
        anki_note = genanki.Note(
            model=anki_model,
            fields=[card.question, card.answer],
        )
        anki_deck.add_note(anki_note)

    output_file = f"{deck.name}.apkg"
    genanki.Package(anki_deck).write_to_file(output_file)
    print(f"Anki deck '{deck.name}' generated successfully. Output file: {output_file}")
