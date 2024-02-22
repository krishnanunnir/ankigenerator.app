from flask import Flask, render_template, request, send_file
import json


app = Flask(__name__)

# Load data for one deck with 10 questions from the JSON file
with open("test.json", "r") as file:
    data = json.load(file)


@app.route("/")
def index():
    return render_template("index.html", data=data)


@app.route("/submit", methods=["POST"])
def submit():
    # Parse the form data into a Deck object
    form_data = request.form
    deck_data = {
        "title": form_data["title"],
        "questions": form_data.getlist("questions"),
    }
    deck = Deck(**deck_data)

    # Generate Anki deck
    anki_deck = generate_anki_deck(deck)

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
