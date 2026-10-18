"""Build short README motion explainers from existing, verified paper artifacts.

python scripts/reading_motion.py
Requires requirements.txt + requirements-showcase.txt. No model or video service.
These are animated explanations, not screen recordings or live generation demos.
"""
import hashlib
import io
import json
from functools import lru_cache
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "examples/waypoint-opd/showcase"
LOCAL = ROOT / "local/motion"
FONT = ROOT / "assets/NotoSansCJKsc-Regular.otf"
BG, INK, MUTED, LINE, BLUE = "#f4f3ef", "#20282c", "#606b70", "#cdd1d1", "#3d6278"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=40)
def font(size):
    return ImageFont.truetype(str(FONT), size)


def write(im, xy, value, size, fill=INK, max_width=None):
    """Wrap display labels; record an error instead of silently clipping text."""
    draw = ImageDraw.Draw(im)
    available = max_width or im.width - xy[0] - 40
    rows = []
    for paragraph in value.split("\n"):
        row = ""
        for char in paragraph:
            if row and draw.textlength(row + char, font=font(size)) > available:
                rows.append(row.rstrip())
                row = char.lstrip()
            else:
                row += char
        rows.append(row)
    for i, row in enumerate(rows):
        point = (xy[0], xy[1] + i * round(size * 1.4))
        draw.text(point, row, font=font(size), fill=fill, anchor="lt")
        box = draw.textbbox(point, row, font=font(size), anchor="lt")
        if box[2] > im.width - 24 or box[3] > im.height - 24:
            raise ValueError("Motion label overflow: " + value)
    return xy[1] + len(rows) * round(size * 1.4)


def paper_crop(doc, page, rect, width, log):
    rect = fitz.Rect(rect)
    assert doc[page].rect.contains(rect)
    pix = doc[page].get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect, alpha=False)
    crop = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    crop = crop.resize((width, round(crop.height * width / crop.width)), Image.Resampling.LANCZOS)
    log.append({"physical_page": page + 1, "rect_pt": list(rect), "width_px": width})
    return crop


def paste(im, crop, xy):
    assert xy[0] >= 0 and xy[1] >= 0
    assert xy[0] + crop.width <= im.width and xy[1] + crop.height < im.height - 80
    im.paste(crop, xy)


def base(mobile, number, title, step, labels):
    w, h = (780, 1000) if mobile else (1200, 740)
    im = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(im)
    write(im, (40, 30), "SOURCE ANNOTATIONS  /  " + number, 24 if mobile else 20, BLUE)
    write(im, (40, 84), title, 42 if mobile else 43)
    y = 192 if mobile else 170
    unit = (w - 80) / 3
    for i, label in enumerate(labels):
        x = round(40 + i * unit)
        draw.line((x, y, x + unit - 14, y), fill=BLUE if i <= step else LINE, width=3)
        write(im, (x, y + 15), label, 28 if mobile else 24, BLUE if i == step else MUTED,
              max_width=unit - 15)
    draw.rectangle((40, y + 76, w - 40, h - 122), fill="white", outline=LINE)
    write(im, (40, h - 78), "真实内容的动作示意 · 非录屏", 24 if mobile else 19, MUTED)
    return im, y + 100


def pointer(im, point, clicked=False):
    im = im.copy()
    draw = ImageDraw.Draw(im)
    x, y = point
    if clicked:
        draw.ellipse((x-23, y-23, x+23, y+23), outline=BLUE, width=3)
    draw.polygon([(x, y), (x+4, y+32), (x+13, y+24), (x+25, y+24)], fill=INK)
    return im


def sequence(states, click=None):
    frames, durations = [], []
    def add(im, ms):
        frames.append(im)
        durations.append(ms)
    add(states[0], 2600)
    for i in range(1, len(states)):
        if click and i == 2:
            start, end = click
            for n in range(1, 13):
                t = n / 12
                t = t * t * (3 - 2*t)
                add(pointer(states[i-1], (start[0]+(end[0]-start[0])*t,
                                          start[1]+(end[1]-start[1])*t)), 60)
            add(pointer(states[i-1], end, True), 500)
        for n in range(1, 7):
            add(Image.blend(states[i-1], states[i], n / 6), 80)
        add(states[i], 3300 if i == 1 else 5000)
    return frames, durations


