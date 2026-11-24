# render.py — paints "The World in One Day — 24 November 2026".
#
# Only the standard library is used: the Canvas in image.py plus the
# bitmap fonts embedded in font_data.py. The layout is one lead story,
# six illustrated cards and twenty-four briefs, 31 stories altogether,
# every one dated Tuesday 24 November 2026 and checked against live
# reporting published that day.
import os

from image import Canvas

W, H = 1024, 1024
PAPER = '#F6F1E6'
NAVY = '#16233D'
NAVY2 = '#1F3358'
RED = '#B3352B'
TEAL = '#0F766E'
GOLD = '#C99A2B'
SLATE = '#3D4A5C'
PLUM = '#5B3A5E'
INK = '#1C1C1C'
MUTED = '#5A5A52'

LEAD_HEAD = ['HUANG RETURNS AS', 'NVIDIA CHIEF']
LEAD_DEK = (
    "Nvidia's board unanimously reinstated Jensen Huang as chief "
    "executive on Monday - and the shares surged more than 31% in a "
    "single day."
)
LEAD_STATS = '+31% IN A DAY  |  UNANIMOUS BOARD VOTE  |  SENATE HEARING 3 DEC'

# One dict per card: band colour, headline, one-line standfirst, icon.
CARDS = [
    {'color': TEAL,
     'title': 'UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA',
     'standfirst': 'Kyiv says drones sank the corvette Merkury at Benghazi.',
     'mark': 'ship'},
    {'color': NAVY2,
     'title': 'NATO SENDS AWACS TO POLAND',
     'standfirst': 'Early-warning jets deploy after missiles landed in Poland.',
     'mark': 'plane'},
    {'color': GOLD,
     'title': 'COP31 ENDS WITH NO DEAL',
     'standfirst': 'Climate talks in Antalya collapse as the EU rejects the text.',
     'mark': 'globe'},
    {'color': RED,
     'title': 'FACTORY FIRE KILLS 24 IN INDONESIA',
     'standfirst': 'Blaze at a candy plant in Cikande; dozens still missing.',
     'mark': 'flame'},
    {'color': SLATE,
     'title': '6.5 QUAKE SHAKES VANUATU',
     'standfirst': 'Strong tremor hits the Pacific islands; no tsunami threat.',
     'mark': 'waves'},
    {'color': PLUM,
     'title': 'DELTA OUTAGE DELAYS 3,000 FLIGHTS',
     'standfirst': 'Automation failure snarls US air travel before Thanksgiving.',
     'mark': 'runway'},
]

