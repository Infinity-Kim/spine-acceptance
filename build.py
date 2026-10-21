"""Собирает index.html из src/template.html.

python3 build.py                      страница для GitHub Pages
python3 build.py --embed DIR out.html  локальная страница с уже загруженным экспортом из DIR
"""
import argparse
import base64
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).parent
CSS_URL = "https://unpkg.com/@esotericsoftware/spine-player@4.2.119/dist/spine-player.min.css"
CSS_CACHE = ROOT / ".cache" / "spine-player.min.css"

HEAD = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Превью и приёмка Spine-экспорта в браузере: проверки, профайлер, прогноз по устройствам.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%233a5bd9'/%3E%3Cpath d='M9 17l5 5 9-11' stroke='white' stroke-width='3.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>
"""


def player_css() -> str:
    if not CSS_CACHE.exists():
        CSS_CACHE.parent.mkdir(exist_ok=True)
        CSS_CACHE.write_bytes(urllib.request.urlopen(CSS_URL).read())
    return CSS_CACHE.read_text()


def embedded(src: pathlib.Path) -> str:
    files = [{"path": f"{src.name}/{p.relative_to(src)}", "b64": base64.b64encode(p.read_bytes()).decode()}
             for p in sorted(src.rglob("*")) if p.is_file()]
    return "window.EMBEDDED_FILES=" + json.dumps(files) + ";"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed", type=pathlib.Path)
    ap.add_argument("out", nargs="?", default=str(ROOT / "index.html"))
    a = ap.parse_args()
    t = (ROOT / "src" / "template.html").read_text()
    t = t.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    t = t.replace("/*SPINE_PLAYER_CSS*/", player_css())
    t = t.replace("/*EMBEDDED*/", embedded(a.embed) if a.embed else "")
    # title и стили шаблона уходят в head, разметка начинается с первого div
    head, body = t.split('<div class="wrap">', 1)
    pathlib.Path(a.out).write_text(HEAD + head + '</head>\n<body>\n<div class="wrap">' + body + "\n</body>\n</html>\n")


if __name__ == "__main__":
    main()