def concept(data, original, doc, mobile, log):
    states = []
    labels = ["论文标题", "中文主线", "核心观点"]
    for step in range(3):
        im, top = base(mobile, "01", "长标题，展开为阅读主线", step, labels)
        w = im.width
        size = 34 if mobile else 29
        if step == 0:
            write(im, (64, top), "从一篇真实论文开始", size, BLUE)
            clip = paper_crop(original, 0, [105, 77, 510, 121], w-128, log)
            paste(im, clip, (64, top+80))
            write(im, (64, top+clip.height+133), "标题给出研究对象；导览进一步说明它想解决什么问题。",
                  size, max_width=w-128)
        elif step == 1:
            write(im, (64, top), "导览先把问题讲清楚", size, BLUE)
            end = write(im, (64, top+78), data["reading_guide"]["headline"].replace("\n", ""),
                        42 if mobile else 39, max_width=w-128)
            write(im, (64, end+40), data["reading_guide"]["problem"], size, max_width=w-128)
        else:
            write(im, (64, top), "核心观点 · 按屏宽重排", size, BLUE)
            end = write(im, (64, top+76), data["reading_guide"]["core_view"], size, max_width=w-128)
            write(im, (64, end+40), "问题 → 方法 → 发现与边界", size, BLUE, max_width=w-128)
        states.append(im)
    return states, None


def background(data, original, doc, mobile, log):
    uri = data["background"]["links"][0]["url"]
    link = next(l for l in doc[0].get_links() if l.get("uri") == uri)
    labels = ["遇到概念", "导览入口", "打开资料"]
    states = []
    for step in range(3):
        im, top = base(mobile, "02", "不懂背景，就沿入口补上", step, labels)
        w = im.width
        size = 34 if mobile else 29
        if step == 0:
            write(im, (64, top), "先修知识 / 本文语境", size, BLUE)
            end = write(im, (64, top+83), data["reading_guide"]["prerequisites"][0], size+3,
                        max_width=w-128)
            write(im, (64, end+40), "概念仍不熟悉？导览保留了继续阅读的资料入口。", size,
                  max_width=w-128)
        elif step == 1:
            write(im, (64, top), "导览中的三个真实链接", size, BLUE)
            rect = fitz.Rect(105, 276.35, 316, 314)
            crop_width = w-128 if mobile else 740
            crop = paper_crop(doc, 0, rect, crop_width, log)
            paste(im, crop, (64, top+85))
            scale = crop_width / rect.width
            box = link["from"]
            point = (64+(box.x0+40-rect.x0)*scale, top+85+(box.y0+6-rect.y0)*scale)
            write(im, (64, top+crop.height+123), "选择 Policy / RL 入门", size, BLUE,
                  max_width=w-128)
        else:
            write(im, (64, top), "目标资料 · 内容摘记", size, BLUE)
            end = write(im, (64, top+72), "Spinning Up / Policies", 40 if mobile else 38,
                        max_width=w-128)
            end = write(im, (64, end+20), "策略是一条规则：帮助智能体决定采取什么行动。", size,
                        max_width=w-128)
            end = write(im, (64, end+24), "spinningup.openai.com\nrl_intro.html#policies", 27 if mobile else 25,
                        BLUE, max_width=w-128)
            write(im, (64, end+28), "从原链接进入这一节，再回论文继续读。", size,
                  max_width=w-128)
        states.append(im)
    return states, ((im.width-100, im.height-170), point)


