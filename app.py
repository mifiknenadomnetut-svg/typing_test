import sqlite3
from flask import Flask, render_template, request, jsonify
import random, time, uuid

app = Flask(__name__)
DATABASE = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with app.app_context():
        db = get_db_connection()
        db.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                wpm INTEGER NOT NULL,
                accuracy INTEGER NOT NULL,
                time_sec REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                text TEXT
            )
        ''')
        db.commit()
        db.close()


def get_user_id_from_cookie(request):
    return request.cookies.get('user_id') or str(uuid.uuid4())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test_page():
    return render_template('index.html')


@app.route('/start_test')
def start_test():
    level = request.args.get('level', 'easy')

    TEXTS = {
        'easy': ["Съешь ещё этих мягких французских булок да выпей же чаю.", "Мама мыла раму, а я смотрел в окно на падающий снег.",
                 "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!", "На дворе трава, на траве дрова.",
                 "Тридцать три корабля лавировали-лавировали, да не вылавировали.",
                 "Бык тупогуб, тупогубенький бычок, у быка бела губа была тупа"],
        'medium': ["Сверхзвуковой истребитель-перехватчик промчался в небе.",
                   "Революция требует отваги и самоотверженности.",
                   "Синхрофазотрон ускорил протоны до субсветовой скорости.",
                   "Трансцендентальная эстетика Канта определяет априорные формы чувственности."
                   "Экзистенциальная дилемма квази-унитарной матрицы не имеет тривиального решения."
                   "Согласно последним данным, проект будет запущен в следующем квартале, если команда разработчиков успеет исправить все критические ошибки"],
        'hard': ["The quick brown fox jumps over the lazy dog.",
                 "Pack my box with five dozen liquor jugs.",
                 "She sells seashells by the seashore.",
                 "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
                 "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",

                 ]
    }
    # Выбираем СЛУЧАЙНЫЙ текст из массива для выбранного уровня
    text = random.choice(TEXTS.get(level, TEXTS['easy']))
    return jsonify({'text': text})


@app.route('/submit_result', methods=['POST'])
def submit_result():
    data = request.json
    user_id = get_user_id_from_cookie(request)

    db = get_db_connection()
    db.execute('''
        INSERT INTO results (user_id, wpm, accuracy, time_sec, text)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, data['wpm'], data['accuracy'], data['time'], data['text']))
    db.commit()
    db.close()

    response = jsonify({'status': 'ok'})
    response.set_cookie('user_id', user_id)
    return response


@app.route('/history')
def history():
    user_id = get_user_id_from_cookie(request)

    db = get_db_connection()
    # ИЗМЕНЕНИЕ: Добавлен .limit(15) для получения только последних 15 записей
    results = db.execute('SELECT * FROM results WHERE user_id = ? ORDER BY timestamp DESC LIMIT 15',
                         (user_id,)).fetchall()
    db.close()

    return render_template('history.html', history=results)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)