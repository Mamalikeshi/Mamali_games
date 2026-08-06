from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Mamali Games")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Mamali Games</title>
        </head>
        <body style="font-family:Tahoma;text-align:center;padding-top:80px;">
            <h1>🎮 Mamali Games</h1>
            <h2>پروژه با موفقیت شروع شد.</h2>
            <p>فعلاً فقط تست اولیه است.</p>
        </body>
    </html>
    """
