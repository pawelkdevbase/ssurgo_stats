import os
import requests
import lxml.html as lx
import json

from config import DOWNLOAD_FOLDER


session = requests.Session()


def from_json(data: dict) -> list:
    zip_files: list = []
    items = data["/app-api/enduserapp/shared-folder"]["items"]
    for i in items:
        if i["type"] != "file":
            continue
        zip_files.append([i["name"], i["typedID"]])
    return zip_files


def json_with_files(pg: int) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) "
        "Gecko/20100101 Firefox/101.0"
    }
    # TODO: Before run check if this is valid path - from time time this is
    # changed on server
    list_url = 'https://nrcs.app.box.com/v/soils/folder/180112652169?page={}'

    r = session.get(list_url.format(pg), headers=headers)
    html = lx.fromstring(r.text)
    scripts = html.xpath(".//script")
    for script in scripts:
        try:
            script_text: str = script.xpath("./text()")[0].strip()
        except IndexError:
            continue
        if script_text.startswith("Box.postStreamData ="):
            return str2json(script_text)
    return dict()


def str2json(text: str) -> dict:
    text = "=".join(text.split("=")[1:]).strip().rstrip(";")
    js: dict = json.loads(text)
    return js


def download_file(fl_tab: list) -> bool:
    flname = fl_tab[0]
    flurl = fl_tab[1]

    if not os.path.isdir(os.path.join(os.path.dirname(__file__),
                                      DOWNLOAD_FOLDER)):
        os.mkdir(os.path.join(os.path.dirname(__file__), DOWNLOAD_FOLDER))

    file_path = os.path.join(
        os.path.dirname(__file__), DOWNLOAD_FOLDER, flname
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) "
        "Gecko/20100101 Firefox/101.0"
    }
    url = "https://nrcs.app.box.com/index.php" + \
        f"?rm=box_download_shared_file&vanity_name=soils&file_id={flurl}"

    with session.get(url,
                     headers=headers,
                     allow_redirects=True,
                     stream=True,) as r:
        r.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return True


if __name__ == '__main__':
    pcnt = 1  # page counter
    fls = []  # list with all files

    while True:
        dwn = json_with_files(pcnt)
        pcnt += 1
        fljs = from_json(dwn)
        if len(fljs) == 0:
            break
        fls += fljs

    for dw in fls:
        print(f'Downloading {dw[0]}')
        download_file(dw)
