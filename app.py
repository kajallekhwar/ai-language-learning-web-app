from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import sqlite3
import requests
import os

# --------- CONFIG ----------
DATABASE = 'app.db'
SECRET_KEY = 'mysecretkey'
LIBRE_URL = "https://libretranslate.de/translate"
# ---------------------------

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ---------------- DATABASE HELPERS ----------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        # connect (file will be created if not exist)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    data = cur.fetchall()
    cur.close()
    return (data[0] if data else None) if one else data


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


# ---------------- SCHEMA / INIT ----------------
def init_db():
    """Ensure the DB file exists and required tables are created using schema.sql"""
    created = False
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # check for 'users' table (as principal table)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not cur.fetchone():
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            cur.close()
            conn.close()
            raise FileNotFoundError(f"schema.sql not found at {schema_path}. Please add it.")
        with open(schema_path, "r", encoding="utf-8") as f:
            script = f.read()
            conn.executescript(script)
            conn.commit()
            created = True
            print("✔ schema.sql executed — tables created.")
    else:
        # optional: ensure 'progress' table exists too
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='progress';")
        if not cur.fetchone():
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                script = f.read()
                conn.executescript(script)
                conn.commit()
                created = True
                print("✔ progress table created via schema.sql.")

    cur.close()
    conn.close()
    if not created:
        print("✔ DB exists and tables present.")
    else:
        print("✔ ensured DB schema.")


# ------------------ COURSE DATA ------------------

COURSES = {
    "english": {
        "title": "Learn English",
        "levels": {
            "Beginner": [
                {"id": 1, "title": "Basic Greetings", "content": "Hello, Good Morning, Thank You"},
                {"id": 2, "title": "Simple Words", "content": "Food, Water, Friend, Family"},
                {"id": 3, "title": "Daily Phrases", "content": "How are you?, Where are you going?"}
            ],
            "Intermediate": [
                {"id": 4, "title": "Short Conversations", "content": "Talking about family, hobbies"},
                {"id": 5, "title": "Grammar Basics", "content": "Tenses, prepositions"}
            ],
            "Advanced": [
                {"id": 6, "title": "Real-Life Dialogues", "content": "Hotel booking, airport conversation"},
                {"id": 7, "title": "Complex Sentences", "content": "Conditional sentences"}
            ]
        }
    },

    "hindi": {
        "title": "Learn Hindi",
        "levels": {
            "Beginner": [
                {"id": 1, "title": "Basic Greetings", "content": "Namaste, Suprabhat, Shukriya"},
                {"id": 2, "title": "Simple Words", "content": "Pani, Khana, Dost, Parivar"},
                {"id": 3, "title": "Daily Phrases", "content": "Aap kaise ho?, Kahan ja rahe ho?"}
            ],
            "Intermediate": [
                {"id": 4, "title": "Short Conversations", "content": "Parivar, Rozmarra ki baatein"},
                {"id": 5, "title": "Hindi Grammar Basics", "content": "Ling, Vachan, Kaal"}
            ],
            "Advanced": [
                {"id": 6, "title": "Real-Life Dialogues", "content": "Market, Travel"},
                {"id": 7, "title": "Complex Sentences", "content": "Yadi, Agar, Kyunki"}
            ]
        }
    },

    "french": {
        "title": "Learn French",
        "levels": {
            "Beginner": [
                {"id": 1, "title": "Greetings", "content": "Bonjour, Salut, Merci"},
                {"id": 2, "title": "Simple Words", "content": "Eau (water), Ami (friend)"},
                {"id": 3, "title": "Daily Phrases", "content": "Comment ça va? (How are you?)"}
            ],
            "Intermediate": [
                {"id": 4, "title": "Conversations", "content": "Basic dialogues about family"},
                {"id": 5, "title": "Grammar Basics", "content": "Articles, gender rules"}
            ],
            "Advanced": [
                {"id": 6, "title": "Real-Life Dialogues", "content": "Airport, restaurant conversations"},
                {"id": 7, "title": "Complex Sentences", "content": "Expressions + compound sentences"}
            ]
        }
    },

    "spanish": {
        "title": "Learn Spanish",
        "levels": {
            "Beginner": [
                {"id": 1, "title": "Greetings", "content": "Hola, Buenos días, Gracias"},
                {"id": 2, "title": "Simple Words", "content": "Agua (water), Amigo (friend)"},
                {"id": 3, "title": "Daily Phrases", "content": "¿Cómo estás? (How are you?)"}
            ],
            "Intermediate": [
                {"id": 4, "title": "Basic Conversations", "content": "Daily use dialogues"},
                {"id": 5, "title": "Grammar Basics", "content": "Verb conjugations, tenses"}
            ],
            "Advanced": [
                {"id": 6, "title": "Dialogue Practice", "content": "Travel, hotel, food conversations"},
                {"id": 7, "title": "Complex Sentences", "content": "Conditional & future tense"}
            ]
        }
    },

    "german": {
        "title": "Learn German",
        "levels": {
            "Beginner": [
                {"id": 1, "title": "Greetings", "content": "Hallo, Guten Morgen, Danke"},
                {"id": 2, "title": "Simple Words", "content": "Wasser, Freund, Familie"},
                {"id": 3, "title": "Daily Phrases", "content": "Wie geht's? (How are you?)"}
            ],
            "Intermediate": [
                {"id": 4, "title": "Conversations", "content": "Family, work conversations"},
                {"id": 5, "title": "Grammar Basics", "content": "Articles der/die/das, tenses"}
            ],
            "Advanced": [
                {"id": 6, "title": "Real-Life Dialogues", "content": "Train, hotel, shopping"},
                {"id": 7, "title": "Complex Sentences", "content": "Passive, subordinate clauses"}
            ]
        }
    }
}