# One dict per brief: desk, headline, standfirst. Each brief is short
# enough to sit on a single line inside its column.
BRIEFS = [
    {'desk': 'EUROPE', 'title': '450 German schools hit by bomb threats',
     'standfirst': 'Police say emailed threats appear unfounded; classes disrupted.'},
    {'desk': 'EUROPE', 'title': 'Cyprus expels two Russian diplomats',
     'standfirst': 'Pair accused of espionage are struck from the embassy list.'},
    {'desk': 'EUROPE', 'title': 'Berlin sends tanks to Lithuania by rail',
     'standfirst': 'Route avoids Poland to avoid provoking Moscow, Bild reports.'},
    {'desk': 'EUROPE', 'title': 'France condemns settler attacks',
     'standfirst': 'Paris denounces violence against Palestinian communities.'},
    {'desk': 'AMERICAS', 'title': 'Democrats clinch House, 258 seats',
     'standfirst': 'Largest House majority since 1992, with funding deadline 11 Dec.'},
    {'desk': 'AMERICAS', 'title': 'FBI probes hack of crime database',
     'standfirst': 'Apparent breach of a key national law-enforcement system.'},
    {'desk': 'AMERICAS', 'title': 'Trump pauses Iowa chemical detonation',
     'standfirst': 'Army told to halt disposal of toxic lead azide stockpile.'},
    {'desk': 'AMERICAS', 'title': "16 killed in 'El Chapo Isidro' capture",
     'standfirst': 'Mexican forces kill cartel suspects in Sinaloa operation.'},
    {'desk': 'AMERICAS', 'title': 'Panama resumes Cobre mine talks',
     'standfirst': 'Government reopens negotiations with First Quantum Minerals.'},
    {'desk': 'ASIA-PACIFIC', 'title': 'China official sentenced to death',
     'standfirst': 'Convicted of leaking 100 intelligence reports, 35 state secrets.'},
    {'desk': 'ASIA-PACIFIC', 'title': 'Seoul names new foreign minister',
     'standfirst': 'South Korea also picks its first woman intelligence chief.'},
    {'desk': 'ASIA-PACIFIC', 'title': 'Lahore tops world pollution ranking',
     'standfirst': 'AQI crosses 500; eight Pakistani cities among the worst.'},
    {'desk': 'ASIA-PACIFIC', 'title': 'Bangladesh garment workers balk',
     'standfirst': 'Unions reject the latest salary proposal as too low.'},
    {'desk': 'MIDDLE EAST & AFRICA', 'title': 'Israeli strikes kill three in Gaza',
     'standfirst': 'Dead include a worker with the UN agency UNRWA.'},
    {'desk': 'MIDDLE EAST & AFRICA', 'title': 'Oxfam: Gaza poisoned for decades',
     'standfirst': 'Explosives and toxins contaminate air, soil and water.'},
    {'desk': 'MIDDLE EAST & AFRICA', 'title': 'Iran flogs singer, 74 lashes',
     'standfirst': 'Parastoo Ahmadi punished with four crew over a virtual concert.'},
    {'desk': 'MIDDLE EAST & AFRICA', 'title': 'US sanctions Iran shadow banks',
     'standfirst': 'Treasury targets dozens of people and entities.'},
    {'desk': 'MIDDLE EAST & AFRICA', 'title': "Taliban erases women's names",
     'standfirst': "Balkh province replaces them with 'Bibi' on documents."},
    {'desk': 'TECH & MARKETS', 'title': 'Trump to punish offshore data centres',
     'standfirst': 'US firms building storage abroad face penalties, he says.'},
    {'desk': 'TECH & MARKETS', 'title': 'UN chief: AI safety rules in a year',
     'standfirst': 'Guterres demands a global AI safety framework, fast.'},
    {'desk': 'TECH & MARKETS', 'title': 'Chemical watchdog in budget crisis',
     'standfirst': 'US payment delays leave the OPCW facing an emergency.'},
    {'desk': 'TECH & MARKETS', 'title': 'BepiColombo now orbits Mercury',
     'standfirst': 'Probe entered orbit on Saturday after a long cruise.'},
    {'desk': 'SPORT & CULTURE', 'title': '49ers rout Vikings 35-10 in Mexico City',
     'standfirst': "Purdy throws three touchdowns in the NFL's Mexico game."},
    {'desk': 'SPORT & CULTURE', 'title': 'Mossad helped foil Swift Vienna plot',
     'standfirst': 'Ex-spy chief says an ISIS-inspired attack was stopped.'},
]


def _shorten(cv, text, font, max_w):
    """Trim text down, adding an ellipsis, until it fits max_w."""
    if cv.text_width(text, font) <= max_w:
        return text
    while text and cv.text_width(text + '...', font) > max_w:
        text = text[:-1]
    return text + '...'


