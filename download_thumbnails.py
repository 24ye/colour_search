import requests
import os

API_KEY = "AIzaSyDyaZyOTm6ucVHaaQkS8INXdd5Xz_0fE4I"
PLAYLIST_ID = "PLKAp28rW2ifw30uU2XTILmuRFNGWswuoD"

os.makedirs("thumbnails", exist_ok=True)

url = "https://www.googleapis.com/youtube/v3/playlistItems"
params = {
    "part": "snippet",
    "playlistId": PLAYLIST_ID,
    "maxResults": 50,
    "key": API_KEY
}

nextPageToken = None
count = 0

while True:
    if nextPageToken:
        params["pageToken"] = nextPageToken

    response = requests.get(url, params=params)
    data = response.json()

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        title = snippet.get("title", "No Title")
        video_id = snippet.get("resourceId", {}).get("videoId")
        thumbnails = snippet.get("thumbnails", {})

        # Safe thumbnail selection: high → medium → default
        if "high" in thumbnails:
            thumbnail_url = thumbnails["high"]["url"]
        elif "medium" in thumbnails:
            thumbnail_url = thumbnails["medium"]["url"]
        elif "default" in thumbnails:
            thumbnail_url = thumbnails["default"]["url"]
        else:
            print(f"No thumbnail found for {title}")
            continue

        print(f"Downloading: {title}")
        img_data = requests.get(thumbnail_url).content
        with open(f"thumbnails/{video_id}.jpg", "wb") as f:
            f.write(img_data)

        count += 1

    nextPageToken = data.get("nextPageToken")
    if not nextPageToken:
        break

print(f"Done! Downloaded {count} thumbnails.")