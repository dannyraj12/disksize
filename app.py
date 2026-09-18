from fastapi import FastAPI
import os
import shutil

app = FastAPI(title="Blitz Storage Test")


@app.get("/")
def home():
    total, used, free = shutil.disk_usage("/")

    return {
        "status": "online",
        "disk": {
            "total_gib": round(total / 1024**3, 2),
            "used_gib": round(used / 1024**3, 2),
            "free_gib": round(free / 1024**3, 2),
        }
    }


@app.get("/mounts")
def mounts():
    with open("/proc/mounts", "r") as f:
        data = f.read()

    return {
        "mounts": data
    }


@app.get("/writable")
def writable():
    paths = [
        "/tmp",
        "/app",
        "/data",
        "/workspace",
        "/mnt",
    ]

    result = {}

    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)

            test_file = os.path.join(path, ".write_test")

            with open(test_file, "w") as f:
                f.write("test")

            os.remove(test_file)

            total, used, free = shutil.disk_usage(path)

            result[path] = {
                "status": "WRITABLE",
                "total_gib": round(total / 1024**3, 2),
                "used_gib": round(used / 1024**3, 2),
                "free_gib": round(free / 1024**3, 2),
            }

        except Exception as e:
            result[path] = {
                "status": "NOT WRITABLE",
                "error": str(e)
            }

    return result
