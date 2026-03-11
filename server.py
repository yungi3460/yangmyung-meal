from flask import Flask, jsonify, render_template_string
import requests
from datetime import datetime, timedelta
import re

app = Flask(__name__)

API_KEY = "82e9dc4cbc6340b2b4e3f5c8a8c56f9c"
ATPT_OFCDC_SC_CODE = "J10"
SD_SCHUL_CODE = "7530189"

def get_date(offset):
    d = datetime.now() + timedelta(days=offset)
    return d.strftime("%Y%m%d")

def get_meal(date):
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={API_KEY}&Type=json&pIndex=1&pSize=10&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={date}"
    try:
        res = requests.get(url).json()
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
<title>양명고 급식</title>
<style>
body{font-family:sans-serif;text-align:center;margin-top:60px;background:#f5f5f5;}
button{padding:10px 20px;margin:5px;border:none;border-radius:8px;background:#4CAF50;color:white;font-size:16px;cursor:pointer;}
button:hover{background:#45a049;}
.box{width:320px;margin:20px auto;padding:20px;background:white;border-radius:12px;box-shadow:0 3px 10px rgba(0,0,0,0.1);}
#meal{white-space:pre-line;}
</style>
</head>
<body>
<h1>양명고 급식</h1>
<button onclick="showToday()">오늘 급식</button>
<button onclick="showTomorrow()">내일 급식</button>
<div class="box">
<p id="meal">불러오는 중...</p>
</div>
<script>
let todayMeal="", tomorrowMeal="";
async function loadMeals(){
    const res = await fetch("/meal")
    const data = await res.json()
    todayMeal = data.today
    tomorrowMeal = data.tomorrow
    document.getElementById("meal").innerText = todayMeal
}
function showToday(){ document.getElementById("meal").innerText = todayMeal }
function showTomorrow(){ document.getElementById("meal").innerText = tomorrowMeal }
loadMeals()
function scheduleMidnightRefresh(){
    const now=new Date()
    const midnight=new Date()
    midnight.setHours(24,0,0,0)
    const timeUntilMidnight=midnight-now
    setTimeout(()=>{ loadMeals(); scheduleMidnightRefresh(); },timeUntilMidnight)
}
scheduleMidnightRefresh()
</script>
</body>
</html>
""")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render가 PORT 환경변수로 포트 전달
    app.run(host="0.0.0.0", port=port)

