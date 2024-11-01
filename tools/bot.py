import requests
import json
import re
import os
import time
import subprocess
import sys


def get_video_length(file_path):
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        file_path
    ]

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.decode('utf-8')}")

    output = result.stdout.decode('utf-8')
    data = json.loads(output)

    duration = int(float(data['format']['duration']))
    return duration-1


def download_file(video_url: str, save_path: str):
    attempt = 0
    max_retries = 3
    while attempt < max_retries:
        attempt += 1
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            time.sleep(3)
    return False


if len(sys.argv) < 6:
    print("Usage: python test.py <username> <password> <course_id> <start_index> <end_index>")
    exit(1)

session = requests.Session()

session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    # Explicitly specify keep-alive (usually not necessary)
    'Connection': 'keep-alive',
    "Referer": f"http://school.huadianline.com/course/{sys.argv[3]}.html"
})

url = 'http://school.huadianline.com/index.php?app=basic&mod=Passport&act=ajaxLogin'

# login
res = session.post(
    url, data={'log_username': sys.argv[1], 'log_pwd': sys.argv[2]})

if res.status_code == 200:
    print("Login successful")


pat = r'<source[^>]*\sid=["\']videoType["\'][^>]*\ssrc=["\']([^"\']+)["\']'

# for idx in range(14597, 14725):
for idx in range(int(sys.argv[4]), int(sys.argv[5])):
    fna = f"{sys.argv[3]}_{idx}"
    url = f"http://school.huadianline.com/course/watch/{sys.argv[3]}_{idx}.html"
    res = session.get(url)
    if res.status_code != 200:
        print(f"Failed to get {fna}")
        continue

    with open(f"{fna}.html", "w", encoding="utf-8") as f:
        f.write(res.text)

    matches = re.findall(pat, res.text)
    if not matches:
        print(f"No matches found for {fna}")
        continue
    print(matches[0])
    t = 0
    if os.path.basename(matches[0]).split(".")[-1].lower() == "mp4":
        print("download mp4")
        download_file(matches[0], f"{fna}.mp4")
        t = get_video_length(f"{fna}.mp4")
        t = int(t)
        print(t)
    else:
        res = session.get(matches[0])
        with open(f"{fna}.m3u8", "w") as f:
            f.write(res.text)
        for line in res.text.splitlines():
            if line.startswith("#EXTINF"):
                duration = float(
                    re.search(r'#EXTINF:([\d\.]+),', line).group(1))
                t += duration

    url = "http://school.huadianline.com/index.php?app=course&mod=Video&act=updateLearn"
    session.headers.update({
        "Referer": url
    })
    print(f"will post index {idx}, length {t}")
    res = session.post(url, data={
        "time": t,
        "player_seek_time": t,
        "vid": int(sys.argv[3]),
        "sid": idx,
        "totaltime": t,
        "is_true": 1,
        "type": 1
    })
    print(res.status_code)
    if res.status_code != 200:
        continue
