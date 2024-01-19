import os
import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    devPort = os.getenv("DEV_PORT")

    uvicorn.run("app.api:app", host="127.0.0.1",
                port=int(devPort), reload=True)
