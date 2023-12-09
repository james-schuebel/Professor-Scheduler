import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from ortools.linear_solver import pywraplp
import mysql.connector
from mysql.connector import errorcode


config = {
  'host':'professor-scheduler-db.mysql.database.azure.com',
  'user':'db',
  'password':'UTDallas1',
  'database':'professorschema',
  'client_flags': [mysql.connector.ClientFlag.SSL],
  'ssl_ca': 'DigiCertGlobalRootG2.crt.pem'
}

app = Flask(__name__)
CORS(app)

def time_to_minutes(t):
        h, m = map(int, t.split(':'))
        return h * 60 + m

# Test
preferences = {
    'bmen1100.103.22f': 'high',
    'bmen1100.104.22f': 'medium',
    'bmen1100.105.22f': 'low',
    'bmen1100.106.22f': 'none'
}
 # Sample data
courses= [
        {
            "section_address": "bmen1100.101.22f",
            "course_prefix": "bmen",
            "course_number": "1100",
            "section": "101 ",
            "class_number": "85327",
            "title": "Introduction to Bioengineering I ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "19",
            "enrolled_max": "19",
            "instructors": "Kathleen Myers",
            "assistants": "Bahareh Kian Pour, Kavya Balaji",
            "term": "22f",
            "session": "1",
            "days": "Monday",
            "times": "13:00 - 14:40",
            "times_12h": "1:00pm - 2:40pm",
            "location": "ML1_1.118",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124625",
            "textbooks": ""
        },
        {
            "section_address": "bmen1100.102.22f",
            "course_prefix": "bmen",
            "course_number": "1100",
            "section": "102 ",
            "class_number": "85332",
            "title": "Introduction to Bioengineering I ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "19",
            "enrolled_max": "19",
            "instructors": "Benjamin Porter",
            "assistants": "Kavya Balaji",
            "term": "22f",
            "session": "1",
            "days": "Tuesday",
            "times": "13:00 - 14:40",
            "times_12h": "1:00pm - 2:40pm",
            "location": "ML1_1.118",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124195",
            "textbooks": ""
        },
        {
            "section_address": "bmen1100.103.22f",
            "course_prefix": "bmen",
            "course_number": "1100",
            "section": "103 ",
            "class_number": "85475",
            "title": "Introduction to Bioengineering I ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "19",
            "enrolled_max": "19",
            "instructors": "Benjamin Porter",
            "assistants": "Kavya Balaji",
            "term": "22f",
            "session": "1",
            "days": "Tuesday",
            "times": "13:00 - 14:40",
            "times_12h": "1:00pm - 2:40pm",
            "location": "ML1_1.122",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124196",
            "textbooks": ""
        },
        {
            "section_address": "bmen1100.104.22f",
            "course_prefix": "bmen",
            "course_number": "1100",
            "section": "104 ",
            "class_number": "85329",
            "title": "Introduction to Bioengineering I ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "15",
            "enrolled_max": "19",
            "instructors": "Kathleen Myers",
            "assistants": "Bahareh Kian Pour, Kavya Balaji",
            "term": "22f",
            "session": "1",
            "days": "Friday",
            "times": "10:00 - 11:40",
            "times_12h": "10:00am - 11:40am",
            "location": "ML1_1.118",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124626",
            "textbooks": ""
        },
        {
            "section_address": "bmen1100.105.22f",
            "course_prefix": "bmen",
            "course_number": "1100",
            "section": "105 ",
            "class_number": "85330",
            "title": "Introduction to Bioengineering I ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "19",
            "enrolled_max": "19",
            "instructors": "Kathleen Myers",
            "assistants": "Bahareh Kian Pour, Kavya Balaji",
            "term": "22f",
            "session": "1",
            "days": "Friday",
            "times": "10:00 - 11:40",
            "times_12h": "10:00am - 11:40am",
            "location": "ML1_1.122",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124627",
            "textbooks": ""
        },
        {
            "section_address": "bmen1100.1l2.22f",
            "course_prefix": "bmen",
            "course_number": "1100",
            "section": "1l2 ",
            "class_number": "85331",
            "title": "Introduction to Bioengineering I ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "21",
            "enrolled_max": "24",
            "instructors": "Kathleen Myers",
            "assistants": "Bahareh Kian Pour, Kavya Balaji",
            "term": "22f",
            "session": "1",
            "days": "Wednesday",
            "times": "10:00 - 11:40",
            "times_12h": "10:00am - 11:40am",
            "location": "ML1_1.122",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124628",
            "textbooks": ""
        },
        {
            "section_address": "bmen1208.001.22f",
            "course_prefix": "bmen",
            "course_number": "1208",
            "section": "001 ",
            "class_number": "85506",
            "title": "Introduction to Bioengineering II ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "15",
            "enrolled_max": "19",
            "instructors": "Clark Meyer",
            "assistants": "Harsh Dave, Ruba Afaneh",
            "term": "22f",
            "session": "1",
            "days": "Thursday",
            "times": "16:00 - 17:15",
            "times_12h": "4:00pm - 5:15pm",
            "location": "ML1_1.118",
            "core_area": "",
            "activity_type": "Combined Lec\/Lab w\/Fee",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124054",
            "textbooks": ""
        },
        {
            "section_address": "bmen1208.002.22f",
            "course_prefix": "bmen",
            "course_number": "1208",
            "section": "002 ",
            "class_number": "85509",
            "title": "Introduction to Bioengineering II ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "12",
            "enrolled_max": "19",
            "instructors": "Clark Meyer",
            "assistants": "Harsh Dave, Ruba Afaneh",
            "term": "22f",
            "session": "1",
            "days": "Thursday",
            "times": "16:00 - 17:15",
            "times_12h": "4:00pm - 5:15pm",
            "location": "ML1_1.122",
            "core_area": "",
            "activity_type": "Combined Lec\/Lab w\/Fee",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124055",
            "textbooks": ""
        },
        {
            "section_address": "bmen1300.001.22f",
            "course_prefix": "bmen",
            "course_number": "1300",
            "section": "001 ",
            "class_number": "88329",
            "title": "Introduction to Biomedical Engineering Computing ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "48",
            "enrolled_max": "49",
            "instructors": "Soudeh Ardestani Khoubrouy, Levi Good",
            "assistants": "Ruchita Mahesh Kumar, Belten Langmia",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "11:30 - 12:45",
            "times_12h": "11:30am - 12:45pm",
            "location": "ECSW_2.210",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125236",
            "textbooks": "9780134443850, 9780134498379, 9780323857734 "
        },
        {
            "section_address": "bmen1300.002.22f",
            "course_prefix": "bmen",
            "course_number": "1300",
            "section": "002 ",
            "class_number": "88330",
            "title": "Introduction to Biomedical Engineering Computing ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "47",
            "enrolled_max": "49",
            "instructors": "Soudeh Ardestani Khoubrouy, Levi Good",
            "assistants": "Ruchita Mahesh Kumar, Belten Langmia",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "16:00 - 17:15",
            "times_12h": "4:00pm - 5:15pm",
            "location": "ECSW_2.210",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125237",
            "textbooks": "9780134443850, 9780134498379, 9780323857734 "
        },
        {
            "section_address": "bmen2320.001.22f",
            "course_prefix": "bmen",
            "course_number": "2320",
            "section": "001 ",
            "class_number": "85515",
            "title": "Statics ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "43",
            "enrolled_max": "44",
            "instructors": "Christian Rivera",
            "assistants": "Brandon Nunley, Andrew Glick",
            "term": "22f",
            "session": "1",
            "days": "Monday, Wednesday",
            "times": "16:00 - 17:15",
            "times_12h": "4:00pm - 5:15pm",
            "location": "ECSN_2.112",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl122272",
            "textbooks": "9780133912876, 9780133918922, 9780136912439, 9780138068332 "
        },
        {
            "section_address": "bmen2320.002.22f",
            "course_prefix": "bmen",
            "course_number": "2320",
            "section": "002 ",
            "class_number": "85317",
            "title": "Statics ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "30",
            "enrolled_max": "30",
            "instructors": "Jacopo Ferruzzi",
            "assistants": "Brandon Nunley, Andrew Glick",
            "term": "22f",
            "session": "1",
            "days": "Monday, Wednesday",
            "times": "10:00 - 11:15",
            "times_12h": "10:00am - 11:15am",
            "location": "ECSW_2.325",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl123984",
            "textbooks": "9780133912876, 9780133918922, 9780133921656, 9780136912439, 9780138068332 "
        },
        {
            "section_address": "bmen3150.101.22f",
            "course_prefix": "bmen",
            "course_number": "3150",
            "section": "101 ",
            "class_number": "85745",
            "title": "Biomedical Engineering Laboratory ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "11",
            "enrolled_max": "19",
            "instructors": "Tariq Ali",
            "assistants": "Vedashree Umesh Bhide",
            "term": "22f",
            "session": "1",
            "days": "Tuesday",
            "times": "13:00 - 15:45",
            "times_12h": "1:00pm - 3:45pm",
            "location": "ML1_1.114",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl123149",
            "textbooks": ""
        },
        {
            "section_address": "bmen3200.101.22f",
            "course_prefix": "bmen",
            "course_number": "3200",
            "section": "101 ",
            "class_number": "88334",
            "title": "Biomedical Engineering Fundamentals and Design ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "13",
            "enrolled_max": "30",
            "instructors": "Christian Rivera, Gu Eon Kang",
            "assistants": "Angeloh Stout, David Schmidtke",
            "term": "22f",
            "session": "1",
            "days": "Monday",
            "times": "10:00 - 12:45",
            "times_12h": "10:00am - 12:45pm",
            "location": "ML1_1.118",
            "core_area": "",
            "activity_type": "Laboratory - No Lab Fee",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl123152",
            "textbooks": "9781107087354, 9781316191842 "
        },
        {
            "section_address": "bmen3220.101.22f",
            "course_prefix": "bmen",
            "course_number": "3220",
            "section": "101 ",
            "class_number": "85845",
            "title": "Electrical and Electronic Circuits in Biomedical Engineering Lab ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "14",
            "enrolled_max": "16",
            "instructors": "Tariq Ali",
            "assistants": "Lindy Patterson",
            "term": "22f",
            "session": "1",
            "days": "Tuesday",
            "times": "16:00 - 18:45",
            "times_12h": "4:00pm - 6:45pm",
            "location": "ML1_1.114",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125352",
            "textbooks": ""
        },
        {
            "section_address": "bmen3220.102.22f",
            "course_prefix": "bmen",
            "course_number": "3220",
            "section": "102 ",
            "class_number": "88314",
            "title": "Electrical and Electronic Circuits in Biomedical Engineering Lab ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "18",
            "enrolled_max": "18",
            "instructors": "Tariq Ali",
            "assistants": "Lindy Patterson",
            "term": "22f",
            "session": "1",
            "days": "Thursday",
            "times": "10:00 - 12:45",
            "times_12h": "10:00am - 12:45pm",
            "location": "ML1_1.114",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125353",
            "textbooks": ""
        },
        {
            "section_address": "bmen3220.103.22f",
            "course_prefix": "bmen",
            "course_number": "3220",
            "section": "103 ",
            "class_number": "88315",
            "title": "Electrical and Electronic Circuits in Biomedical Engineering Lab ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "16",
            "enrolled_max": "17",
            "instructors": "Tariq Ali",
            "assistants": "Suhashine Sukumar",
            "term": "22f",
            "session": "1",
            "days": "Thursday",
            "times": "13:00 - 15:45",
            "times_12h": "1:00pm - 3:45pm",
            "location": "ML1_1.118",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125354",
            "textbooks": ""
        },
        {
            "section_address": "bmen3220.104.22f",
            "course_prefix": "bmen",
            "course_number": "3220",
            "section": "104 ",
            "class_number": "88316",
            "title": "Electrical and Electronic Circuits in Biomedical Engineering Lab ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "16",
            "enrolled_max": "17",
            "instructors": "Tariq Ali",
            "assistants": "Vedashree Umesh Bhide",
            "term": "22f",
            "session": "1",
            "days": "Thursday",
            "times": "13:00 - 15:45",
            "times_12h": "1:00pm - 3:45pm",
            "location": "ML1_1.114",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125355",
            "textbooks": ""
        },
        {
            "section_address": "bmen3302.501.22f",
            "course_prefix": "bmen",
            "course_number": "3302",
            "section": "501 ",
            "class_number": "88328",
            "title": "Bioengineering Signals and Systems ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "59",
            "enrolled_max": "59",
            "instructors": "Soudeh Ardestani Khoubrouy",
            "assistants": "Caleb Maymir",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "17:30 - 18:45",
            "times_12h": "5:30pm - 6:45pm",
            "location": "ECSW_1.355",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125238",
            "textbooks": ""
        },
        {
            "section_address": "bmen3310.001.22f",
            "course_prefix": "bmen",
            "course_number": "3310",
            "section": "001 ",
            "class_number": "85725",
            "title": "Fluid Mechanics and Transport Processes in Biomedical Engineering ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "25",
            "enrolled_max": "30",
            "instructors": "Christian Rivera",
            "assistants": "Andrew Glick, Gu Eon Kang",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "14:30 - 15:45",
            "times_12h": "2:30pm - 3:45pm",
            "location": "CB_1.218",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl122273",
            "textbooks": "9780134608976, 9780134637433, 9780137517091, 9780138068332, 9780470128688 "
        },
        {
            "section_address": "bmen3315.001.22f",
            "course_prefix": "bmen",
            "course_number": "3315",
            "section": "001 ",
            "class_number": "85499",
            "title": "Thermodynamics and Physical Chemistry in Biomedical Engineering ",
            "topic": "",
            "enrolled_status": "Closed",
            "enrolled_current": "39",
            "enrolled_max": "39",
            "instructors": "David Schmidtke",
            "assistants": "Lucero Ramirez",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "10:00 - 11:15",
            "times_12h": "10:00am - 11:15am",
            "location": "FN_2.104",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124897",
            "textbooks": ""
        },
        {
            "section_address": "bmen3315.002.22f",
            "course_prefix": "bmen",
            "course_number": "3315",
            "section": "002 ",
            "class_number": "85507",
            "title": "Thermodynamics and Physical Chemistry in Biomedical Engineering ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "36",
            "enrolled_max": "49",
            "instructors": "Stuart Cogan",
            "assistants": "Lucero Ramirez",
            "term": "22f",
            "session": "1",
            "days": "Monday, Wednesday",
            "times": "08:30 - 09:45",
            "times_12h": "8:30am - 9:45am",
            "location": "SOM_11.210",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125571",
            "textbooks": "9780136056065 "
        },
        {
            "section_address": "bmen3320.001.22f",
            "course_prefix": "bmen",
            "course_number": "3320",
            "section": "001 ",
            "class_number": "85306",
            "title": "Electrical and Electronic Circuits in Biomedical Engineering ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "62",
            "enrolled_max": "69",
            "instructors": "Tariq Ali",
            "assistants": "Chance Kaneshiro",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "08:30 - 09:45",
            "times_12h": "8:30am - 9:45am",
            "location": "GR_4.301",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl123143",
            "textbooks": "9780133760033, 9780133760033 "
        },
        {
            "section_address": "bmen3325.001.22f",
            "course_prefix": "bmen",
            "course_number": "3325",
            "section": "001 ",
            "class_number": "85431",
            "title": "Advanced Computational Tools for Biomedical Engineering ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "11",
            "enrolled_max": "19",
            "instructors": "Katherine Brown",
            "assistants": "Niharika Pandala",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "14:30 - 15:45",
            "times_12h": "2:30pm - 3:45pm",
            "location": "ML1_1.106",
            "core_area": "",
            "activity_type": "Combined Lec\/Lab no Fee",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl122624",
            "textbooks": "9780128122037, 9780128135105, 9780128122037, 9780128135105 "
        },
        {
            "section_address": "bmen3325.002.22f",
            "course_prefix": "bmen",
            "course_number": "3325",
            "section": "002 ",
            "class_number": "85742",
            "title": "Advanced Computational Tools for Biomedical Engineering ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "7",
            "enrolled_max": "19",
            "instructors": "Clark Meyer",
            "assistants": "",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "10:00 - 11:15",
            "times_12h": "10:00am - 11:15am",
            "location": "ML1_1.106",
            "core_area": "",
            "activity_type": "Combined Lec\/Lab no Fee",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl120562",
            "textbooks": ""
        },
        {
            "section_address": "bmen3331.001.22f",
            "course_prefix": "bmen",
            "course_number": "3331",
            "section": "001 ",
            "class_number": "88333",
            "title": "Cell and Molecular Engineering ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "8",
            "enrolled_max": "49",
            "instructors": "Polimyr Caesar Dave Dingal",
            "assistants": "Grady Mukubwa",
            "term": "22f",
            "session": "1",
            "days": "Monday, Wednesday",
            "times": "08:30 - 09:45",
            "times_12h": "8:30am - 9:45am",
            "location": "SOM_2.714",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl122036",
            "textbooks": "9780134605197, 9780134704227, 9780134715070, 9780135212905 "
        },
        {
            "section_address": "bmen3331.002.22f",
            "course_prefix": "bmen",
            "course_number": "3331",
            "section": "002 ",
            "class_number": "88347",
            "title": "Cell and Molecular Engineering ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "22",
            "enrolled_max": "44",
            "instructors": "Caroline Jones",
            "assistants": "Grady Mukubwa",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "13:00 - 14:15",
            "times_12h": "1:00pm - 2:15pm",
            "location": "ECSN_2.112",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124556",
            "textbooks": ""
        },
        {
            "section_address": "bmen3332.001.22f",
            "course_prefix": "bmen",
            "course_number": "3332",
            "section": "001 ",
            "class_number": "88366",
            "title": "Quantitative Physiology for Engineers ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "29",
            "enrolled_max": "49",
            "instructors": "Shashank Sirsi",
            "assistants": "Sugandha Chaudhary",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "13:00 - 14:15",
            "times_12h": "1:00pm - 2:15pm",
            "location": "SCI_3.250",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "",
            "textbooks": ""
        },
        {
            "section_address": "bmen3332.002.22f",
            "course_prefix": "bmen",
            "course_number": "3332",
            "section": "002 ",
            "class_number": "88376",
            "title": "Quantitative Physiology for Engineers ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "27",
            "enrolled_max": "49",
            "instructors": "Levi Good",
            "assistants": "Sugandha Chaudhary",
            "term": "22f",
            "session": "1",
            "days": "Monday, Wednesday",
            "times": "16:00 - 17:15",
            "times_12h": "4:00pm - 5:15pm",
            "location": "FN_2.102",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125130",
            "textbooks": "9780134714868 "
        },
        {
            "section_address": "bmen3341.001.22f",
            "course_prefix": "bmen",
            "course_number": "3341",
            "section": "001 ",
            "class_number": "85828",
            "title": "Probability Theory and Statistics for Biomedical Engineers ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "32",
            "enrolled_max": "60",
            "instructors": "Kathleen Myers",
            "assistants": "Niharika Pandala",
            "term": "22f",
            "session": "1",
            "days": "Monday, Wednesday",
            "times": "08:30 - 09:45",
            "times_12h": "8:30am - 9:45am",
            "location": "ECSW_3.210",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124629",
            "textbooks": "9780134507248 "
        },
        {
            "section_address": "bmen3350.001.22f",
            "course_prefix": "bmen",
            "course_number": "3350",
            "section": "001 ",
            "class_number": "85729",
            "title": "Biomedical Component and System Design ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "13",
            "enrolled_max": "40",
            "instructors": "Katherine Brown",
            "assistants": "Suhashine Sukumar",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "11:30 - 12:45",
            "times_12h": "11:30am - 12:45pm",
            "location": "ECSN_2.126",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl122761",
            "textbooks": "9781119457312, 9781119457336, 9781119457312, 9781119457336 "
        },
        {
            "section_address": "bmen3380.001.22f",
            "course_prefix": "bmen",
            "course_number": "3380",
            "section": "001 ",
            "class_number": "85542",
            "title": "Medical Imaging Systems and Methods ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "34",
            "enrolled_max": "35",
            "instructors": "Levi Good",
            "assistants": "Rouzbeh Molaei Imenabadi",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "13:00 - 14:15",
            "times_12h": "1:00pm - 2:15pm",
            "location": "FN_2.104",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125131",
            "textbooks": "9780511851209, 9780521190657 "
        },
        {
            "section_address": "bmen3399.001.22f",
            "course_prefix": "bmen",
            "course_number": "3399",
            "section": "001 ",
            "class_number": "85498",
            "title": "Introductory Biomechanics ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "57",
            "enrolled_max": "79",
            "instructors": "Victor Varner",
            "assistants": "Ke'Vaughn Waldon",
            "term": "22f",
            "session": "1",
            "days": "Tuesday, Thursday",
            "times": "10:00 - 11:15",
            "times_12h": "10:00am - 11:15am",
            "location": "ECSW_1.365",
            "core_area": "",
            "activity_type": "Lecture",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl124881",
            "textbooks": ""
        },
        {
            "section_address": "bmen4110.101.22f",
            "course_prefix": "bmen",
            "course_number": "4110",
            "section": "101 ",
            "class_number": "85313",
            "title": "Biomedical Feedback Systems Laboratory ",
            "topic": "",
            "enrolled_status": "Open",
            "enrolled_current": "20",
            "enrolled_max": "24",
            "instructors": "Levi Good",
            "assistants": "Priyansh Pathak",
            "term": "22f",
            "session": "1",
            "days": "Monday",
            "times": "13:00 - 15:45",
            "times_12h": "1:00pm - 3:45pm",
            "location": "ML1_1.110",
            "core_area": "",
            "activity_type": "Laboratory",
            "school": "ecs",
            "dept": "encsbien",
            "syllabus": "syl125132",
            "textbooks": ""
        },
    ]

