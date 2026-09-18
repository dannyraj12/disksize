from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import shutil
import time
import requests

app = FastAPI(title="Blitz Remote Uploader Test")


class DownloadRequest(BaseModel):
    url: str


@app.get("/")
def home():
    total, used, free = shutil.disk_usage("/")
    
    return {
        "status": "online",
        "disk": {
            "total_gb": round(total / 1024**3, 2),
            "used_gb": round(used / 1024**3, 2),
            "free_gb": round(free / 1024**3, 2),
        }
    }


@app.get("/disk")
def disk():
    total, used, free = shutil.disk_usage("/")

    return {
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
        "total_gb": round(total / 1024**3, 2),
        "used_gb": round(used / 1024**3, 2),
        "free_gb": round(free / 1024**3, 2),
    }


@app.post("/test-download")
def test_download(data: DownloadRequest):

    filename = "/tmp/test_download.bin"

    try:
        start = time.time()

        with requests.get(
            data.url,
            stream=True,
            timeout=60,
            allow_redirects=True
        ) as r:

            r.raise_for_status()

            downloaded = 0

            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                    if not chunk:
                        continue

                    f.write(chunk)
                    downloaded += len(chunk)

        elapsed = time.time() - start

        total, used, free = shutil.disk_usage("/")

        return {
            "success": True,
            "downloaded_bytes": downloaded,
            "downloaded_gb": round(downloaded / 1024**3, 2),
            "seconds": round(elapsed, 2),
            "speed_mbps": round(
                downloaded / elapsed / 1024 / 1024,
                2
            ),
            "disk_after": {
                "total_gb": round(total / 1024**3, 2),
                "used_gb": round(used / 1024**3, 2),
                "free_gb": round(free / 1024**3, 2),
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if os.path.exists(filename):
            os.remove(filename)
