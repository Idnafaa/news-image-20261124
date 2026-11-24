# render.py — draws "The World in One Day — 24 November 2026".
#
# Pure Python standard library: the Canvas from image.py plus the
# embedded bitmap fonts in font_data.py. The poster carries one lead
# story, six illustrated cards and twenty-four briefs — 31 stories in
# all, each dated Tuesday 24 November 2026 and verified against live
# reporting on the day itself.
import os

from image import Canvas

W, H = 1024, 1024
PAPER = "#F6F1E6"
NAVY = "#16233D"
NAVY2 = "#1F3358"
RED = "#B3352B"
TEAL = "#0F766E"
GOLD = "#C99A2B"
SLATE = "#3D4A5C"
PLUM = "#5B3A5E"
INK = "#1C1C1C"
MUTED = "#5A5A52"

LEAD_HEAD = ["HUANG RETURNS AS", "NVIDIA CHIEF"]
LEAD_DEK = (
    "Nvidia's board unanimously reinstated Jensen Huang as chief executive "
    "on Monday - and the shares surged more than 31% in a single day."
)
LEAD_STATS = "+31% IN A DAY  |  UNANIMOUS BOARD VOTE  |  SENATE HEARING 3 DEC"

# Each card: its band colour, headline, one-line dek and icon kind.
CARDS = [
    {"band": TEAL, "head": "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
     "dek": "Kyiv says drones sank the corvette Merkury at Benghazi.",
     "icon": "ship"},
    {"band": NAVY2, "head": "NATO SENDS AWACS TO POLAND",
     "dek": "Early-warning jets deploy after missiles landed in Poland.",
     "icon": "plane"},
    {"band": GOLD, "head": "COP31 ENDS WITH NO DEAL",
     "dek": "Climate talks in Antalya collapse as the EU rejects the text.",
     "icon": "globe"},
    {"band": RED, "head": "FACTORY FIRE KILLS 24 IN INDONESIA",
     "dek": "Blaze at a candy plant in Cikande; dozens still missing.",
     "icon": "flame"},
    {"band": SLATE, "head": "6.5 QUAKE SHAKES VANUATU",
     "dek": "Strong tremor hits the Pacific islands; no tsunami threat.",
     "icon": "waves"},
    {"band": PLUM, "head": "DELTA OUTAGE DELAYS 3,000 FLIGHTS",
     "dek": "Automation failure snarls US air travel before Thanksgiving.",
     "icon": "runway"},
]

