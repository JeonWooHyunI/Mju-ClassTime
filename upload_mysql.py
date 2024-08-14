import pymysql
import json
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv
import os
from tqdm import tqdm
import time

load_dotenv()


HOST = os.getenv("MYSQL_HOST")
USER = os.getenv("MYSQL_ID")
PW = os.getenv("MYSQL_PW")
DB = os.getenv("DB_NAME")

# MySQL 데이터베이스 연결 설정
db_config = {
    'host': HOST,
    'user': USER,
    'password': PW,
    'database': DB,
    'charset': 'utf8mb4'
}

print(HOST + "에 업로드를 진행하시겠습니다.")
print('원치 않으면 5초 이내에 종료해 주세요. Ctrl + c')
#time.sleep(5) 

def upload_data_to_mysql(json_data):
    # 데이터베이스에 연결
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    total_items = len(json_data)

    with tqdm(total=total_items, desc="Uploading data") as pbar:
        # JSON 데이터를 테이블에 삽입
        for item in json_data:
            course_id = item.get("course_id")
            course_name = item.get("course_name")
            credits = item.get("credits")
            lecture_time = item.get("lecture_time")
            professor_name = item.get("professor_name")
            course_description = item.get("course_description")
            schedule = item.get("schedule")
            classroom = ','.join(item.get("classroom", []))  # 목록을 쉼표로 구분된 문자열로 변환

            sql = """
            INSERT INTO course (course_id, course_name, credits, lecture_time, professor_name, course_description, schedule, classroom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                course_name = VALUES(course_name),
                credits = VALUES(credits),
                lecture_time = VALUES(lecture_time),
                course_description = VALUES(course_description),
                schedule = VALUES(schedule),
                classroom = VALUES(classroom);
            """
        
            try:
                cursor.execute(sql, (course_id, course_name, credits, lecture_time, professor_name, course_description, schedule, classroom))
            except pymysql.MySQLError as e:
                print(f"Error: {e}")

            pbar.update(1)

    # 커밋하고 연결 종료
    connection.commit()
    cursor.close()
    connection.close()

def select_file():
    root = tk.Tk()
    root.withdraw()  # Tkinter GUI 창을 숨깁니다

    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],
        title="Select a JSON file"
    )
    
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                json_data = json.load(file)
                upload_data_to_mysql(json_data)
                print("성공적으로 업로드되었습니다!")
            except json.JSONDecodeError as e:
                print(f"Error reading JSON file: {e}")

if __name__ == "__main__":
    select_file()