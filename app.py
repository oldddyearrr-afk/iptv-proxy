from flask import Flask, redirect, request, Response
import requests

app = Flask(__name__)

# قائمة القنوات - استبدلها بقنواتك المجانية
CHANNELS = {
    "318197": "https://mn-nl.mncdn.com/utviraqi2/64c80359/index.m3u8",
    "358222": "https://zindisorani.zaroktv.com.tr/hls/stream.m3u8",
    "433740": "https://ghaasiflu.online/Dijlah/index.m3u8",
    "1001": "https://live.channel8.com/Channel8-Kurdish/index.fmp4.m3u8",
    "1002": "https://mn-nl.mncdn.com/utviraqi2/64c80359/index.m3u8",
}

# الروت الرئيسي - نفس الصيغة اللي تبيها
@app.route('/<username>/<password>/<channel_id>')
def stream(username, password, channel_id):
    """
    الرابط: /Arjc0WCSzNRt_180488/KILxRwQfON9tBs/318197?token=xxx
    username = Arjc0WCSzNRt_180488
    password = KILxRwQfON9tBs
    channel_id = 318197
    """
    
    # جيب التوكن (اختياري)
    token = request.args.get('token', '')
    
    # تحقق من القناة
    if channel_id not in CHANNELS:
        return "Channel not found", 404
    
    # جيب رابط القناة الأصلي
    original_url = CHANNELS[channel_id]
    
    # اعمل proxy للبث
    try:
        resp = requests.get(original_url, stream=True, timeout=10)
        
        # ارجع البث مع الـ headers الصحيحة
        return Response(
            resp.iter_content(chunk_size=1024),
            content_type=resp.headers.get('Content-Type', 'video/mp2t'),
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Cache-Control': 'no-cache',
            }
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

# Health check
@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def index():
    return """
    <h1>IPTV Proxy Server</h1>
    <p>الخادم يعمل بنجاح! ✅</p>
    <p>استخدم الصيغة: /username/password/channel_id?token=xxx</p>
    """

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, threaded=True)
