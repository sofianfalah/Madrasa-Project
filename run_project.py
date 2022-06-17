import subprocess
import threading

cmdFlask = 'python ./app.py'
cmdBot = 'python ./telegramBot.py'


def runFlask():
   subprocess.check_call(cmdFlask, shell=True)


def runBot():
   subprocess.check_call(cmdBot, shell=True)


t1 = threading.Thread(target=runFlask)
t1.start()

t2 = threading.Thread(target=runBot)
t2.start()