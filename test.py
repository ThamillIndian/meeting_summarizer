import requests

url = "http://127.0.0.1:8000/process-audio/"
files = {
    "file": ("audio-sample-1.mp3", open("audio-sample-1.mp3", "rb")),
    "num_speakers": (None, "2")
}
response = requests.post(url, files=files)
print(response.json())