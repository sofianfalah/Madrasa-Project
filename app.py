
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database

import telegram
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import config
import json
import psycopg2
import os
from enum import Enum

engine = create_engine(config.postgresLink)
if not database_exists(engine.url):
    create_database(engine.url)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = config.postgresLink
db = SQLAlchemy(app)
metadata = MetaData(bind=engine)


global bot

bot = telegram.Bot(token=config.TOKEN)


class course(Enum):
    mathilim = 0
    mamshikhim = 1
    refuit = 2
    talkingWithMadrasa = 3


@app.route('/')
def index():
    return 'Welcome to Madrasa Server!'


@app.route('/receivePollAnswer', methods=['POST'])
def receivePollAnswer():
    # request_data = request.get_json()
    # chat_id = request_data['chat_id']
    # bot_poll_id = request_data['bot_poll_id']
    # selected_option = request_data['option']
    #
    # answer_row = AnswerPerUser.query.filter(
    #     (AnswerPerUser.chat_id == chat_id) & (AnswerPerUser.bot_poll_id == bot_poll_id)).first()
    # answer_row.option = selected_option
    # db.session.commit()
    return "Updated!"


# @app.route('/sendPollToAllUsers', methods=['POST'])
# def sendPollToAllUsers():
#     pollId = request.json.get("poll_id", None)
#     Question = request.json.get("Question", None)
#     option1 = request.json.get("option1", None)
#     option2 = request.json.get("option2", None)
#     option3 = request.json.get("option3", None)
#     option4 = request.json.get("option4", None)
#     options_list = []
#     options_list.extend([option1, option2])
#     if option3:
#         options_list.append(option3)
#     if option4:
#         options_list.append(option4)
#
#     users_ids = User.query.all()
#     json_questions = json.loads(xmlParser())
#
#     try:
#         for row in users_ids:
#             for question in json_questions:
#                 bot.send_poll(row.chat_id, question['question'], question['answers'], is_anonymous=False,
#                                     type="quiz", allows_multiple_answers=False, correct_option_id=question['correct'])
#             resp = bot.send_poll(row.chat_id, Question, options_list, is_anonymous=False, allows_multiple_answers=False,
#                                  type="quiz",correct_option_id=2)
#
#             poll_id_from_bot = resp.poll.id
#             new_poll_to_answer = AnswerPerUser(chat_id=row.chat_id, poll_id=pollId, option=-1,
#                                                bot_poll_id=poll_id_from_bot)
#             db.session.add(new_poll_to_answer)
#             db.session.commit()
#             #bot.send_sticker(chat_id=row.chat_id,mimetypes="webp", sticker="https://mathiasbynens.be/demo/animated-webp")
#
#
#     except Exception as inst:
#         print(type(inst))  # the exception instance
#         print(inst.args)  # arguments stored in .args
#         print(inst)
#     return 'ok'


@app.route("/addpoint", methods=['POST'])
def addpoint():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course
    if course_id == course.mathilim.value:
        file_name = "mathilim.json"
    elif course_id == course.mamshikhim.value:
        file_name = "mamshikhim.json"
    elif course_id == course.refuit.value:
        file_name = "refuit.json"
    elif course_id == course.refuit.value:
        file_name = "refuit.json"

    new_list = user.correct_answers.copy()
    new_list[course_id] += 1
    user.correct_answers = new_list
    db.session.commit()
    return str(user.correct_answers[course_id])



@app.route("/userExists", methods=['POST'])
def userExists():
    arr = User.query.filter_by(chat_id=request.args['chat_id']).all()
    if len(arr) == 0:
        return 'Does Not Exist'
    return 'Exists'

@app.route("/getExerciseIndex", methods=['POST'])
def getExerciseIndex():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course
    exercise_ind = user.exercise_index[course_id]
    return str(exercise_ind)

@app.route("/getCurrentCourse", methods=['POST'])
def getCurrentCourse():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course
    return str(course_id)


@app.route("/getCurrentUnit", methods=['POST'])
def getCurrentUnit():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course
    return str(user.unit_index[course_id])


