from flask import Flask, jsonify, render_template_string
import requests
from datetime import datetime, timedelta, timezone
import re
import os

app = Flask(__name__)

# ⚠️ 여기에 NEIS API Key 입력
API_KEY = "82e9dc4cbc6340b2b4e3f5c8a8c56f9c"
ATPT_OFCDC_SC_CODE = "J10"  # 교육청 코드
SD_SCHUL_CODE = "7530189"   # 양명고 학교 코드

# 한국시간 기준 날짜 계산
def get_date(offset):
    KST = timezone(timedelta(hours=9))
    d = datetime.now(KST) + timedelta(days=offset)
    return d.strftime("%Y%m%d")

# 급식 가져오기
def get_meal(date):
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={API_KEY}&Type=json&pIndex=1&pSize=10&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={date}"
    try:
        res = requests.get(url, timeout=5).json()
        meal = res["mealServiceDietInfo"][1]["row"][0]["DDISH_NM"]
        meal = re.sub(r"<br\s*/?>", "\n", meal)
        meal = meal.replace("(양명)", "")
        return meal
    except:
        return "급식 정보 없음"

@app.route("/meal")
def meal():
    today = get_meal(get_date(0))
    tomorrow = get_meal(get_date(1))
    return jsonify({"today": today, "tomorrow": tomorrow})

@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>양명고 급식</title>
<style>
body{
    font-family:sans-serif;
    text-align:center;
    margin:0;
    padding:20px;
    background:#f5f5f5;
}
button{
    padding:15px 25px;
    margin:10px;
    border:none;
    border-radius:10px;
    background:#4CAF50;
    color:white;
    font-size:18px;
    cursor:pointer;
    width:45%;
}
button:hover{
    background:#45a049;
}
.box{
    width:90%;
    max-width:400px;
    margin:20px auto;
    padding:20px;
    background:white;
    border-radius:15px;
    box-shadow:0 3px 10px rgba(0,0,0,0.1);
    word-break:break-word;
    font-size:16px;
}
#meal{
    white-space:pre-line;
}
</style>
</head>
<body>

<h1 style="font-size:24px;">양명고 급식</h1>

<button onclick="showToday()">오늘 급식</button>
<button onclick="showTomorrow()">내일 급식</button>

<div class="box">
<p id="meal">불러오는 중...</p>
</div>

<script>

let todayMeal=""
let tomorrowMeal=""

async function loadMeals(){
    const res = await fetch("/meal")
    const data = await res.json()
    todayMeal = data.today
    tomorrowMeal = data.tomorrow
    document.getElementById("meal").innerText = todayMeal
}

function showToday(){
    document.getElementById("meal").innerText = todayMeal
}

function showTomorrow(){
    document.getElementById("meal").innerText = tomorrowMeal
}

loadMeals()

// 00:00 자동 갱신
function scheduleMidnightRefresh(){
    const now = new Date()
    const midnight = new Date()
    midnight.setHours(24,0,0,0)
    const timeUntilMidnight = midnight - now

    setTimeout(()=>{
        loadMeals()
        scheduleMidnightRefresh()
    }, timeUntilMidnight)
}

scheduleMidnightRefresh()

</script>

</body>
</html>
""")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)