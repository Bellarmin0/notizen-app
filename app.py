from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Anlegen eines absoluten Pfads zur Datenbank
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_NAME = os.path.join(BASE_DIR, "notes.db")

# Erstellt Datenbank, falls sie noch nicht existiert
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                text TEXT NOT NULL
            )
        ''')
        conn.commit()  
init_db()


# Erstellung der Liste mit Notizen auf Startseite, dazu Abruf der Daten aus DB
@app.route('/')            
def index():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, text FROM notes ORDER BY id DESC")
        notes = [{"id": row[0], "title": row[1], "text": row[2]} for row in cursor.fetchall()]
    return render_template("index.html", notizen=notes)

# Erstellung einer neuen Notiz
@app.route('/notiz', methods=['GET', 'POST'])
def notiz_hinzufuegen():
    if request.method == 'POST':
        title = request.form.get('note_title')
        text = request.form.get('note_text')
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (title, text) VALUES (?, ?)", (title, text))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('notiz.html')

# Löschen einer Notiz
@app.route('/bearbeiten/<int:note_id>', methods=['GET', 'POST'])
def notiz_bearbeiten(note_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Bei POST-Request: Lesen der Formularfelder, Updaten der Notizen
        if request.method == "POST":
            title = request.form["note_title"]
            text = request.form["note_text"]
            cursor.execute("UPDATE notes SET title=?, text=? WHERE id=?", (title, text, note_id))
            conn.commit()
            return redirect(url_for("index"))

        # GET-Request: Laden der ausgewählten Notiz aus der DB 
        cursor.execute("SELECT id, title, text FROM notes WHERE id=?", (note_id,))
        row = cursor.fetchone()
        if row:
            note = {"id": row[0], "title": row[1], "text": row[2]}
        else:
            note = None
    return render_template("notiz_bearbeiten.html", note=note)

@app.route('/loeschen/<int:note_id>', methods=['POST'])
def notiz_loeschen(note_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
