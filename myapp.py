from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import sqlite3

con = sqlite3.connect('test.db')
cur = con.cursor()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

questions = ["Возраст", 
"Гендер", 
"Уровень образования", 
"Какие из этих анекдотов вы слышали?",
"Какие из этих анекдотов вам кажется смешными?",
"Какой ваш любимый анекдот?"]

cur.execute("""
CREATE TABLE if not exists questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    question TEXT
)
""")

for elem in questions:
    cur.execute("INSERT INTO questions (question) VALUES (?)", [elem])
    con.commit()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text)
    education = db.Column(db.Text)
    age = db.Column(db.Integer)


class Answers(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.Text)
    q2 = db.Column(db.Text)
    q3 = db.Column(db.Text)




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions')
def question_page():
    return render_template(
        'quiz.html'
    )



@app.route('/process', methods=['get'])
def answer_process():
    if not request.args:
        return redirect(url_for('question_page'))
    gender = request.args.get('gender')
    education = request.args.get('education')
    age = request.args.get('age')
    user = User(
        age=age,
        gender=gender,
        education=education
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    q1 = ' '.join(request.args.getlist('q1'))
    q2 = ' '.join(request.args.getlist('q2'))
    q3 = request.args.get('q3')
    answer = Answers(id=user.id, q1=q1, q2=q2, q3=q3)
    db.session.add(answer)
    db.session.commit()
    db.session.refresh(answer)
    return 'Ok'

@app.route('/stat')
def stats():
    all_info = {}
    age_stats = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all_info['age_mean'] = round(age_stats[0], 1)
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['total_count'] = User.query.count()
    #all_info['q1_mean'] = db.session.query(func.avg(Answers.q1)).one()[0]
    q1_lists = db.session.query(Answers.q1).all()
    list_of_q1 = []
    freq_di_q1 = {}
    for li in q1_lists:
        splitted_li = str(li)[2:-3].split(', ')
        list_of_q1.extend(splitted_li)
        
        for elem in splitted_li:
            if elem in freq_di_q1:
                freq_di_q1[elem] += 1
            else:
                freq_di_q1[elem] = 1
    sorted_tuple = sorted(freq_di_q1.items(), key=lambda x: x[1])
    sort_freq_di = dict(sorted_tuple)
    return render_template('stat.html', all_info=all_info, sort_freq_di=sort_freq_di)


if __name__ == '__main__':
    db.create_all()
    app.run()