@app.route("/userNewCourse", methods=['POST'])
def userNewCourse():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = int(request.args['course_id'])
    user.current_course = course_id
    db.session.commit()
    return str(user.unit_index[course_id])

@app.route("/userNextExercise", methods=['POST'])
def userNextExercise():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course
    new_list = user.exercise_index.copy()
    new_list[course_id] += 1
    user.exercise_index = new_list
    db.session.commit()
    return str(user.exercise_index[course_id])

@app.route("/userResetExerciseNum", methods=['POST'])
def userResetExerciseNum():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course
    new_list = user.exercise_index.copy()
    new_list[course_id] = -1
    user.exercise_index = new_list
    db.session.commit()
    return str(user.exercise_index[course_id])

@app.route("/userNextUnit", methods=['POST'])
def userNextUnit():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course
    new_list = user.unit_index.copy()
    new_list[course_id] += 1
    user.unit_index = new_list
    db.session.commit()
    return str(user.unit_index[course_id])


@app.route("/updateCorrectAnswers", methods=['POST'])
def updateCorrectAnswers():
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    course_id = user.current_course

    answers_list = user.total_answers.copy()
    print("total answers: ",answers_list[course_id])
    answers_list[course_id] += 1
    user.total_answers = answers_list
    db.session.commit()
    if course_id != course.talkingWithMadrasa.value:
        if course_id == course.mathilim.value:
            file_name = "mathilim.json"
        elif course_id == course.mamshikhim.value:
            file_name = "mamshikhim.json"
        elif course_id == course.refuit.value:
            file_name = "refuit.json"
        file_path = os.path.join(os.getcwd(), file_name)
        f = open(file_path, encoding="utf8")
        data = json.load(f)
        print("course_id",course_id)

        correct_ans = data[user.unit_index[course_id]]["exercises"][user.exercise_index[course_id]-1]["correct"][0]
        f.close()
        print("int(correct_ans): ", int(correct_ans))
        print("int(request.args['selected_option']:", int(request.args['selected_option']))

        if int(correct_ans) != int(request.args['selected_option']):
            return "wrong answer"
    if (course_id == course.talkingWithMadrasa.value and int(request.args['selected_option'])==1) or (course_id != course.talkingWithMadrasa.value):
        new_list = user.correct_answers.copy()
        new_list[course_id] += 1
        user.correct_answers = new_list
        db.session.commit()
        return 'right answer'
    return "wrong answer"

@app.route("/users", methods=['POST'])
def registerUser():
    try:
        correct_ans_list = [0]*4
        total_ans_list = [0]*4
        unit_index_list = [0]*4
        exercise_ind = [-1]*3
        new_user = User(chat_id=request.args['chat_id'],
                        username=request.args['username'], current_course = 0,
                        correct_answers = correct_ans_list,
                        total_answers = total_ans_list,
                        unit_index = unit_index_list,
                        exercise_index = exercise_ind)

        db.session.add(new_user)
        db.session.commit()
        return 'You were successfully added'
    except exc.IntegrityError:
        db.session.rollback()
        return 'You already exist'


@app.route("/users", methods=['DELETE'])
def deleteUser():
    arr = User.query.filter_by(chat_id=request.args['chat_id']).all()
    if len(arr) == 0:
        return 'already removed!'
    user = User.query.filter_by(chat_id=request.args['chat_id']).first()
    db.session.delete(user)
    db.session.commit()
    return 'You were successfully removed from our system.'


class User(db.Model):
    __tablename__ = 'users'
    chat_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    current_course = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.ARRAY(db.Integer), nullable=False)
    total_answers = db.Column(db.ARRAY(db.Integer), nullable=False)
    unit_index = db.Column(db.ARRAY(db.Integer), nullable=False)
    exercise_index = db.Column(db.ARRAY(db.Integer), nullable=False)




# db.drop_all()
# db.session.commit()
db.create_all()
db.session.commit()



if __name__ == '__main__':
    app.run()