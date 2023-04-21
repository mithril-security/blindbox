import requests

res = requests.post(
    "https://nitro.mithrilsecurity.io/whisper/predict",
    files={
        "audio": open("test2.wav", "rb"),
    },
).text

print(res)