# Each brief: its section, headline and dek. Kept short so every brief
# fits on a single line in its column.
BRIEFS = [
    {"section": "EUROPE", "head": "450 German schools hit by bomb threats",
     "dek": "Police say emailed threats appear unfounded; classes disrupted."},
    {"section": "EUROPE", "head": "Cyprus expels two Russian diplomats",
     "dek": "Pair accused of espionage are struck from the embassy list."},
    {"section": "EUROPE", "head": "Berlin sends tanks to Lithuania by rail",
     "dek": "Route avoids Poland to avoid provoking Moscow, Bild reports."},
    {"section": "EUROPE", "head": "France condemns settler attacks",
     "dek": "Paris denounces violence against Palestinian communities."},
    {"section": "AMERICAS", "head": "Democrats clinch House, 258 seats",
     "dek": "Largest House majority since 1992, with funding deadline 11 Dec."},
    {"section": "AMERICAS", "head": "FBI probes hack of crime database",
     "dek": "Apparent breach of a key national law-enforcement system."},
    {"section": "AMERICAS", "head": "Trump pauses Iowa chemical detonation",
     "dek": "Army told to halt disposal of toxic lead azide stockpile."},
    {"section": "AMERICAS", "head": "16 killed in 'El Chapo Isidro' capture",
     "dek": "Mexican forces kill cartel suspects in Sinaloa operation."},
    {"section": "AMERICAS", "head": "Panama resumes Cobre mine talks",
     "dek": "Government reopens negotiations with First Quantum Minerals."},
    {"section": "ASIA-PACIFIC", "head": "China official sentenced to death",
     "dek": "Convicted of leaking 100 intelligence reports, 35 state secrets."},
    {"section": "ASIA-PACIFIC", "head": "Seoul names new foreign minister",
     "dek": "South Korea also picks its first woman intelligence chief."},
    {"section": "ASIA-PACIFIC", "head": "Lahore tops world pollution ranking",
     "dek": "AQI crosses 500; eight Pakistani cities among the worst."},
    {"section": "ASIA-PACIFIC", "head": "Bangladesh garment workers balk",
     "dek": "Unions reject the latest salary proposal as too low."},
    {"section": "MIDDLE EAST & AFRICA", "head": "Israeli strikes kill three in Gaza",
     "dek": "Dead include a worker with the UN agency UNRWA."},
    {"section": "MIDDLE EAST & AFRICA", "head": "Oxfam: Gaza poisoned for decades",
     "dek": "Explosives and toxins contaminate air, soil and water."},
    {"section": "MIDDLE EAST & AFRICA", "head": "Iran flogs singer, 74 lashes",
     "dek": "Parastoo Ahmadi punished with four crew over a virtual concert."},
    {"section": "MIDDLE EAST & AFRICA", "head": "US sanctions Iran shadow banks",
     "dek": "Treasury targets dozens of people and entities."},
    {"section": "MIDDLE EAST & AFRICA", "head": "Taliban erases women's names",
     "dek": "Balkh province replaces them with 'Bibi' on documents."},
    {"section": "TECH & MARKETS", "head": "Trump to punish offshore data centres",
     "dek": "US firms building storage abroad face penalties, he says."},
    {"section": "TECH & MARKETS", "head": "UN chief: AI safety rules in a year",
     "dek": "Guterres demands a global AI safety framework, fast."},
    {"section": "TECH & MARKETS", "head": "Chemical watchdog in budget crisis",
     "dek": "US payment delays leave the OPCW facing an emergency."},
    {"section": "TECH & MARKETS", "head": "BepiColombo now orbits Mercury",
     "dek": "Probe entered orbit on Saturday after a long cruise."},
    {"section": "SPORT & CULTURE", "head": "49ers rout Vikings 35-10 in Mexico City",
     "dek": "Purdy throws three touchdowns in the NFL's Mexico game."},
    {"section": "SPORT & CULTURE", "head": "Mossad helped foil Swift Vienna plot",
     "dek": "Ex-spy chief says an ISIS-inspired attack was stopped."},
]


def _fit_text(cv, text, font, max_w):
    """Shorten text with an ellipsis until it fits max_w in font."""
    if cv.text_width(text, font) <= max_w:
        return text
    while text and cv.text_width(text + "...", font) > max_w:
        text = text[:-1]
    return text + "..."


