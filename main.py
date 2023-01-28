import re
import requests
import ffmpeg
import sys
import json
import base64

regex_json = r"var episodes = (.*)"
regex_playlist = r"\"([a-zA-Z-0-9=]{25,})\""
regex_pstream = r"https:\/\/www\.pstream.[^';]*"
regex_player = r"https:\/\/www\.pstream\.net\/u.[^\"]*"
regex_stream_1080 = r"(https:\/\/www\.pstream\.net\/h\/1080.*)$"
regex_stream_720 = r"(https:\/\/www\.pstream\.net\/h\/720.*)$"
regex_stream_480 = r"(https:\/\/www\.pstream\.net\/h\/480.*)$"

base_url = "https://neko-sama.fr"

headers = {"Referer": "https://www.google.com",
           "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/81.0",
           "DNT": "1",
           "Connection": "keep-alive",
           "Upgrade-Insecure-Requests": "1",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
           "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
           "Accept-Encoding": "gzip, deflate, br"}

s = requests.Session()
s.headers = headers


def convert_pl(pl_url, filename):
    with open("tmp.m3u", "w") as f:
        f.write(s.get(pl_url).text)

    print(filename)
    ffmpeg.input("tmp.m3u", protocol_whitelist="file,http,https,tcp,tls,crypto").output(
        filename, acodec="copy", vcodec="copy").run()
    return


def get_episode_chunks(url):
    src = s.get(url).text
    ret = re.findall(regex_pstream, src, re.M)
    src = s.get(ret[0]).text
    ret = re.findall(regex_player, src, re.M)
    src = s.get(ret[0]).text
    ret = re.findall(regex_playlist, src, re.M)
    dec = base64.b64decode(ret[0])[2:].decode()
    playlist_url = json.loads(dec)["mmmmmmmmmmmmmmmmmmmm"]
    m3u = s.get(playlist_url).text

    pl = re.findall(regex_stream_1080, m3u, re.M)
    if pl:
        return pl[0]

    pl = re.findall(regex_stream_720, m3u, re.M)
    if pl:
        return pl[0]

    pl = re.findall(regex_stream_480, m3u, re.M)
    if pl:
        return pl[0]

    return None


def main():
    src = s.get(sys.argv[1]).text
    ret = re.findall(regex_json, src, re.M)
    ep_list = json.loads(ret[0][:-1])

    if len(ep_list) > 99:
        pad = 3
    else:
        pad = 2

    nb = 1

    with open("log.txt", "w") as log:
        for ep in ep_list:
            pl = get_episode_chunks(base_url + ep["url"])

            if pl is None:
                log.write(ep["url"] + " stream not found\n")
                print(ep["url"] + " stream not found")

            else:
                convert_pl(pl, sys.argv[2] + " " + str(nb).zfill(pad)+".mp4")
                nb += 1

    return


if __name__ == "__main__":
    main()