def evidence(data, original, doc, mobile, log):
    note = next(a for a in data["annotations"] if a["id"] == "a12")
    report = json.loads((ROOT/"output/waypoint-opd-v1-annotated.report.json").read_text(encoding="utf-8"))
    target = next(l for l in report["guide_links"] if l["label"] == "第4页 · 正确性限制")
    goto = next(l for l in doc[0].get_links() if l["kind"] == fitz.LINK_GOTO
                and l["page"]+1 == target["output_page"] and abs(l["to"].y-target["point"][1]) < .02)
    annotation = next(a for a in report["annotations"] if a["id"] == "a12")
    assert abs(annotation["source_boxes"][0][1]-goto["to"].y) < .02
    assert abs(annotation["source_boxes"][0][0]-goto["to"].x) < .02
    assert note["quote"] in " ".join(doc[goto["page"]].get_text().split())
    labels = ["导览判断", "点击入口", "原文依据"]
    states = []
    for step in range(3):
        im, top = base(mobile, "03", "从一句判断，回到证据现场", step, labels)
        w = im.width
        size = 34 if mobile else 29
        if step == 0:
            write(im, (64, top), "阅读路径 / 边界", size, BLUE)
            end = write(im, (64, top+86), data["reading_guide"]["steps"][-1]["title"].split("：", 1)[1],
                        42 if mobile else 39, max_width=w-128)
            write(im, (64, end+40), "这句话不是阅读的终点。继续看作者在哪里写下了限制。", size,
                  max_width=w-128)
        elif step == 1:
            write(im, (64, top), "PDF 内部入口 / 原论文第 4 页", size, BLUE)
            rect = fitz.Rect(105, 522, 375, 570)
            crop_width = w-128
            crop = paper_crop(doc, 0, rect, crop_width, log)
            paste(im, crop, (64, top+85))
            scale = crop_width/rect.width
            point = (64+(goto["from"].x0+50-rect.x0)*scale,
                     top+85+(goto["from"].y0+6-rect.y0)*scale)
            write(im, (64, top+crop.height+100), "点击“正确性限制”，定位到对应原句。", size,
                  max_width=w-128)
        else:
            write(im, (64, top), "原论文第 4 页 / 作者的限制", size, BLUE)
            crop = paper_crop(doc, goto["page"], [144.2, 595.5, 428, 610.8], w-128, log)
            paste(im, crop, (64, top+80))
            end = write(im, (64, top+crop.height+119), "【作者主张】" + note["text"], size,
                        max_width=w-128)
            write(im, (64, end+35), "再读上下文，检查假设、实验与结论边界。", size,
                  max_width=w-128)
        states.append(im)
    return states, ((im.width-100, im.height-170), point)


def main():
    data_path = ROOT/"examples/waypoint-opd/annotations.json"
    source = ROOT/"local/waypoint-opd-v1.pdf"
    annotated = ROOT/"output/waypoint-opd-v1-annotated.pdf"
    report_path = annotated.with_suffix(".report.json")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert sha(source) == data["paper"]["sha256"]
    assert sha(annotated) == report["output_sha256"]
    assert sha(data_path) == report["annotations_sha256"]
    before = {str(p.relative_to(ROOT)): sha(p) for p in (source, annotated, data_path, report_path)}
    DEST.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    manifest = {"kind": "Animated explanation, not a screen recording or live generation",
                "inputs": before, "paper": data["paper"]["url"], "paper_license": "CC BY 4.0",
                "background_target": data["background"]["links"][0],
                "background_note": "Chinese paraphrase of Spinning Up Policies opening definition; not a website screenshot.",
                "navigation": {"annotation": "a12", "original_page": 4, "physical_page": 5},
                "outputs": {}}
    with fitz.open(source) as original, fitz.open(annotated) as doc:
        for name, builder in [("concept", concept), ("background", background), ("evidence", evidence)]:
            for mobile in (False, True):
                suffix = "-mobile" if mobile else ""
                stem = f"motion-{name}{suffix}"
                log = []
                states, click = builder(data, original, doc, mobile, log)
                frames, durations = sequence(states, click)
                # A shared palette avoids flashing on crossfades; no dither keeps CJK edges clean.
                atlas = Image.new("RGB", (states[0].width, states[0].height*3))
                for i, frame in enumerate(states): atlas.paste(frame, (0, i*frame.height))
                palette = atlas.quantize(colors=128, dither=Image.Dither.NONE)
                indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
                path = DEST/(stem+".gif")
                indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=durations,
                                loop=0, optimize=True, disposal=1)
                poster = DEST/(stem+"-still.png")
                states[-1].save(poster, optimize=True)
                contact = Image.new("RGB", (states[0].width*3, states[0].height))
                for i, frame in enumerate(states): contact.paste(frame, (i*frame.width, 0))
                contact.thumbnail((1800, 1000))
                contact.save(LOCAL/(stem+"-stages.png"))
                with Image.open(path) as gif:
                    measured = sum(gif.seek(i) or gif.info.get("duration", 0) for i in range(gif.n_frames))
                    assert measured == sum(durations)
                    assert gif.info["loop"] == 0
                    assert path.stat().st_size < 4_000_000, "Keep README animations small"
                    manifest["outputs"][path.name] = {"size": list(gif.size), "frames": gif.n_frames,
                        "duration_ms": measured, "bytes": path.stat().st_size, "sha256": sha(path),
                        "crops": log, "poster": {"file": poster.name, "sha256": sha(poster)}}
                print(path.name, path.stat().st_size, "bytes", measured, "ms")
    assert before == {str(p.relative_to(ROOT)): sha(p) for p in (source, annotated, data_path, report_path)}
    (DEST/"motion-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
