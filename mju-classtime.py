"""
MJU-ClassTime (VERSION 1.0.1)
[Dev]
-JeonWooHyun (MJU 경영대학 1학년)
[주요기능]
-명지대 학사정보시스템의 학기중 수업정보를 크롤링하여 json파일로 저장합니다.
"""
"""
The MIT License

Copyright (c) 2024 JeonWooHYun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import os #for console-adjust
from rich.panel import Panel #for console-design
from rich.console import Console #for console-design
from rich.prompt import Prompt #for console-design
from bs4 import BeautifulSoup #for crolling
import requests #for crolling
import time
import re
import math
import json
from collections import OrderedDict
from tqdm import tqdm

console = Console() #rich.console

def loading():
    console.print(' /$$      /$$    /$$$$$ /$$   /$$          /$$$$$$  /$$                           /$$$$$$$$ /$$                        ', style="#af00ff")
    console.print('| $$$    /$$$   |__  $$| $$  | $$         /$$__  $$| $$                          |__  $$__/|__/                        ', style="#af00ff")
    console.print('| $$$$  /$$$$      | $$| $$  | $$        | $$  \\__/| $$  /$$$$$$   /$$$$$$$ /$$$$$$$| $$    /$$ /$$$$$$/$$$$   /$$$$$$ ', style="#af00ff")
    console.print('| $$ $$/$$ $$      | $$| $$  | $$ /$$$$$$| $$      | $$ |____  $$ /$$_____//$$_____/| $$   | $$| $$_  $$_  $$ /$$__  $$', style="#af00ff")
    console.print('| $$  $$$| $$ /$$  | $$| $$  | $$|______/| $$      | $$  /$$$$$$$|  $$$$$$|  $$$$$$ | $$   | $$| $$ \\ $$ \\ $$| $$$$$$$$', style="#af00ff")
    console.print('| $$\\  $ | $$| $$  | $$| $$  | $$        | $$    $$| $$ /$$__  $$ \\____  $$\\____  $$| $$   | $$| $$ | $$ | $$| $$_____/', style="#af00ff")
    console.print('| $$ \\/  | $$|  $$$$$$/|  $$$$$$/        |  $$$$$$/| $$|  $$$$$$$ /$$$$$$$//$$$$$$$/| $$   | $$| $$ | $$ | $$|  $$$$$$$', style="#af00ff")
    console.print('|__/     |__/ \\______/  \\______/          \\______/ |__/ \\_______/|_______/|_______/ |__/   |__/|__/ |__/ |__/ \\_______/', style="#af00ff")
    console.print(Panel.fit('MJU-ClassTime (Version 1.0.1) Made by JeonWooHyun', style="#009F8C"))    
    print('\n 5초 뒤 실행됩니다. . .')         
    time.sleep(5)                                                                                                          
    clear_terminal()
    setting()

def setting():
    global student_cookie
    global student_csrf
    global Sem
    global Yer
    global Major_code
    console.print(Panel.fit('[INFO!] 학사정보시스템(MSI)는 접속시 학생 접근 토큰을 요구하고있습니다.'), style="red")
    console.print('**사용자-토큰-획득.txt에 따라 쿠키를 추출한 후 아래에 입력해주시기 바랍니다.')
    student_cookie = Prompt.ask('Cookie') #쿠키 획득
    student_csrf = Prompt.ask('Csrf') #Csrf 획득
    clear_terminal()
    console.print(Panel.fit('추출하시려는 학기&수업정보를 입력해주시기 바랍니다.'), style="red")
    console.print(Panel.fit('[학과코드] **문서참조'), style="#2CEEBE")
    Yer = Prompt.ask('년도(4자리)', default="2024")
    Sem = Prompt.ask('학기', choices=["10", "15", "20","25"])
    Major_code = input('학과 코드:')
    crolling()

pages = str(1)

def crolling():
    global soup
    global pages
    global actual_pages
    payload = {
        "year": Yer,
        "smt": Sem,
        "searchType": "1",
        "deptCd": Major_code,
        "curiNm": "",
        "page": pages, 
        "campusDiv": "",
        "_csrf": student_csrf
    }
    headers = {
        "Cookie": student_cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 "
        }
    url = "https://msi.mju.ac.kr/servlet/su/sue/Sue00Svl06viewTimetable"
    response = requests.post(url, headers=headers, data=payload)  

    soup = BeautifulSoup(response.text, 'html.parser') 

    if int(pages) == 1: #처음실행일 경우
        #크롤링하기

        #검색해야될 페이지수 찾기
        count_list = str(soup.find("div", "data-title")) #총 검색 수가 포함된 문장 파싱
        all_list_count = re.sub(r'[^0-9]', '', count_list) #숫자만 추출
        actual_pages = (int(all_list_count) / 10) #페이지당10개씩 나누기

        if str(type(actual_pages)) == "<class 'float'>": #소수점 검사
            actual_pages = math.ceil(actual_pages) 
            pages = str(int(pages) + 1) 
            adjust() #페이지수는 Update하고 일단 자료 정리하러~
        else:
            #actual_pages는 정수 그대로 가져감
            pages = str(int(pages)) + 1 
            adjust()

    elif int(pages) == actual_pages: #n번째 실행시 마지막 페이지수에 도달한다면
        print('\n 온전하지 않은 json파일을 정제합니다.')
        filtering()

        want_upload = input("mysql 업로드 프로그램을 실행시키겠습니까? (Y/N)")
        if(want_upload == 'Y'):
            os.system('upload_mysql.py')
        
    else:
        #게속 반복
        pages = str(int(pages) + 1)
        adjust()


#페이지별 파싱 결과 분류 및 정리
def adjust():   
    pc_list_div = soup.find(id='pc-list')
    table = pc_list_div.find('table')
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    data = []

    for row in rows:
        cells = row.find_all('td')
        ghualho_pattern = r'\((.*?)\)'
        classroom = re.findall(ghualho_pattern, cells[8].get_text(strip=True))
        classroom_sorted = list(OrderedDict.fromkeys(classroom))
        schedule = re.sub(ghualho_pattern, '', cells[8].get_text(strip=True)).strip()

        course_data = {
            "course_id": cells[6].get_text(strip=True), #강좌번호
            "course_name": cells[1].get_text(strip=True), #강좌명
            "credits": cells[2].get_text(strip=True), #학점
            "lecture_time": cells[3].get_text(strip=True), #강의시간
            "professor_name": cells[5].get_text(strip=True), #교수명
            "course_description": cells[9].get_text(strip=True), #강의 비고
            "schedule": schedule, #일정
            "classroom": classroom_sorted #강의실
        }
        data.append(course_data) 

    global file_output
    file_output = Major_code+'courses.json'
    json_saving(Major_code+'courses.json', data)
    print(data)
    crolling()

def json_saving(filename, data):
    with open(filename, 'a', encoding='utf-8') as f:
        #json.dump(data, f, indent=4, ensure_ascii=False)
        for item in data:
            json.dump(item, f, ensure_ascii=False, indent=4)  # 객체를 JSON 문자열로 변환하여 파일에 쓰기
            f.write(',\n')

def filtering():
    with open(file_output, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = r'\{.*?\}'
    matches = re.findall(pattern, content, re.DOTALL)

    data_list = [json.loads(match) for match in matches]

    with open(file_output, 'w', encoding='utf-8') as file:
        json.dump(data_list, file, ensure_ascii=False, indent=4)

def clear_terminal():
    if os.name == 'nt': 
        os.system('cls')
    else:
        os.system('clear')

loading()