def get_chapter_by_id(ch_id, lang):
    for level, chapters in COURSES[lang]["levels"].items():
        for ch in chapters:
            if ch["id"] == ch_id:
                return ch
    return None


# ---------------------- ROUTES ----------------------

@app.route("/")
def index():
    return render_template("index.html", courses=COURSES)


@app.route("/select_course", methods=["POST"])
def select_course():
    name = request.form.get("name", "Student")
    lang = request.form.get("language")

    user_id = execute_db(
        "INSERT INTO users (name, selected_language, unlocked_chapter) VALUES (?, ?, ?)",
        (name, lang, 1)
    )

    session["user_id"] = user_id
    session["selected_language"] = lang

    return redirect(url_for("course", lang=lang))


@app.route("/course/<lang>")
def course(lang):
    return render_template("course.html", course=COURSES[lang], lang=lang)


@app.route("/chapters/<lang>")
def chapters(lang):
    user = query_db("SELECT * FROM users WHERE id=?", (session["user_id"],), one=True)
    unlocked = user["unlocked_chapter"]

    chapter_list = []
    for level, chs in COURSES[lang]["levels"].items():
        for c in chs:
            chapter_list.append({**c, "level": level})

    return render_template("chapters.html", chapters=chapter_list, lang=lang, unlocked=unlocked)


@app.route("/chapter/<lang>/<int:ch_id>")
def chapter(lang, ch_id):
    user = query_db("SELECT * FROM users WHERE id=?", (session["user_id"],), one=True)
    unlocked = user["unlocked_chapter"]

    if ch_id > unlocked:
        return render_template("locked.html", message="Chapter Locked")

    chapter = get_chapter_by_id(ch_id, lang)
    return render_template("chapter.html", chapter=chapter, lang=lang)


@app.route("/quiz/<lang>/<int:ch_id>")
def quiz(lang, ch_id):
    chapter = get_chapter_by_id(ch_id, lang)

    questions = [
        {"q": "Write one word from this chapter", "id": "q1"},
        {"q": "Write a phrase from this chapter", "id": "q2"},
        {"q": "Translate 'Hello' in this language", "id": "q3"}
    ]

    return render_template("quiz.html", chapter=chapter, questions=questions, lang=lang)


@app.route("/submit_quiz/<lang>/<int:ch_id>", methods=["POST"])
def submit_quiz(lang, ch_id):
    answers = request.form
    total = len(answers)
    correct = 0

    for a in answers.values():
        if a.strip():
            correct += 1

    score = int((correct / total) * 100)

    execute_db("INSERT INTO progress (user_id, chapter, score) VALUES (?, ?, ?)",
               (session["user_id"], ch_id, score))

    if score >= 60:
        execute_db("UPDATE users SET unlocked_chapter=? WHERE id=?",
                   (ch_id + 1, session["user_id"]))

    return render_template("result.html", score=score, chapter_id=ch_id, lang=lang)


@app.route("/translate_api", methods=["POST"])
def translate_api():
    data = request.json
    text = data["text"]
    target = data["target"]

    r = requests.post(LIBRE_URL, data={
        "q": text,
        "source": "auto",
        "target": target
    })

    try:
        return jsonify({"translated": r.json()["translatedText"]})
    except:
        return jsonify({"translated": ""})


@app.route("/reset")
def reset():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    # ensure DB schema exists before starting
    init_db()
    app.run(debug=True)