professors = [
        {
            'name': 'Kathleen Myers',
            'availability': {
                'Monday': [(time_to_minutes('9:00'), time_to_minutes('16:00'))],
                'Tuesday': [(time_to_minutes('9:00'), time_to_minutes('16:00'))],
                'Wednesday': [(time_to_minutes('9:00'), time_to_minutes('16:00'))],
                'Thursday': [(time_to_minutes('9:00'), time_to_minutes('16:00'))],
                'Friday': [(time_to_minutes('9:00'), time_to_minutes('16:00'))],
                # ... other days
            },
            'preferences': {
                '1200': 10, # Let's say 10 is the highest preference, 0 is no preference.
                '1334': 5,
                '2340': 3,
                '3162': 1 
                # ... other courses
            }
        }
        # ... other professors
    ]
""""
print(professors[0]['availability'])
@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        print(data['professors'][0]['availability'])
        professors1 = data.get('professors')
        courses1 = data.get('courses')
        
        if not professors1 or not courses1:
            return jsonify({'error': 'Missing professors or courses data'}), 400
        
        solution = generate_schedule(courses1, professors1)
        return jsonify({'solution': solution})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""

@app.route('/dbclass', methods=['GET'])
def dbclass():
    try:
       conn = mysql.connector.connect(**config)
       print("Connection established")
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    else:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM professorschema.class cls where cls.enrolled_status = 'Open' order by title;")
      row_headers=[x[0] for x in cursor.description]  #gather the rowheaders
      classesdb = cursor.fetchall()
      classes = []
      for result in classesdb:
        course_dict = dict(zip(row_headers, result))
        course_dict['days'] = course_dict['days'].split(', ') if course_dict['days'] else []
        course_dict['times'] = course_dict['times'] if course_dict['times'] != 'tbd' else None

        # Filter out courses with missing essential data
        if course_dict['days'] and course_dict['times']:
            classes.append(course_dict)
      #cursor.execute('SELECT * FROM professorschema.class cls where cls.class_number = % s',(siid, ))
      #classes = cursor.fetchone()
      # Cleanup
      cursor.close()
      conn.close()

    #return jsonify(classes)
    return classes #json.dumps(classes)

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        #print(data)
        #print(data['professors'][0]['availability'])
        professor = data.get('professor')
        professors1 = professor.get('professors')
        #print(professors1)
        #professors1 = data.get('professors')
        #courses1 = data.get('courses')
        
        if not professors1:
            return jsonify({'error': 'Missing professors data'}), 400
        print("before generating")
        index = generate_schedule(dbclass(), professors1)
        print("after generating")
        solution = decode_schedules(index, dbclass(), professors1)
        print(index)
        return jsonify({'solution': solution})
    except Exception as e:
        print("Error occurred:", e)
        return jsonify({'error': str(e)}), 500

"""
@app.route('/solve', methods=['GET'])
def solve():
        index = generate_schedule(dbclass(), professors)
        solution = decode_schedules(index, dbclass(), professors)#generate_schedule(courses, professors)
        return jsonify([{'solution': solution}, {'index' : index}])
