import speech_recognition
import telegram
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram.ext import PollAnswerHandler, Updater, CommandHandler, CallbackQueryHandler, CallbackContext, \
    MessageHandler, Filters

import logging
import requests
import speech_recognition as sr
import config
from os import path
from pydub import AudioSegment
import subprocess
import json
from Levenshtein import distance as lev
import os
import time
import threading
from enum import Enum

global bot

bot = telegram.Bot(token=config.TOKEN)

updater = Updater("5317871500:AAGDEX_gtZtw9lBVPK0tgbgQ7i9UtZg_f6U", use_context=True)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


class course(Enum):
    mathilim = 0
    mamshikhim = 1
    refuit = 2
    talkingWithMadrasa = 3


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    r = requests.delete('http://127.0.0.1:5000/DeleteAudioMessages',
                        params={'chat_id': update.message.chat_id})
    r = requests.post('http://127.0.0.1:5000/userExists',
                      params={'chat_id': update.message.chat_id})
    if r.text == 'Does Not Exist':
        user = update.effective_user
        update.message.reply_markdown_v2(
            fr' \! {user.mention_markdown_v2()} ' + 'מרחבא ')

        reply_keyboard = [['/register', '/remove', '/start']]
        rep = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            fr'כיף שהגעת לכיתה! ' + '\n' +
            fr'נא לבחור באחת מהאפשרויות הבאות: ' + '\n\n' +
            fr'Register - ' + 'להרשמה כמשתמש במערכת' + '\n\n' +
            fr'Remove - ' + 'לבטל את ההרשמה' + '\n\n' +
            fr'Start - ' + 'לראות את ההודעה הזו שוב' + '\n', reply_markup=rep)
    else:
        user = update.effective_user
        update.message.reply_markdown_v2(
            fr' \! {user.mention_markdown_v2()} ' + 'מרחבא ')

        reply_keyboard = [['/exercises', '/remove', '/start']]
        rep = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            fr'כיף שהגעת לכיתה! ' + '\n' +
            fr'נא לבחור באחת מהאפשרויות הבאות: ' + '\n\n' +
            fr'Exercises - ' + 'המשיכו ללמוד' + '\n\n' +
            fr'Remove - ' + 'לבטל את ההרשמה' + '\n\n' +
            fr'Start - ' + 'לראות את ההודעה הזו שוב' + '\n', reply_markup=rep)


def register_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    username = update.message.from_user['first_name']
    r = requests.post('http://127.0.0.1:5000/users',
                      params={'chat_id': update.message.chat_id, 'username': username})
    reply_keyboard = [['/exercises', '/remove']]
    rep = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    if r.text == 'You already exist':
        update.message.reply_text(
            fr'כבר נמצא במערכת' + '\n\n' +
            fr'Exercises - ' + 'המשיכו ללמוד' + '\n\n' +
            fr'Remove - ' + 'לבטל את ההרשמה' + '\n\n', reply_markup=rep)
    else:
        update.message.reply_text(
            fr'ההרשמה הסתיימה בהצלחה' + '\n\n' +
            fr'Exercises - ' + 'התחילו ללמוד' + '\n\n' +
            fr'Remove - ' + 'לבטל את ההרשמה' + '\n\n', reply_markup=rep)


