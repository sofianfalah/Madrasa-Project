import os
import xml.etree.ElementTree as ET
import json

# helper code for converting Madrasa Xml data file to Json

gb_curr_dir = ""
gb_path = ""


def getVerNum(xml_file):
    current_dir = "sequential"
    path = os.path.join(gb_path, current_dir)
    units_number = 0
    if xml_file in os.listdir(path):
        xml_file = os.path.join(path, xml_file)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for vertical in root.iter('vertical'):
            units_number += 1
    return units_number


def getNumberOfUnits(chapter_xml_file):
    current_dir = "chapter"
    units_number = 0
    path = os.path.join(gb_path, current_dir)
    if chapter_xml_file in os.listdir(path):
        xml_file = os.path.join(path, chapter_xml_file)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for seq in root.iter('sequential'):
            units_number = getVerNum(seq.attrib['url_name'] + ".xml")
    return units_number


def xmlParser(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    questions_list = []
    question_text = ''
    question_dict = {}
    correct_answer = []
    prev = ''
    answers_index = 0
    flag = True
    for elem in root.iter():
        if elem.tag == 'problem' and flag:
            display_title = elem.attrib['display_name']
            question_dict['title'] = display_title
            flag = False
        if elem.tag != 'choice' and elem.tag != 'option':
            if prev == 'choice' or prev == 'option':
                question_dict['answers'] = answers_list
                question_dict['correct'] = correct_answer
                questions_list.append(question_dict)
                question_dict = {}
                prev = ''

        if elem.tag == 'p' or elem.tag == 'label':
            if elem.text is not None:
                question_text += elem.text
                question_text += " \n "

        if elem.tag == "source":
            question_dict['audio'] = elem.attrib['src']

        if elem.tag == 'choicegroup' or elem.tag == 'optioninput' or elem.tag == 'checkboxgroup':
            question_dict['text'] = question_text
            question_text = ''
            answers_list = []
            correct_answer = []
            answers_index = 0
        if elem.tag == 'choice' or elem.tag == 'option':
            answers_list.append(elem.text)
            if elem.attrib['correct'].lower() == 'true':
                correct_answer.append(answers_index)
            answers_index += 1
        prev = elem.tag

    question_dict['answers'] = answers_list
    question_dict['correct'] = correct_answer
    questions_list.append(question_dict)

    # json_file = json.dumps(questions_list, indent=2)

    # print(json.loads(final))
    return questions_list


def XMLParseProblems(prob_xml_file, problem_counter):
    current_dir = "problem"
    path = os.path.join(gb_path, current_dir)
    xml_file = os.path.join(path, prob_xml_file)

    print("problem", problem_counter, ":", xml_file)
    json_questions = xmlParser(xml_file)
    return json_questions
    # json_questions = json.loads(json_questions)
    # print(json_questions)


def XMLParseVideo(video_xml_file):
    current_dir = "video"
    path = os.path.join(gb_path, current_dir)
    if video_xml_file in os.listdir(path):
        xml_file = os.path.join(path, video_xml_file)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for video in root.iter("video"):
            return "https://youtu.be/" + video.attrib['youtube_id_1_0']


def getProblemName(ver_xml_file, lessonNum, unitNum, id_ref, course):
    if lessonNum == 8 and unitNum > 7 and course == "ערבית מדוברת - מתחילים":
        return None
    unit_dict = {}
    all_problems_list = []
    current_dir = "vertical"
    problem_counter = 0
    video_URL = ""
    path = os.path.join(gb_path, current_dir)
    if ver_xml_file in os.listdir(path):
        xml_file = os.path.join(path, ver_xml_file)
        print("path: ", xml_file)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        if len(root.findall("problem")) == 0 and len(root.findall("video")) == 0:
            return None
        for vertical in root.iter("vertical"):
            Title = vertical.attrib['display_name']

        if len(root.findall("video")) != 0:
            for video in root.iter("video"):
                video_URL = XMLParseVideo(video.attrib['url_name'] + ".xml")
                break
        for problem in root.iter('problem'):
            problem_counter += 1
            # here we get problem attribute (url_name)
            # print(vertical.attrib['url_name'])
            # now we should find it in problem directory
            pr_list = XMLParseProblems(problem.attrib['url_name'] + ".xml", problem_counter)
            all_problems_list.extend(pr_list)
        unit_dict["id"] = id_ref[0]
        unit_dict["course"] = course
        unit_dict["Lesson"] = lessonNum
        unit_dict["unit"] = unitNum
        unit_dict["Title"] = Title
        unit_dict["videoURL"] = video_URL
        unit_dict["exercises"] = all_problems_list

        return unit_dict
    return None


def getVerticalName(seq_xml_file, lessonNum, id_ref, course):
    current_dir = "sequential"
    path = os.path.join(gb_path, current_dir)
    unit_number = 1
    all_units_in_lesson_list = []
    if seq_xml_file in os.listdir(path):
        xml_file = os.path.join(path, seq_xml_file)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for vertical in root.iter('vertical'):
            # here we get vertical attribute (url_name)
            # print(vertical.attrib['url_name'])
            # now we should find it in vertical directory
            unit_dict = getProblemName(vertical.attrib['url_name'] + ".xml", lessonNum, unit_number, id_ref, course)
            if unit_dict is not None:
                id_ref[0] += 1
                unit_number += 1
                all_units_in_lesson_list.append(unit_dict)

    return all_units_in_lesson_list


def getSequentialName(chapter_xml_file, lessonNum, id_ref, course):
    current_dir = "chapter"
    path = os.path.join(gb_path, current_dir)
    all_sequential_list = []
    if chapter_xml_file in os.listdir(path):
        xml_file = os.path.join(path, chapter_xml_file)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for seq in root.iter('sequential'):
            # here we get sequential attribute (url_name)
            # print(seq.attrib['url_name'])
            # now we should find it in sequential directory
            res = getVerticalName(seq.attrib['url_name'] + ".xml", lessonNum, id_ref, course)
            if course == "ערבית מדוברת לצוותים רפואיים":
                all_sequential_list.extend(res)
                lessonNum += 0.1
            else:
                return res
    if course == "ערבית מדוברת לצוותים רפואיים":
        return all_sequential_list
    return None


def getChapterName(id_ref, course):
    current_dir = "course"
    path = os.path.join(gb_path, current_dir)
    lesson_number = -1
    all_lessons_in_chapter = []
    for filename in os.listdir(path):
        xml_file = os.path.join(path, filename)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for chapter in root.iter('chapter'):
            lesson_number += 1
            if course == "הכתב הערבי" and lesson_number > 3:
                continue
            # here we get chapter attribute (url_name)
            # print(chapter.attrib['url_name'])
            # now we should find it in chapter directory
            res = getSequentialName(chapter.attrib['url_name'] + ".xml", lesson_number, id_ref, course)
            if res is not None:
                all_lessons_in_chapter.extend(res)
    with open("problems.json", "w", encoding='utf8') as jsonFile:
        json.dump(all_lessons_in_chapter, jsonFile, ensure_ascii=False, indent=2)


if __name__ == '__main__':

    course_name = ""
    id_ref = [1]
    print("to parse mathilim course write: 1")
    print("to parse mamshikhim course write: 2")
    print("to parse refuit course write: 3")
    print("to parse ktavaravi course write: 4")
    course_number = int(input("Enter a number: "))
    if course_number == 1:
        course_name = "ערבית מדוברת - מתחילים"
        gb_curr_dir = "course1"
        gb_path = os.path.join(os.getcwd(), gb_curr_dir)
        getChapterName(id_ref, course_name)
    elif course_number == 2:
        course_name = "ערבית מדוברת - ממשיכים"
        gb_curr_dir = "course2"
        gb_path = os.path.join(os.getcwd(), gb_curr_dir)
        getChapterName(id_ref, course_name)
    elif course_number == 3:
        course_name = "ערבית מדוברת לצוותים רפואיים"
        gb_curr_dir = "course3"
        gb_path = os.path.join(os.getcwd(), gb_curr_dir)
        getChapterName(id_ref, course_name)
    elif course_number == 4:
        course_name = "הכתב הערבי"
        gb_curr_dir = "course4"
        gb_path = os.path.join(os.getcwd(), gb_curr_dir)
        getChapterName(id_ref, course_name)

    # with open("problems.json", encoding="utf8") as f:
    #     data = json.load(f)
    #     print(data["exercises"][13]["text"])