"""

def split_days(days_string):
    # Split the string by ", " and return the resulting list
    return days_string.split(", ") if days_string else []

        
def generate_schedule(courses, professors, num_schedules=5):
    all_schedules = []

    # Convert days to integers (Monday=0, Tuesday=1, etc.)
    day_to_int = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
    }
    # Create a reverse mapping from integers to day names
    int_to_day = {v: k for k, v in day_to_int.items()}

    # Aggregate unique preference levels from all professors
    unique_prefs = set()
    for professor in professors:
        unique_prefs.update(professor['preferences'].values())

    for schedule_num in range(num_schedules):
        solver = pywraplp.Solver.CreateSolver('SCIP')

        x = {}
        for i, course in enumerate(courses):
            for j, professor in enumerate(professors):
                x[i, j] = solver.IntVar(0, 1, f'x_{i}_{j}')

        # Constraints: Avoid overlap and strictly respect availability
        for j, professor in enumerate(professors):
            available_days = set(day_to_int[day] for day in professor['availability'])

            for i, course in enumerate(courses):
                course_days = [day_to_int[d] for d in course['days']]

                # Process each day the course is held
                for course_day in course_days:
                    if course_day in available_days:
                        course_start, course_end = [time_to_minutes(t) for t in course['times'].split(' - ')]
                        fits_in_slot = any(start <= course_start < course_end <= end for start, end in professor['availability'][int_to_day[course_day]])
                        if not fits_in_slot:
                            solver.Add(x[i, j] == 0)
                    else:
                        solver.Add(x[i, j] == 0)

                # Avoid overlap with other courses
                for k, other_course in enumerate(courses):
                    if i != k:
                        other_course_days = [day_to_int[d] for d in other_course['days']]
                        overlap_days = set(course_days) & set(other_course_days)
                        if overlap_days:
                            for overlap_day in overlap_days:
                                if overlap_day in available_days:
                                    course_start, course_end = [time_to_minutes(t) for t in course['times'].split(' - ')]
                                    other_course_start, other_course_end = [time_to_minutes(t) for t in other_course['times'].split(' - ')]
                                    # Check if courses overlap on overlap_day
                                    if not (course_end <= other_course_start or course_start >= other_course_end):
                                        solver.Add(x[i, j] + x[k, j] <= 1)


        # Constraints: Avoid overlap within a schedule
        for j, professor in enumerate(professors):
            for i, course in enumerate(courses):
                course_start, course_end = [time_to_minutes(t) for t in course['times'].split(' - ')]
                for k, other_course in enumerate(courses):
                    if i != k:
                        other_course_start, other_course_end = [time_to_minutes(t) for t in other_course['times'].split(' - ')]
                        # Check if the courses overlap in time
                        overlap = not (course_end <= other_course_start or course_start >= other_course_end)
                        if overlap:
                            # Add constraint to avoid assigning overlapping courses to the same professor
                            solver.Add(x[i, j] + x[k, j] <= 1)

        # Constraints: Ensure each preference level is represented exactly once
        for pref in unique_prefs:
            solver.Add(solver.Sum(x[i, j] for i, course in enumerate(courses) 
                                  for j, professor in enumerate(professors) 
                                  if professor['preferences'].get(course['course_number'], 0) == pref) == 1)


        # Objective: Maximize total preference
        solver.Maximize(solver.Sum(professors[j]['preferences'].get(courses[i]['course_number'], 0) * x[i, j] for i in range(len(courses)) for j in range(len(professors))))

        # Avoid previous schedules
        if schedule_num > 0:
            for prev_schedule in all_schedules:
                solver.Add(solver.Sum([x[i, j] for i, j in prev_schedule]) <= len(prev_schedule) - 1)

        # Solve the problem
        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
                current_schedule = []
                for i, course in enumerate(courses):
                    for j, professor in enumerate(professors):
                        if x[i, j].solution_value() == 1:
                            assignment = {
                                'instructor': professor['name'],
                                'section_address': course['section_address'],
                                'course': course['title'],
                                'course_number': course['course_number'],
                                'class_number' : course['class_number'],
                                'time': course['times']
                            }
                            current_schedule.append((i, j))
                all_schedules.append(current_schedule)
        else:
            print('No more optimal solutions found!')
            break  # Correctly placed inside the loop now

    return all_schedules


def days_to_int(days_arr):
    score_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
    }
    
    days_indices = []
    for day in days_arr:
        # Use .get() to return None if the day is not found, 
        # this way you can filter out any invalid days.
        index = score_map.get(day.strip(), None)
        if index is not None:
            days_indices.append(index)

    return days_indices



def decode_schedules(solution, courses, professors):
    print("decoding")
    i = 1
    decoded_solutions = []
    for schedule in solution:
        decoded_schedule = []
        for course_index, professor_index in schedule:
            course_info = courses[course_index]
            professor_info = professors[professor_index]
            decoded_assignment = {
                'courseName': course_info['section_address'][:-4],
                'courseDays': days_to_int(course_info['days']),
                'courseStart': course_info['times'].split(' - ')[0],
                'courseEnd' : course_info['times'].split(' - ')[1]
            }
            #print(decoded_assignment)
            decoded_schedule.append(decoded_assignment)
        decode_wrapper = {
            "scheduleName": f"Schedule {i}",
            "courses": decoded_schedule,
            }
        #print(decode_wrapper)
        decoded_solutions.append(decode_wrapper)
        i+=1
    return decoded_solutions



#scored_preferences = assign_preference_score(preferences)
#print(scored_preferences)


if __name__ == '__main__':
    app.run(port=5000)
