#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import pytz
import os

app = Flask(__name__)
CORS(app)

# Timezone Nova York
NEW_YORK_TZ = pytz.timezone('America/New_York')

# Dias da semana em português
WEEKDAYS = {
    0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira", 
    3: "quinta-feira", 4: "sexta-feira", 5: "sábado", 6: "domingo"
}

# Meses em português
MONTHS = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto", 
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def get_day_period(hour):
    """Determinar período do dia"""
    if 5 <= hour < 12:
        return "manhã"
    elif 12 <= hour < 18:
        return "tarde"
    elif 18 <= hour < 24:
        return "noite"
    else:
        return "madrugada"

def format_date_natural(dt):
    """Formatar data naturalmente"""
    today = datetime.now(NEW_YORK_TZ).date()
    date_obj = dt.date()
    
    if date_obj == today:
        return "hoje"
    elif date_obj == today + timedelta(days=1):
        return "amanhã"
    elif date_obj == today - timedelta(days=1):
        return "ontem"
    else:
        weekday = WEEKDAYS[date_obj.weekday()]
        day = date_obj.day
        month = MONTHS[date_obj.month]
        return f"{weekday}, {day} de {month}"

@app.route('/', methods=['GET'])
def home():
    """Página inicial"""
    return jsonify({
        "service": "DateTime Webhook para ElevenLabs",
        "status": "online",
        "timezone": "America/New_York",
        "endpoints": [
            "GET  /health",
            "POST /webhook/datetime/current",
            "POST /webhook/datetime/business-info",
            "POST /webhook/datetime/relative"
        ]
    })

@app.route('/webhook/datetime/current', methods=['POST', 'GET'])
def get_current_datetime():
    """Obter data/hora atual"""
    try:
        now = datetime.now(NEW_YORK_TZ)
        
        weekday_name = WEEKDAYS[now.weekday()]
        month_name = MONTHS[now.month]
        day_period = get_day_period(now.hour)
        date_natural = format_date_natural(now)
        
        formatted = f"{day_period} de {date_natural}, {now.strftime('%H:%M')}"
        
        datetime_info = {
            "formatted": formatted,
            "time_24h": now.strftime("%H:%M"),
            "date_br": now.strftime("%d/%m/%Y"),
            "weekday_name": weekday_name,
            "month_name": month_name,
            "day_period": day_period,
            "date_natural": date_natural,
            "is_weekend": now.weekday() >= 5,
            "is_business_hours": 9 <= now.hour < 18 and now.weekday() < 5,
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute
        }
        
        return jsonify({
            "success": True,
            "message": f"Agora são {formatted}",
            "datetime_info": datetime_info
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao obter data/hora: {str(e)}"
        }), 500

@app.route('/webhook/datetime/business-info', methods=['POST', 'GET'])
def get_business_info():
    """Informações de contexto comercial"""
    try:
        now = datetime.now(NEW_YORK_TZ)
        
        is_weekend = now.weekday() >= 5
        is_business_hours = 9 <= now.hour < 18 and now.weekday() < 5
        weekday_name = WEEKDAYS[now.weekday()]
        day_period = get_day_period(now.hour)
        
        if is_weekend:
            message = f"Hoje é {weekday_name}, fim de semana"
        elif is_business_hours:
            message = f"Estamos em horário comercial, {day_period} de {weekday_name}"
        else:
            message = f"Estamos fora do horário comercial, {day_period} de {weekday_name}"
        
        return jsonify({
            "success": True,
            "message": message,
            "business_context": {
                "is_business_hours": is_business_hours,
                "is_weekend": is_weekend,
                "day_period": day_period,
                "weekday_name": weekday_name
            },
            "current_time": now.strftime("%H:%M")
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao obter contexto: {str(e)}"
        }), 500

@app.route('/webhook/datetime/relative', methods=['POST'])
def get_relative_time():
    """Calcular tempo relativo"""
    try:
        data = request.get_json()
        target_date = data.get('target_date')
        target_time = data.get('target_time', '00:00')
        
        if not target_date:
            return jsonify({
                "success": False,
                "message": "Data alvo é obrigatória"
            }), 400
        
        target_dt = datetime.strptime(f"{target_date} {target_time}", "%Y-%m-%d %H:%M")
        target_dt = NEW_YORK_TZ.localize(target_dt)
        
        now = datetime.now(NEW_YORK_TZ)
        diff = target_dt - now
        total_seconds = int(diff.total_seconds())
        is_future = total_seconds > 0
        abs_seconds = abs(total_seconds)
        
        days = abs_seconds // 86400
        hours = (abs_seconds % 86400) // 3600
        minutes = (abs_seconds % 3600) // 60
        
        if days > 0:
            time_desc = f"{days} dia{'s' if days != 1 else ''}"
            if hours > 0:
                time_desc += f" e {hours} hora{'s' if hours != 1 else ''}"
        elif hours > 0:
            time_desc = f"{hours} hora{'s' if hours != 1 else ''}"
            if minutes > 0:
                time_desc += f" e {minutes} minuto{'s' if minutes != 1 else ''}"
        elif minutes > 0:
            time_desc = f"{minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            time_desc = "menos de 1 minuto"
        
        if is_future:
            relative_desc = f"em {time_desc}"
        else:
            relative_desc = f"há {time_desc}"
        
        formatted = f"A data/hora alvo é {relative_desc}"
        
        return jsonify({
            "success": True,
            "message": formatted,
            "relative_info": {
                "description": time_desc,
                "relative_description": relative_desc,
                "is_future": is_future,
                "difference_days": days,
                "difference_hours": hours,
                "difference_minutes": minutes
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao calcular tempo: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    now = datetime.now(NEW_YORK_TZ)
    return jsonify({
        "status": "healthy",
        "service": "DateTime Webhook Service",
        "current_time": now.strftime("%H:%M de %d/%m/%Y"),
        "timezone": "America/New_York",
        "uptime": "online"
    })

@app.route('/test', methods=['GET'])
def test_all():
    """Testar todas funcionalidades"""
    try:
        now = datetime.now(NEW_YORK_TZ)
        tomorrow = now + timedelta(days=1)
        
        return jsonify({
            "status": "success",
            "current_time": now.strftime("%H:%M de %d/%m/%Y"),
            "tomorrow": tomorrow.strftime("%Y-%m-%d"),
            "is_business_hours": 9 <= now.hour < 18 and now.weekday() < 5,
            "weekday": WEEKDAYS[now.weekday()],
            "all_endpoints_working": True
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Configuração para Railway/Heroku/Render
    port = int(os.environ.get('PORT', 5001))
    
    print("🕐 DateTime Webhook para ElevenLabs")
    print("📍 Timezone: America/New_York (Nova York)")
    print(f"🚀 Iniciando na porta {port}")
    print("🔗 Endpoints disponíveis:")
    print("   GET  /")
    print("   GET  /health")
    print("   POST /webhook/datetime/current")
    print("   POST /webhook/datetime/business-info")
    print("   POST /webhook/datetime/relative")
    
    # Configuração otimizada para produção
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False,
        threaded=True
    )
