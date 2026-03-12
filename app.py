from flask import Flask, jsonify, render_template_string
import requests
from datetime import datetime, timedelta, timezone
import re
import os

app = Flask(__name__)

API_KEY = "82e9dc4cbc6340b2b4e3f5c8a8c56f9c"

ATPT_OFCDC_SC_CODE = "J10"
SD_SCHUL_CODE = "7530189"

GRADE = "1"      # 학년
CLASS_NM = "5"   # 반

cache = {}

def get_kst():
    KST = timezone(timedelta(hours=9))
    return datetime.now(KST)

def get_date(offset):
    return (get_kst() + timedelta(days=offset)).strftime("%Y%m%d")

def clean_text(text):
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = text.replace("(양명)", "")
    return text

def get_meal(date):
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={date}"
    try:
        res = requests.get(url, timeout=5).json()
        meal = res["mealServiceDietInfo"][1]["row"][0]["DDISH_NM"]
        return clean_text(meal)
    except:
        return "급식 정보 없음"

def get_timetable(date):
    url = f"https://open.neis.go.kr/hub/hisTimetable?KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&ALL_TI_YMD={date}&GRADE={GRADE}&CLASS_NM={CLASS_NM}"
    try:
        res = requests.get(url, timeout=5).json()
        rows = res["hisTimetable"][1]["row"]

        result = []
        for r in rows:
            period = r["PERIO"]
            subject = r["ITRT_CNTNT"]
            result.append(f"{period}교시 {subject}")

        return "\n".join(result)
    except:
        return "시간표 정보 없음"

def load_data():
    today = get_date(0)
    tomorrow = get_date(1)

    cache["today_meal"] = get_meal(today)
    cache["tomorrow_meal"] = get_meal(tomorrow)

    cache["today_tt"] = get_timetable(today)
    cache["tomorrow_tt"] = get_timetable(tomorrow)

@app.route("/data")
def data():
    if not cache:
        load_data()
    return jsonify(cache)

@app.route("/")
def home():
    return render_template_string("""

<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>양명고 급식 & 시간표</title>

<style>

body{
font-family:sans-serif;
background:#f5f5f5;
text-align:center;
padding:20px;
margin:0;
}

h1{
font-size:24px;
}

button{

width:45%;
padding:14px;
margin:8px;
border:none;
border-radius:10px;
background:#4CAF50;
color:white;
font-size:16px;
cursor:pointer;

}

button:hover{
background:#43a047;
}

.box{

background:white;
max-width:420px;
margin:20px auto;
padding:20px;
border-radius:15px;
box-shadow:0 3px 10px rgba(0,0,0,0.1);
white-space:pre-line;
min-height:150px;

}

</style>

</head>

<body>

<h1>양명고 급식 & 시간표</h1>

<button onclick="show('today_meal')">오늘 급식</button>
<button onclick="show('tomorrow_meal')">내일 급식</button>

<br>

<button onclick="show('today_tt')">오늘 시간표</button>
<button onclick="show('tomorrow_tt')">내일 시간표</button>

<div class="box" id="box">
불러오는 중...
</div>

<script>

let data={}

async function load(){

const res = await fetch("/data?"+Date.now())
data = await res.json()

document.getElementById("box").innerText=data.today_meal

}

function show(type){

document.getElementById("box").innerText=data[type]

}

load()

function scheduleRefresh(){

const now = new Date()

const midnight = new Date()

midnight.setHours(24,0,0,0)

const diff = midnight - now

setTimeout(()=>{

location.reload()

},diff)

}

scheduleRefresh()

</script>

</body>

</html>

""")

if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)