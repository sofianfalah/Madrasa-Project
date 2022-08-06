<h3>Technion Industrial Project 234313</h3>

<b>Students:</b> Sofian Falah, Lena Helo

<b>Website:</b> https://sofianfa3.wixsite.com/madrasaarabicbot

<b>Bot handle on telegram:</b> @MadrasaArabicBot

<b>Organization:</b> <a href="https://madrasafree.com/">Madrasa - Learning to communicate</a>

<b>Project title:</b> Development of a Telegram Bot for practicing spoken Arabic!
 
<b>Project description:</b> Madrasa is a social organization that teaches Arabic for free through 
technology and communal learning. Over 100,000 registered Israeli students are learning to 
communicate via Madrasa’s online courses, social media channels, and study groups throughout 
the country. We also promote the learning and integration of spoken Arabic in leading arenas of 
Israeli society through key strategic collaborations with partners from all sectors through 
designated courses and language.

Today we have four online courses - Arabic for beginners, intermediate level, medical teams, 
and a course for reading and writing in Arabic. All these courses include videos and very simple 
exercises, but we lack more ways to allow our students to practice the Arabic they learn! We 
now wish to develop a Telegram bot, to make the learning process much more effective and 
enjoyable! This will begin with defining the different options and previous bots developed for 
Telegram by other people, then continue developing our bot to fit our learners’ needs! 
The bot will allow our learners to practice Arabic with their own voice using speech-to-text 
features! 

Value for the company: Developing the Telegram Bot will allow our 100,000 (and counting) 
students to practice the speaking skills that they learn from the online courses and thus improve 
immensely the effectiveness and experience of learning.

Value for students: For the students, this will be an opportunity to work with our both 
pedagogical and technological team on developing bots for the growing field of online learning 
and to see its social impact on tens of thousands of learners in Israel. 

Recommended pre-requisite courses:  

• 236369 - Managing Data On The World-wide Web (Recommended)

• 236299 Intro. to Natural Language Processing (Recommended)

• 236817 Seminar in Natural Language Processing (Recommended)

Topography of our project:
1) Telegram Bot: Connecting point between the Flask server and the user. It handles requests from users through the bot and contacts the Flask app using HTTP routes in case an access to the database is needed.

2) Flask Application: Initiates and manages the database using SQL-alchemy, Provides services of GET/POST/DELETE requests to the telegram bot.

3) PostgreSQL Database: Table of users, their IDs and their progress. Table of feedbacks from users. Table of messages to delete, in order to spare the user from the saved voice messages on their phone, that get sent by the bot.
