import logging
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
import genanki
import os
from typing import List
from pydantic import BaseModel, Field
import random
from os import environ
from openai import OpenAI
import datetime
from s3_utils import upload_to_s3, generate_donload_link

logger = logging.getLogger(__name__)


class QuestionAnswer(BaseModel):
    question: str = Field(None, description="The question to ask")
    answer: str = Field(None, description="The answer to the question")

    def __init__(self, question, answer):
        super().__init__(question=question, answer=answer)


class QuestionDeck(BaseModel):
    topic: str = Field(None, description="The name of the anki deck")
    question_list: List[QuestionAnswer] = Field(
        None, description="The list of questions"
    )

    def __init__(self, topic, question_list):
        super().__init__(topic=topic, question_list=question_list)


OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"


model_3 = "gpt-3.5-turbo-0125"


def openai_parse_webpage(input_text):
    parser = PydanticOutputParser(pydantic_object=QuestionDeck)
    text = """

    I am currently going through the following text to learn more about it

    {input_content_for_deck}

    I am really curious about this topic and the concepts that it involves. I want you to generate questions and their answers
    that will help me understand it better. I want you to ask me questions that will help me push my understanding of said topic better
    it doesn't matter if I'm not capable of answering cause my goal is to learn more and more.

    Ask as many questions as you can think of. I want to learn as much as possible from this.

    I want atleast 20 questions and their answers.

    Make the answers detailed and informative.

    The question and answer format should be as follows:
    {format_instructions}

    """

    prompt = ChatPromptTemplate(
        messages=[HumanMessagePromptTemplate.from_template(text)],
        input_variables=["input_content_for_deck"],
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
        },
    )
    llm = ChatOpenAI(temperature=0.9, model=model_3, openai_api_key=OPENAI_API_KEY)
    input = prompt.format_prompt(input_content_for_deck=input_text)
    input.to_messages()
    output = llm(input.to_messages())
    parsed = parser.parse(output.content)
    return parsed


def generate_anki_deck(question_deck: QuestionDeck):
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)

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

    anki_deck = genanki.Deck(deck_id, question_deck.topic)

    for qa in question_deck.question_list:
        anki_note = genanki.Note(
            model=anki_model,
            fields=[qa.question, qa.answer],
        )
        anki_deck.add_note(anki_note)
    current_time = datetime.datetime.now().strftime("%H-%M-%S")

    # Prepend current time to deck name
    output_file = os.path.join("decks", f"{current_time}_{question_deck.topic}.apkg")
    genanki.Package(anki_deck).write_to_file(output_file)
    print(
        f"Anki deck '{question_deck.topic}' generated successfully. Output file: {output_file}"
    )
    return output_file


def generate_and_write_anki_deck(input_text: str):
    parsed = openai_parse_webpage(input_text)
    output_file = generate_anki_deck(parsed)
    upload_to_s3(output_file)
    url = generate_donload_link(output_file)
    return url
