import requests
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


app = Flask(__name__)

db_name = os.getenv('DB_NAME')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('DB_HOST')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{user}:{password}@{host}/{db_name}")
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class QuestionsModel(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quest_text = db.Column(db.String())
    answer_text = db.Column(db.String())
    date = db.Column(db.Date())

    def __init__(self, quest_text, answer_text, date):
        self.quest_text = quest_text
        self.answer_text = answer_text
        self.date = date

    def json(self):
        return ({
            "quest_text": self.quest_text,
            "answer_text": self.answer_text,
            "date": self.date})


@app.route('/questions', methods=['POST', 'GET'])
def handle_questions():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            quantity = data['questions_num']
            for _ in range(quantity):
                res = requests.get(
                    'https://jservice.io/api/random?count=1').json()
                while not (
                    QuestionsModel.query.filter(
                        QuestionsModel.quest_text == res[0]['question'])):
                    res = requests.get(
                        'https://jservice.io/api/random?count=1')
                new_question = QuestionsModel(
                    quest_text=res[0]['question'],
                    answer_text=res[0]['answer'],
                    date=res[0]['created_at'])
                db.session.add(new_question)
                db.session.commit()
            return new_question.json(), 201
        else:
            return {"error": "The request payload is not in JSON format"}
    else:
        questions = QuestionsModel.query.all()
        return {'Questions': list(x.json() for x in questions)}


if __name__ == '__main__':
    app.run(debug=True)