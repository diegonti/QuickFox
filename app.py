from flask import Flask, render_template, request, session, send_file, url_for
from pathlib import Path
import random

THIS_FOLDER = Path(__file__).parent.resolve()

# Main app config
app = Flask(__name__,static_folder="./static/")
app.secret_key = 'foxitDAYNT'

# External variables
comm = dict()   # Should be external database + handle different users

############################## External functions ##############################
def extract_questions(game_types):
    """Extracts all the questions for the selected game_types."""
    questions = []
    for type in game_types:
        type_path = THIS_FOLDER / f"data/{type}.txt"
        with open(type_path,"r",encoding="utf-8") as inFile:
            for line in inFile:
                q = line.strip()
                questions.append([type,q])
    return questions



############################## Main Web App routes ##############################
@app.route('/')
def index():
    return render_template('index.html', text=None)

@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/select_boxes', methods=['GET', 'POST'])
def select_boxes():
    """Get selected boxes (game types) and extract questions"""

    if request.method == 'POST':
        selected_boxes = request.form.getlist('box')    # Collect selected boxes
        comm['selected_boxes'] = selected_boxes      # Store in comm

    # Get selected game_types
    game_types = comm.get("selected_boxes",["BEBER","INVITADOS","PDM","RETOS","TRIVIA","VOTAR"])
    if game_types == []: game_types = ["BEBER","INVITADOS","PDM","RETOS","TRIVIA","VOTAR"]

    # Open files and extract questions
    questions = extract_questions(game_types)

    comm["questions"] = questions

    return render_template("index.html",selected_boxes=selected_boxes)


@app.route('/next_question', methods=['POST'])
def next_question():
    """Selects and displays a random question from the pool. """

    # Get selected boxes
    game_types = comm.get("selected_boxes",["BEBER","INVITADOS","PDM","RETOS","TRIVIA","VOTAR"])
    if game_types == []: game_types = ["BEBER","INVITADOS","PDM","RETOS","TRIVIA","VOTAR"]

    # Get questions
    questions = comm.get("questions",[["INFO","Aquí apareceran las preguntas!"]])

    # Shuffle and select random question
    random.shuffle(questions)
    question_type, text_to_display = random.choice(questions)

    if question_type == "TRIVIA":
        text_to_display, answer_to_display = text_to_display.split("/R:")
        answer_to_display = f"R: {answer_to_display}"
    else:
        answer_to_display = None

    # Display type/text
    return render_template('index.html', 
                           question_type=question_type,
                           question_text=text_to_display,
                           selected_boxes=game_types,
                           answer_text=answer_to_display)


@app.route('/add_question', methods=['POST'])
def add_question():
    """Allows the user to add a question to the pool."""

    new_question = request.form.copy()
    question_type = new_question["dropdown_new"] # esto deberia ser seleccionable
    question_text = new_question["NEW_QUESTION_TEXT"]

    error_storage_full = None

    # check folder size 
    app_size = sum(f.stat().st_size for f in THIS_FOLDER.glob('**/*') if f.is_file())/1e6
    if app_size > 400.0:
        error_storage_full = "STORAGE FULL! You cannot add more questions :("
        print("STORAGE FULL! You cannot add more questions :(")
        return render_template("add.html",error_message=error_storage_full)
    else:
        new_path = THIS_FOLDER / f"data/{question_type}.txt"
        with open(new_path,"a",encoding="utf-8") as outFile:
            outFile.write(question_text + "\n")

        return render_template("index.html")




if __name__ == '__main__':
    app.run()