def remove_command(update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    r = requests.delete('http://127.0.0.1:5000/users', params={'chat_id': update.message.chat_id})
    if r.text == 'already removed!':
        reply_keyboard = [['/register']]
        rep = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text(fr'אינך רשום במערכת' + '\n', reply_markup=rep)
    else:
        # update.message.reply_text('מתבאסים מהעזיבה שלך! '+'\n'+'חשבונך נמחק בהצלחה')

        keyboard = [
            [
                InlineKeyboardButton("feedback",
                                     switch_inline_query_current_chat="/feedback " + "\n\n"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='מתבאסים מהעזיבה שלך! ' + '\n' + 'חשבונך נמחק בהצלחה',
                                 reply_markup=reply_markup)
        reply_keyboard = [['/register']]
        rep = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text("נשמח לקבל פידבק", reply_markup=rep)
        # context.bot.send_message(chat_id=update.message.chat_id,
        #                          text="נשמח לקבל ממך פידבק",
        #                          reply_markup=telegram.ForceReply(True))


def exercises(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    r = requests.post('http://127.0.0.1:5000/userExists',
                      params={'chat_id': update.message.chat_id})
    if r.text == 'Does Not Exist':
        update.message.reply_markdown_v2(
            fr'/register' + '\n' + 'צריך להירשם במערכת כדי להתחיל' + '\n')
    else:
        keyboard = [
            [
                InlineKeyboardButton("ערבית מדוברת מתחילים", callback_data="mathilim"),
            ],
            [
                InlineKeyboardButton("ערבית מדוברת ממשיכים", callback_data="mamshikhim"),
            ],
            [
                InlineKeyboardButton("ערבית מדוברת לצוותים רפואיים", callback_data="refuit"),
            ],
            [
                InlineKeyboardButton("מדברים עם מדרסה", callback_data="talkingWithMadrasa"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('הקורסים של מדרסה:', reply_markup=reply_markup)


def next_exercise(update: Update, context: CallbackContext) -> None:
    requests.delete('http://127.0.0.1:5000/DeleteAudioMessages',
                    params={'chat_id': update.message.chat_id})

    r = requests.post('http://127.0.0.1:5000/getCurrentUnit',
                      params={'chat_id': update.message.chat_id})
    curr_unit = int(r.text)
    r = requests.post('http://127.0.0.1:5000/getCurrentCourse',
                      params={'chat_id': update.message.chat_id})
    curr_course = int(r.text)
    if curr_course == course.talkingWithMadrasa.value:
        handlingAudioSegment(update.message.chat_id, curr_unit)
    else:
        handlingSegments(update.message.chat_id, curr_unit, curr_course)

    # TODO: check course_id + handlingSegments()


def next_unit(update: Update, context: CallbackContext) -> None:
    r = requests.delete('http://127.0.0.1:5000/DeleteAudioMessages',
                    params={'chat_id': update.message.chat_id})
    print(r.text)
    r = requests.post('http://127.0.0.1:5000/getCurrentUnit',
                      params={'chat_id': update.message.chat_id})
    curr_unit = int(r.text)
    r = requests.post('http://127.0.0.1:5000/getCurrentCourse',
                      params={'chat_id': update.message.chat_id})
    curr_course = int(r.text)
    handlingSegments(update.message.chat_id, curr_unit, curr_course)


def get_feedback(update: Update, context: CallbackContext) -> None:
    # TODO: Add feedback table
    update.message.reply_text('קיבלנו את המשוב, תודה רבה!', reply_markup=ReplyKeyboardRemove())
    bot.sendSticker(chat_id=update.message.chat_id,
                    sticker="https://raw.githubusercontent.com/LenaHelo/stickers/main/nhrk_s3d.webp")


def otherMessages(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    reply_keyboard = [['/start']]
    rep = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text('לא הבנתי מה ששלחת ', reply_markup=rep)


def deleteMessageByThread(chat_id, message_id):
    time.sleep(50)
    bot.deleteMessage(chat_id, message_id)


def messageToDelete(chat_id, message_id):
    response = requests.post('http://127.0.0.1:5000/addMessageToDelete',
                  params={'chat_id': chat_id, 'message_id': message_id})
    print(response.text)

def handlingAudioSegment(chat_id, counter):
    file_path = os.path.join(os.getcwd(), "jsonFiles/vocab.json")
    f = open(file_path, encoding="utf8")
    data = json.load(f)
    text1 = data[counter]["arabic"] + " " + "[" + data[counter]["part_of_speech"] + "]"
    text2 = "משמעות " + data[counter]["arabic"] + " בעברית: " + data[counter]["hebrew"]
    text3 = "נא לשלוח הקלטה של הביטוי: " + data[counter]["arabic"]
    text = text1 + '\n' + text2 + '\n' + text3
    mes = bot.sendAudio(chat_id=chat_id, audio=data[counter]["audio"], caption=text)
    messageToDelete(chat_id, mes.message_id)
    print("message added to db, message_id = ", mes.message_id)
    # t1 = threading.Thread(target=deleteMessageByThread, args=(chat_id, mes.message_id,))
    # t1.start()
    f.close()


def handlingSegments(chat_id, array_index, course_id):
    r = requests.post('http://127.0.0.1:5000/getExerciseIndex',
                      params={'chat_id': chat_id})
    exercise_index = int(r.text)
    file_name = ""
    if course_id == course.mathilim.value:
        file_name = "jsonFiles/mathilim.json"
    elif course_id == course.mamshikhim.value:
        file_name = "jsonFiles/mamshikhim.json"
    elif course_id == course.refuit.value:
        file_name = "jsonFiles/refuit.json"
    file_path = os.path.join(os.getcwd(), file_name)
    f = open(file_path, encoding="utf8")
    data = json.load(f)
    # TODO: a5r json blmlf
    if exercise_index == -1:
        text1 = "שיעור מספר " + str(data[array_index]["Lesson"]) + ", יחידה מספר " + str(
            data[array_index]["unit"]) + "\n";
        text2 = data[array_index]["Title"] + "\n"
        bot.sendMessage(chat_id, text1 + text2)
        if data[array_index]["videoURL"] != "":
            bot.sendMessage(chat_id, data[array_index]["videoURL"])
            # bot.sendVideo(chat_id, data[array_index]["videoURL"])
        if len(data[array_index]["exercises"]) == 0:
            requests.post('http://127.0.0.1:5000/userNextUnit',
                          params={'chat_id': chat_id})
            reply_keyboard = [['/nextUnit', '/start']]
            repp = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id, 'nextUnit - ' + 'המשך' + '\n', reply_markup=repp)
        else:
            requests.post('http://127.0.0.1:5000/userNextExercise',
                          params={'chat_id': chat_id})
            reply_keyboard = [['/startExercising', '/start']]
            repp = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id, 'startExercising - ' + 'התחל' + '\n', reply_markup=repp)
            bot.sendSticker(chat_id=chat_id,
                            sticker="https://raw.githubusercontent.com/LenaHelo/stickers/main/bnjh.webp")


    else:
        problem_dict = data[array_index]["exercises"][exercise_index]
        if len(problem_dict["correct"]) == 1:
            if "title" in problem_dict:
                bot.sendMessage(chat_id, problem_dict["title"])
            if "audio" in problem_dict:
                mes = bot.sendAudio(chat_id, problem_dict["audio"])
                messageToDelete(chat_id, mes.message_id)
                # t1 = threading.Thread(target=deleteMessageByThread, args=(chat_id, mes.message_id,))
                # t1.start()
            bot.send_poll(chat_id, problem_dict['text'], problem_dict['answers'], is_anonymous=False,
                          type="quiz", allows_multiple_answers=False, correct_option_id=problem_dict["correct"][0])
        else:
            print("telegram lo tome5")

        if exercise_index == len(data[array_index]["exercises"]) - 1:
            requests.post('http://127.0.0.1:5000/userNextUnit',
                          params={'chat_id': chat_id})
            requests.post('http://127.0.0.1:5000/userResetExerciseNum',
                          params={'chat_id': chat_id})
            reply_keyboard = [['/nextUnit', '/start']]
            repp = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id, 'nextUnit - ' + 'המשך' + '\n', reply_markup=repp)

        else:
            requests.post('http://127.0.0.1:5000/userNextExercise',
                          params={'chat_id': chat_id})
            reply_keyboard = [['/nextExercise', '/start']]
            repp = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id, 'nextExercise - ' + 'המשך' + '\n', reply_markup=repp)

    f.close()


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    chat_id = query.from_user.id
    # CallbackQueries need to be answered, even if no notification to the user is needed
    if query.data == "talkingWithMadrasa":
        r = requests.post('http://127.0.0.1:5000/userNewCourse',
                          params={'chat_id': chat_id, 'course_id': course.talkingWithMadrasa.value})
        handlingAudioSegment(chat_id, int(r.text))
        query.answer('תשובתך נשמרה')
        query.edit_message_text("בקורס הזה תקבלו מילים בערבית ותתרגלו את ההגיה דרך שליחת הקלטות לבוט")
    elif query.data == "mathilim":
        r = requests.post('http://127.0.0.1:5000/userNewCourse',
                          params={'chat_id': query.from_user.id, 'course_id': course.mathilim.value})
        handlingSegments(chat_id, int(r.text), course.mathilim.value)
        query.answer('תשובתך נשמרה')
        query.delete_message()
    elif query.data == "mamshikhim":
        r = requests.post('http://127.0.0.1:5000/userNewCourse',
                          params={'chat_id': query.from_user.id, 'course_id': course.mamshikhim.value})
        handlingSegments(chat_id, int(r.text), course.mamshikhim.value)
        query.answer('תשובתך נשמרה')
        query.delete_message()
    elif query.data == "refuit":
        r = requests.post('http://127.0.0.1:5000/userNewCourse',
                          params={'chat_id': query.from_user.id, 'course_id': course.refuit.value})
        handlingSegments(chat_id, int(r.text), course.refuit.value)
        query.answer('תשובתך נשמרה')
        query.delete_message()


def voice_handler(update, context):
    try:
        bot = context.bot
        file = bot.getFile(update.message.voice.file_id)

        file.download('voice.mp3')
        filename = "voice.wav"
        dst = "voice.wav"
        # convert mp3 to wav file
        subprocess.call(['ffmpeg', '-i', 'voice.mp3',
                         'voice.wav', '-y'])

        # initialize the recognizer
        r = sr.Recognizer()
        # open the file
        with sr.AudioFile(filename) as source:
            # listen for the data (load audio to memory)
            audio_data = r.record(source)
            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data, language='ar-AR')
            text1 = "הביטוי שאמרת: " + text

            r = requests.post('http://127.0.0.1:5000/getCurrentUnit',
                              params={'chat_id': update.message.chat_id})

            file_path = os.path.join(os.getcwd(), "jsonFiles/vocab.json")
            with open(file_path, encoding="utf8") as f:
                data = json.load(f)
                text2 = data[int(r.text)]["arabic_stt"]
            levDis = lev(text, text2)
            max_len = max(len(text), len(text2))
            percentage = ((max_len - levDis) / max_len) * 100
            ret_text = str("{:.2f}".format(percentage)) + "%"
            reply_text = "הביטוי שאמרת נכון באחוז: " + ret_text
            if percentage < 100:
                reply_text = "הביטוי הנכון: " + text2 + "\n\n" + reply_text
                # bot.sendSticker(chat_id=update.message.chat_id,
                #                 sticker="https://raw.githubusercontent.com/TelegramBots/book/master/src/docs/sticker-fred.webp")
                context.bot.sendSticker(chat_id=update.message.chat_id,
                                        sticker="https://raw.githubusercontent.com/LenaHelo/stickers/main/bsita.webp")
                requests.post('http://127.0.0.1:5000/updateCorrectAnswers',
                              params={'chat_id': update.message.chat_id, 'selected_option': 0})
            else:
                context.bot.sendSticker(chat_id=update.message.chat_id,
                                        sticker="https://raw.githubusercontent.com/LenaHelo/stickers/main/bzbt.webp")

                requests.post('http://127.0.0.1:5000/updateCorrectAnswers',
                              params={'chat_id': update.message.chat_id, 'selected_option': 1})
            requests.post('http://127.0.0.1:5000/userNextUnit',
                          params={'chat_id': update.message.chat_id})
            text1 = text1 + "\n\n" + reply_text

            bot.sendMessage(update.message.chat_id, text1, reply_to_message_id=update.message.message_id)

            reply_keyboard = [['/nextExercise', '/start']]
            repp = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(
                fr'nextExercise - ' + 'לתרגיל הבא' + '\n', reply_markup=repp)
    except speech_recognition.UnknownValueError as e:
        update.message.reply_text("הקול לא ברור.. נא להקליט שוב")


def rec_poll_answer(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    answer = update.poll_answer

    r = requests.post('http://127.0.0.1:5000/updateCorrectAnswers',
                      params={'chat_id': answer.user.id, 'selected_option': answer.option_ids[0]})
    print(r.text)
    # url = 'http://localhost:5000/receivePollAnswer'
    # myobj = {'chat_id': answer.user.id,
    #          'bot_poll_id': answer.poll_id,
    #          'option': answer.option_ids[0]
    #          }
    #
    # requests.post(url, json=myobj)
    if r.text == 'right answer':
        context.bot.sendSticker(chat_id=answer.user.id,
                                sticker="https://raw.githubusercontent.com/LenaHelo/stickers/main/y3ni_3lk.webp")


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("register", register_command))
    updater.dispatcher.add_handler(CommandHandler("remove", remove_command))
    updater.dispatcher.add_handler(CommandHandler("exercises", exercises))
    updater.dispatcher.add_handler(CommandHandler("nextExercise", next_exercise))
    updater.dispatcher.add_handler(CommandHandler("nextUnit", next_unit))
    updater.dispatcher.add_handler(CommandHandler("startExercising", next_unit))
    updater.dispatcher.add_handler(CommandHandler("feedback", get_feedback))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(PollAnswerHandler(rec_poll_answer))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('@MadrasaArabicBot /feedback'), get_feedback))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, otherMessages))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