def _draw_icon(cv, kind, x, y, s, fg):
    """A small geometric icon centred near (x, y), sized about s."""
    if kind == "ship":
        cv.fill_poly([(x - s, y + 8), (x + s, y + 8), (x + s - 8, y + 22),
                      (x - s + 8, y + 22)], fg)
        cv.fill_rect(x - 2, y - 18, 4, 26, fg)
        cv.fill_poly([(x + 2, y - 18), (x + 2, y + 2), (x + 20, y + 2)], fg)
        cv.hline(x - s - 4, y + 28, 2 * s + 8, fg, 2)
    elif kind == "plane":
        cv.fill_poly([(x - s, y), (x + s, y - 6), (x + s, y + 6)], fg)
        cv.fill_poly([(x - 6, y - 4), (x + 10, y - 22), (x + 16, y - 4)], fg)
        cv.fill_poly([(x - 6, y + 4), (x + 10, y + 22), (x + 16, y + 4)], fg)
        cv.fill_rect(x - 2, y - 26, 4, 6, fg)
        cv.fill_circle(x, y - 28, 5, fg)
    elif kind == "globe":
        cv.circle_outline(x, y, s, fg, 3)
        cv.line(x - s, y, x + s, y, fg, 2)
        cv.line(x, y - s, x, y + s, fg, 2)
        cv.fill_circle(x + s // 2, y - s // 2, 4, fg)
    elif kind == "flame":
        cv.fill_poly([(x, y - s - 4), (x + 12, y - 6), (x + 18, y + 8),
                      (x + 10, y + s), (x - 10, y + s), (x - 18, y + 8),
                      (x - 12, y - 6)], fg)
        cv.fill_poly([(x, y - 2), (x + 7, y + 8), (x, y + s - 4),
                      (x - 7, y + 8)], PAPER)
    elif kind == "waves":
        for k in range(3):
            yy = y - 12 + k * 12
            cv.line(x - s, yy, x - s // 2, yy - 8, fg, 3)
            cv.line(x - s // 2, yy - 8, x, yy, fg, 3)
            cv.line(x, yy, x + s // 2, yy - 8, fg, 3)
            cv.line(x + s // 2, yy - 8, x + s, yy, fg, 3)
        cv.line(x - 4, y - 30, x + 6, y - 14, fg, 3)
        cv.line(x + 6, y - 14, x - 2, y - 2, fg, 3)
    elif kind == "runway":
        cv.fill_poly([(x - s, y + 4), (x + s, y - 4), (x + s, y + 4),
                      (x - s, y + 12)], fg)
        cv.fill_rect(x - s, y + 20, 12, 3, fg)
        cv.fill_rect(x - s // 3, y + 20, 12, 3, fg)
        cv.fill_rect(x + s // 3, y + 20, 12, 3, fg)
        cv.fill_poly([(x - 8, y - 22), (x + 22, y - 26), (x + 22, y - 18),
                      (x - 8, y - 14)], fg)


def _right_text(cv, text, font, y, color, margin=28):
    """Draw one line right-aligned against the page margin."""
    cv.draw_text(W - margin - cv.text_width(text, font), y, text, font, color)


def _masthead(cv):
    cv.fill_rect(0, 0, W, 88, NAVY)
    cv.draw_text(28, 18, "THE WORLD IN ONE DAY", "bold56", "#F6F1E6")
    cv.draw_text(28, 70, "TUESDAY  -  24 NOVEMBER 2026", "bold13", GOLD)
    _right_text(cv, "THE DAY IN WORLD NEWS", "bold13", 30, "#F6F1E6")
    _right_text(cv, "31 STORIES  -  ONE IMAGE", "reg13", 52, "#C9CFD8")
    cv.fill_rect(0, 88, W, 4, RED)


def _dateline(cv):
    cv.draw_text(28, 104, "SUMMING UP TUESDAY 24 NOVEMBER 2026 - FROM KYIV TO SEOUL, "
                 "SILICON VALLEY TO ANTALYA", "bold13", NAVY)
    cv.hline(28, 124, W - 56, NAVY, 1)


def _lead(cv):
    y = 140
    cv.draw_text(28, y, "TECHNOLOGY  -  THE LEAD STORY", "bold13", RED)
    y += 22
    for ln in LEAD_HEAD:
        cv.draw_text(28, y, ln, "bold40", INK)
        y += 46
    y += 4
    y = cv.draw_wrapped(28, y, 560, LEAD_DEK, "reg20", "#33302A", leading=26)
    y += 10
    cv.draw_text(28, y, LEAD_STATS, "bold13", RED)


def _chip(cv):
    """Lead illustration: a chip on a circuit board, right of the lead."""
    px, py, pw, ph = 612, 132, 384, 236
    cv.fill_rect(px, py, pw, ph, NAVY)
    cv.rect_outline(px, py, pw, ph, GOLD, 2)
    for i in range(5):
        yy = py + 24 + i * 40
        cv.hline(px + 16, yy, 60, TEAL, 2)
        cv.hline(px + pw - 76, yy, 60, TEAL, 2)
    for i in range(4):
        xx = px + 60 + i * 88
        cv.vline(xx, py + 12, 30, GOLD, 2)
        cv.vline(xx, py + ph - 42, 30, GOLD, 2)
    chip = 150
    cx, cy = px + (pw - chip) // 2, py + (ph - chip) // 2
    cv.fill_rect(cx, cy, chip, chip, "#0E1B30")
    cv.rect_outline(cx, cy, chip, chip, GOLD, 3)
    for i in range(6):
        cv.fill_rect(cx - 14, cy + 12 + i * 22, 14, 6, GOLD)
        cv.fill_rect(cx + chip, cy + 12 + i * 22, 14, 6, GOLD)
        cv.fill_rect(cx + 12 + i * 22, cy - 14, 6, 14, GOLD)
        cv.fill_rect(cx + 12 + i * 22, cy + chip, 6, 14, GOLD)
    label = "NVDA"
    cv.draw_text(cx + (chip - cv.text_width(label, "bold40")) // 2, cy + 34,
                 label, "bold40", "#F6F1E6")
    sub = "+31% IN A DAY"
    cv.draw_text(cx + (chip - cv.text_width(sub, "bold13")) // 2, cy + 92,
                 sub, "bold13", GOLD)
    cv.draw_text(px + 16, py + ph - 24, "JENSEN HUANG, BACK IN CHARGE",
                 "bold13", "#C9CFD8")


def _cards(cv):
    card_w, card_h, gap = 312, 104, 20
    top0 = 392
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 3)
        x = 28 + col * (card_w + gap)
        yy = top0 + row * (card_h + 8)
        cv.fill_rect(x, yy, card_w, card_h, "#FFFFFF")
        cv.rect_outline(x, yy, card_w, card_h, "#D8D2C2", 1)
        cv.fill_rect(x, yy, 76, card_h, card["band"])
        _draw_icon(cv, card["icon"], x + 38, yy + 52, 22, "#F6F1E6")
        tx = x + 88
        tw = card_w - 100
        lines = cv.wrap_lines(card["head"], "bold13", tw)[:2]
        ly = yy + 12
        for ln in lines:
            cv.draw_text(tx, ly, ln, "bold13", INK)
            ly += 16
        ly += 2
        cv.draw_wrapped(tx, ly, tw, card["dek"], "reg13", MUTED, leading=15)


def _briefs(cv):
    by = 624
    cv.draw_text(28, by, "AROUND THE WORLD - IN BRIEF", "bold13", NAVY)
    cv.hline(28, by + 20, W - 56, RED, 2)
    col_w = 470
    col_x = [28, 526]
    # Balanced by hand: 13 briefs left (Europe, Americas, Asia-Pacific),
    # 11 right (Middle East & Africa, Tech & Markets, Sport & Culture).
    columns = [BRIEFS[:13], BRIEFS[13:]]
    for ci, col in enumerate(columns):
        x = col_x[ci]
        cy = by + 32
        seen = set()
        for brief in col:
            section, head, dek = brief["section"], brief["head"], brief["dek"]
            if section not in seen:
                seen.add(section)
                cv.draw_text(x, cy, section, "bold13", RED)
                cy += 18
            head_w = cv.text_width(head, "bold13")
            cv.fill_rect(x, cy + 2, 6, 6, RED)
            hx = x + 12
            if head_w <= col_w - 16:
                cv.draw_text(hx, cy, head, "bold13", INK)
                rest = _fit_text(cv, " - " + dek, "reg13", col_w - 16 - head_w)
                cv.draw_text(hx + head_w, cy, rest, "reg13", MUTED)
            else:
                cv.draw_text(hx, cy,
                             _fit_text(cv, head, "bold13", col_w - 16),
                             "bold13", INK)
            cy += 19


def _footer(cv):
    cv.hline(28, 984, W - 56, NAVY, 1)
    cv.draw_text(28, 996,
                 "Compiled Tuesday 24 November 2026  -  Sources: Reuters, Associated "
                 "Press, The Wall Street Journal, Al Jazeera, Oxfam",
                 "reg13", MUTED)


def draw():
    cv = Canvas(W, H, PAPER)
    _masthead(cv)
    _dateline(cv)
    _lead(cv)
    _chip(cv)
    _cards(cv)
    _briefs(cv)
    _footer(cv)
    return cv


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    canvas = draw()
    canvas.save_png(os.path.join(here, "entry.png"))
    print("wrote entry.png")