def _glyph(cv, kind, x, y, s, fg):
    """Draw a small geometric icon centred near (x, y), size about s."""
    if kind == 'ship':
        cv.fill_poly([(x - s, y + 8), (x + s, y + 8),
                      (x + s - 8, y + 22), (x - s + 8, y + 22)], fg)
        cv.fill_rect(x - 2, y - 18, 4, 26, fg)
        cv.fill_poly([(x + 2, y - 18), (x + 2, y + 2),
                      (x + 20, y + 2)], fg)
        cv.hline(x - s - 4, y + 28, 2 * s + 8, fg, 2)
    elif kind == 'plane':
        cv.fill_poly([(x - s, y), (x + s, y - 6), (x + s, y + 6)], fg)
        cv.fill_poly([(x - 6, y - 4), (x + 10, y - 22),
                      (x + 16, y - 4)], fg)
        cv.fill_poly([(x - 6, y + 4), (x + 10, y + 22),
                      (x + 16, y + 4)], fg)
        cv.fill_rect(x - 2, y - 26, 4, 6, fg)
        cv.fill_circle(x, y - 28, 5, fg)
    elif kind == 'globe':
        cv.circle_outline(x, y, s, fg, 3)
        cv.line(x - s, y, x + s, y, fg, 2)
        cv.line(x, y - s, x, y + s, fg, 2)
        cv.fill_circle(x + s // 2, y - s // 2, 4, fg)
    elif kind == 'flame':
        cv.fill_poly([(x, y - s - 4), (x + 12, y - 6), (x + 18, y + 8),
                      (x + 10, y + s), (x - 10, y + s), (x - 18, y + 8),
                      (x - 12, y - 6)], fg)
        cv.fill_poly([(x, y - 2), (x + 7, y + 8), (x, y + s - 4),
                      (x - 7, y + 8)], PAPER)
    elif kind == 'waves':
        for k in range(3):
            yy = y - 12 + k * 12
            cv.line(x - s, yy, x - s // 2, yy - 8, fg, 3)
            cv.line(x - s // 2, yy - 8, x, yy, fg, 3)
            cv.line(x, yy, x + s // 2, yy - 8, fg, 3)
            cv.line(x + s // 2, yy - 8, x + s, yy, fg, 3)
        cv.line(x - 4, y - 30, x + 6, y - 14, fg, 3)
        cv.line(x + 6, y - 14, x - 2, y - 2, fg, 3)
    elif kind == 'runway':
        cv.fill_poly([(x - s, y + 4), (x + s, y - 4), (x + s, y + 4),
                      (x - s, y + 12)], fg)
        cv.fill_rect(x - s, y + 20, 12, 3, fg)
        cv.fill_rect(x - s // 3, y + 20, 12, 3, fg)
        cv.fill_rect(x + s // 3, y + 20, 12, 3, fg)
        cv.fill_poly([(x - 8, y - 22), (x + 22, y - 26), (x + 22, y - 18),
                      (x - 8, y - 14)], fg)


def _right_aligned(cv, text, font, y, color, margin=28):
    """Draw one line right-aligned against the page margin."""
    cv.draw_text(W - margin - cv.text_width(text, font), y, text, font, color)


def _header(cv):
    cv.fill_rect(0, 0, W, 88, NAVY)
    cv.draw_text(28, 18, 'THE WORLD IN ONE DAY', 'bold56', '#F6F1E6')
    cv.draw_text(28, 70, 'TUESDAY  -  24 NOVEMBER 2026', 'bold13', GOLD)
    _right_aligned(cv, 'THE DAY IN WORLD NEWS', 'bold13', 30, '#F6F1E6')
    _right_aligned(cv, '31 STORIES  -  ONE IMAGE', 'reg13', 52, '#C9CFD8')
    cv.fill_rect(0, 88, W, 4, RED)


def _kicker(cv):
    cv.draw_text(28, 104,
                 'SUMMING UP TUESDAY 24 NOVEMBER 2026 - FROM KYIV TO SEOUL, '
                 'SILICON VALLEY TO ANTALYA', 'bold13', NAVY)
    cv.hline(28, 124, W - 56, NAVY, 1)


def _lead_story(cv):
    y = 140
    cv.draw_text(28, y, 'TECHNOLOGY  -  THE LEAD STORY', 'bold13', RED)
    y += 22
    for headline in LEAD_HEAD:
        cv.draw_text(28, y, headline, 'bold40', INK)
        y += 46
    y += 4
    y = cv.draw_wrapped(28, y, 560, LEAD_DEK, 'reg20', '#33302A', leading=26)
    y += 10
    cv.draw_text(28, y, LEAD_STATS, 'bold13', RED)


def _chip_art(cv):
    """Lead illustration, right of the lead: a chip on a circuit board."""
    bx, by, bw, bh = 612, 132, 384, 236
    cv.fill_rect(bx, by, bw, bh, NAVY)
    cv.rect_outline(bx, by, bw, bh, GOLD, 2)
    for i in range(5):
        yy = by + 24 + i * 40
        cv.hline(bx + 16, yy, 60, TEAL, 2)
        cv.hline(bx + bw - 76, yy, 60, TEAL, 2)
    for i in range(4):
        xx = bx + 60 + i * 88
        cv.vline(xx, by + 12, 30, GOLD, 2)
        cv.vline(xx, by + bh - 42, 30, GOLD, 2)
    side = 150
    qx = bx + (bw - side) // 2
    qy = by + (bh - side) // 2
    cv.fill_rect(qx, qy, side, side, '#0E1B30')
    cv.rect_outline(qx, qy, side, side, GOLD, 3)
    for i in range(6):
        cv.fill_rect(qx - 14, qy + 12 + i * 22, 14, 6, GOLD)
        cv.fill_rect(qx + side, qy + 12 + i * 22, 14, 6, GOLD)
        cv.fill_rect(qx + 12 + i * 22, qy - 14, 6, 14, GOLD)
        cv.fill_rect(qx + 12 + i * 22, qy + side, 6, 14, GOLD)
    tag = 'NVDA'
    cv.draw_text(qx + (side - cv.text_width(tag, 'bold40')) // 2, qy + 34,
                 tag, 'bold40', '#F6F1E6')
    gain = '+31% IN A DAY'
    cv.draw_text(qx + (side - cv.text_width(gain, 'bold13')) // 2, qy + 92,
                 gain, 'bold13', GOLD)
    cv.draw_text(bx + 16, by + bh - 24, 'JENSEN HUANG, BACK IN CHARGE',
                 'bold13', '#C9CFD8')


def _card_grid(cv):
    cw, ch, gap = 312, 104, 20
    top = 392
    for n, card in enumerate(CARDS):
        r, c = divmod(n, 3)
        x = 28 + c * (cw + gap)
        y = top + r * (ch + 8)
        cv.fill_rect(x, y, cw, ch, '#FFFFFF')
        cv.rect_outline(x, y, cw, ch, '#D8D2C2', 1)
        cv.fill_rect(x, y, 76, ch, card['color'])
        _glyph(cv, card['mark'], x + 38, y + 52, 22, '#F6F1E6')
        text_x = x + 88
        text_w = cw - 100
        head_lines = cv.wrap_lines(card['title'], 'bold13', text_w)[:2]
        line_y = y + 12
        for line in head_lines:
            cv.draw_text(text_x, line_y, line, 'bold13', INK)
            line_y += 16
        line_y += 2
        cv.draw_wrapped(text_x, line_y, text_w, card['standfirst'],
                        'reg13', MUTED, leading=15)


def _brief_columns(cv):
    top = 624
    cv.draw_text(28, top, 'AROUND THE WORLD - IN BRIEF', 'bold13', NAVY)
    cv.hline(28, top + 20, W - 56, RED, 2)
    width = 470
    starts = [28, 526]
    # Balanced by hand: 13 briefs left (Europe, Americas, Asia-Pacific),
    # 11 right (Middle East & Africa, Tech & Markets, Sport & Culture).
    groups = [BRIEFS[:13], BRIEFS[13:]]
    for i, group in enumerate(groups):
        x = starts[i]
        y = top + 32
        shown = set()
        for brief in group:
            desk = brief['desk']
            title = brief['title']
            standfirst = brief['standfirst']
            if desk not in shown:
                shown.add(desk)
                cv.draw_text(x, y, desk, 'bold13', RED)
                y += 18
            title_w = cv.text_width(title, 'bold13')
            cv.fill_rect(x, y + 2, 6, 6, RED)
            text_x = x + 12
            if title_w <= width - 16:
                cv.draw_text(text_x, y, title, 'bold13', INK)
                tail = _shorten(cv, ' - ' + standfirst, 'reg13',
                                width - 16 - title_w)
                cv.draw_text(text_x + title_w, y, tail, 'reg13', MUTED)
            else:
                cv.draw_text(text_x, y,
                             _shorten(cv, title, 'bold13', width - 16),
                             'bold13', INK)
            y += 19


def _colophon(cv):
    cv.hline(28, 984, W - 56, NAVY, 1)
    cv.draw_text(28, 996,
                 'Compiled Tuesday 24 November 2026  -  Sources: Reuters, '
                 'Associated Press, The Wall Street Journal, Al Jazeera, Oxfam',
                 'reg13', MUTED)


def draw():
    cv = Canvas(W, H, PAPER)
    _header(cv)
    _kicker(cv)
    _lead_story(cv)
    _chip_art(cv)
    _card_grid(cv)
    _brief_columns(cv)
    _colophon(cv)
    return cv


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    canvas = draw()
    canvas.save_png(os.path.join(here, 'entry.png'))
    print('wrote entry.png')
