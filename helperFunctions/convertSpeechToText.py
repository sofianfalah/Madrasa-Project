
import json
import subprocess
import speech_recognition as sr

# helper code for converting audio to text and updating json file

if __name__ == '__main__':
    print("converting audio to text and updating json file: ")
    with open("../jsonFiles/vocab.json", encoding="utf8") as f:
        data = json.load(f)
        list_len = len(data)
        counter = 0
        for dict_audio in data:
            print("**speechToText** files number to convert: ", list_len-counter)
            print("now converting file id: ", dict_audio["id"])
            counter += 1
            try:
                audio_file = dict_audio["audio"]
                filename = "../voice.wav"
                subprocess.call(['ffmpeg', '-i', audio_file,
                                 filename, '-y'])
                # initialize the recognizer
                r = sr.Recognizer()
                # open the file
                with sr.AudioFile(filename) as source:
                    # listen for the data (load audio to memory)
                    audio_data = r.record(source)
                    # recognize (convert from speech to text)
                    text = r.recognize_google(audio_data, language='ar-AR')
                    dict_audio["arabic_text"] = text
            except sr.UnknownValueError as e:
                dict_audio["arabic_text"] = "UnknownValueError"

    with open("../jsonFiles/vocab.json", "w", encoding='utf8') as jsonFile:
        json.dump(data, jsonFile, ensure_ascii=False, indent=2)

