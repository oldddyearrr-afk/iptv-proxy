from flask import Flask, Response, request, stream_with_context
import requests
import re

app = Flask(__name__)

# قائمة القنوات - ضع روابطك هنا
CHANNELS = {
    "1001": "https://mn-nl.mncdn.com/utviraqi2/64c80359/index.m3u8",
    "1002": "http://thksmom.shop/IN_EN/index.m3u8?token=krikar",
    "1003": "http://2.57.214.72:2095/Arjc0WCSzNRt_180488/KILxRwQfON9tBs/418111?token=yHXUHH.X.y.X.ydHyzzfzHy.X.y.IQ.ts.21ad7b2f58ad4c016dbbdbbe596adbc69e11cce4b0546199b4bfd6d87b4716b5",
    # أضف المزيد...
}

# التوكنات المسموحة (اختياري - احذفها إذا تبي مفتوح)
VALID_TOKENS = [
    "ayhamaGGGGG.HAJRB",
    "token123",
    "freeaccess"
]

def proxy_stream(url):
    """
    يجلب البث من المصدر الأصلي ويخفيه
    """
    try:
        # Headers لتجنب الحظر
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.google.com/',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # اجلب البث
        resp = requests.get(url, stream=True, headers=headers, timeout=15)
        
        # تحديد نوع المحتوى
        content_type = resp.headers.get('Content-Type', 'application/octet-stream')
        
        # إذا كان m3u8، نعدل الروابط الداخلية
        if 'mpegurl' in content_type or url.endswith('.m3u8'):
            content = resp.content.decode('utf-8', errors='ignore')
            
            # استبدل الروابط المطلقة بروابط نسبية
            # هذا يخفي المصدر الأصلي
            base_url = '/'.join(url.split('/')[:-1])
            content = re.sub(
                r'(https?://[^\s]+)',
                lambda m: f"/proxy?url={m.group(1)}",
                content
            )
            
            return Response(
                content,
                content_type='application/vnd.apple.mpegurl',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                }
            )
        
        # للبث المباشر (ts, mp4, وغيرها)
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            stream_with_context(generate()),
            content_type=content_type,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Cache-Control': 'no-cache',
            }
        )
        
    except Exception as e:
        return Response(f"Stream Error: {str(e)}", status=500)


@app.route('/<username>/<password>/<channel_id>')
def stream(username, password, channel_id):
    """
    الصيغة: /user/pass/1001?token=xxx
    """
    # جيب التوكن
    token = request.args.get('token', '')
    
    # تحقق من التوكن (اختياري - احذف هذا القسم إذا تبي مفتوح)
    # if token not in VALID_TOKENS:
    #     return Response("Invalid token", status=403)
    
    # تحقق من القناة
    if channel_id not in CHANNELS:
        return Response("Channel not found", status=404)
    
    # جيب الرابط الأصلي
    original_url = CHANNELS[channel_id]
    
    # اعمل proxy وخفي المصدر
    return proxy_stream(original_url)


@app.route('/proxy')
def proxy():
    """
    Route إضافي لـ m3u8 segments
    يخفي الروابط الأصلية
    """
    url = request.args.get('url', '')
    if not url:
        return Response("Missing URL", status=400)
    
    return proxy_stream(url)


@app.route('/health')
def health():
    return "OK", 200


@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IPTV Proxy Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .success { color: #28a745; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            .example {
                background: #e9ecef;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ IPTV Proxy Server</h1>
            <p class="success"><strong>الخادم يعمل بنجاح!</strong></p>
            
            <h3>📺 صيغة الرابط:</h3>
            <div class="example">
                <code>/username/password/channel_id?token=your_token</code>
            </div>
            
            <h3>مثال:</h3>
            <div class="example">
                <code>/user/pass/1001?token=ayhamaGGGGG.HAJRB</code>
            </div>
            
            <h3>✨ المميزات:</h3>
            <ul>
                <li>✅ يدعم m3u8, ts, mp4, وجميع الصيغ</li>
                <li>✅ يخفي الرابط الأصلي</li>
                <li>✅ يعمل على جميع المشغلات</li>
                <li>✅ CORS مفعل</li>
            </ul>
        </div>
    </body>
    </html>
    """


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, threaded=True)
