from flask import Flask, render_template, request, send_file
import json

from api_code import (
    generate_anki_deck,
    openai_parse_webpage,
    QuestionAnswer,
    QuestionDeck,
    generate_and_write_anki_deck,
)


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    input_text = None
    name = None
    length = None
    if request.method == "POST":
        input_text = request.form["input_text"]
        question_deck = openai_parse_webpage(input_text)
        return render_template("index.html", data=question_deck)
    return render_template(
        "template.html", input_text=input_text, name=name, length=length
    )


@app.route("/submit", methods=["POST"])
def submit():
    # Parse the form data into a Deck object
    form_data = dict(request.form)
    topic = form_data.pop("topic")
    deck = QuestionDeck(topic, [])
    for i in range(1, len(form_data.keys()) // 2 + 1):
        question = form_data.get(f"question-{i}")
        answer = form_data.get(f"answer-{i}")
        deck.question_list.append(QuestionAnswer(question, answer))

    # Generate Anki deck
    anki_deck = generate_and_write_anki_deck(deck)

    # Save the Anki deck to a file
    deck_filename = "generated_deck.apkg"
    anki_deck.write_to_file(deck_filename)

    # Provide a download link for the user
    return render_template("download.html", filename=deck_filename)


@app.route("/download/<filename>")
def download(filename):
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
