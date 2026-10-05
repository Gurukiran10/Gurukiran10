"""Generate portfolio-styled SVG cards for the GitHub profile README."""
import base64, os
from html import escape
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
FONT_DIR = os.path.join(HERE, "fonts")
os.makedirs(OUT, exist_ok=True)

BG, CARD, BG2 = "#09090b", "#131316", "#111113"
LINE, LINE2 = "#232328", "#2e2e35"
TEXT, MUTED, DIM = "#ededef", "#8b8b95", "#5f5f69"
ACC, ACC_INK = "#c8f560", "#0b0d05"
BLUE, AMBER, PINK, RED = "#7cc4ff", "#ffc857", "#e7a6ff", "#ff6b6b"

FONTS = {  # key: (family, weight, style, ttf, woff)
    "sans": ("Inter Tight", 400, "normal", FONT_DIR + "/InterTight-400"),
    "sansb": ("Inter Tight", 600, "normal", FONT_DIR + "/InterTight-600"),
    "serif": ("Instrument Serif", 400, "italic", FONT_DIR + "/InstrumentSerif-400"),
    "mono": ("JetBrains Mono", 500, "normal", FONT_DIR + "/JetBrainsMono-500"),
}
_metrics = {}


def width(text, key, size):
    if key not in _metrics:
        f = TTFont(FONTS[key][3] + ".ttf")
        _metrics[key] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[key]
    w = 0
    for ch in text:
        g = cmap.get(ord(ch))
        w += hmtx[g][0] if g else upm * 0.6
    return w * size / upm


def wrap(text, key, size, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if width(t, key, size) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def font_css(keys):
    css = []
    for k in keys:
        fam, w, st, base = FONTS[k]
        data = base64.b64encode(open(base + ".woff", "rb").read()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};"
                   f"src:url(data:font/woff;base64,{data}) format('woff');}}")
    return "\n".join(css)


FAM = {
    "sans": "font-family:'Inter Tight',system-ui,sans-serif;font-weight:400",
    "sansb": "font-family:'Inter Tight',system-ui,sans-serif;font-weight:600",
    "serif": "font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-weight:400",
    "mono": "font-family:'JetBrains Mono',ui-monospace,Consolas,monospace;font-weight:500",
}


def T(x, y, text, key="sans", size=14, fill=TEXT, anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" style="{FAM[key]};font-size:{size}px" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{escape(text)}</text>')


def svg(name, w, h, body, keys, extra_css="", label=""):
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-label="{escape(label)}">\n<style>\n{font_css(keys)}\n{extra_css}\n</style>\n'
           f'<defs><radialGradient id="glow" cx="78%" cy="18%" r="60%"><stop offset="0" stop-color="{ACC}" stop-opacity=".14"/>'
           f'<stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient></defs>\n{body}\n</svg>')
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(out)
    print(f"{name:22} {len(out)//1024} KB")


def card(w, h, fill=CARD, glow=False, r=20):
    s = f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="{fill}" stroke="{LINE}" stroke-width="1.5"/>'
    if glow:
        s += f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="url(#glow)"/>'
    return s


def pill(x, y, text, key="mono", size=11.5, fg=MUTED, bg=None, border=LINE, padx=10, h=24):
    w = width(text, key, size) + padx * 2
    s = f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{bg or "none"}" stroke="{border}"/>'
    s += T(x + padx, y + h / 2 + size * 0.36, text, key, size, fg)
    return s, w


def chips(x, y, items, maxw=None):
    out, cx = [], x
    for it in items:
        w = width(it, "mono", 11) + 18
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="24" rx="7" fill="{BG2}" stroke="{LINE}"/>')
        out.append(T(cx + 9, y + 16, it, "mono", 11, MUTED))
        cx += w + 6
    return "".join(out)


ANIM = """
.l{animation:show 18s infinite backwards}
@keyframes show{0%{opacity:0}2%{opacity:1}93%{opacity:1}98%{opacity:0}100%{opacity:0}}
.blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
.pulse{animation:pulse 1.8s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}
@media (prefers-reduced-motion:reduce){.l,.blink,.pulse{animation:none}}
"""

# ---------------------------------------------------------------- hero
def hero():
    W, H = 900, 440
    b = [card(W, H, BG, glow=True)]
    # brand + status
    b.append(T(40, 58, "gk", "mono", 20, TEXT) + T(40 + width("gk", "mono", 20), 58, "/", "mono", 20, ACC))
    sx = 100
    sw = width("Open to AI / Backend Engineer roles", "mono", 12) + 44
    b.append(f'<rect x="{sx}" y="38" width="{sw:.1f}" height="28" rx="14" fill="{BG2}" stroke="{LINE}"/>')
    b.append(f'<circle class="pulse" cx="{sx+16}" cy="52" r="4" fill="{ACC}"/>')
    b.append(T(sx + 28, 56.5, "Open to AI / Backend Engineer roles", "mono", 12, MUTED))
    # headline
    fs, x0 = 58, 40
    y1, y2, y3 = 150, 212, 274
    b.append(T(x0, y1, "I build AI agents", "sansb", fs, TEXT, extra='letter-spacing="-2"'))
    tw = width("that ", "sansb", fs) - 2
    b.append(T(x0, y2, "that", "sansb", fs, TEXT, extra='letter-spacing="-2"'))
    b.append(T(x0 + tw + 4, y2, "do the work", "serif", fs + 4, MUTED))
    aw = width("and ", "sansb", fs) - 4
    b.append(T(x0, y3, "and", "sansb", fs, TEXT, extra='letter-spacing="-2"'))
    pw = width("prove it.", "sansb", fs) - 9 * 2 + 18
    b.append(f'<rect x="{x0+aw+4}" y="{y3-48}" width="{pw:.1f}" height="62" rx="8" fill="{ACC}"/>')
    b.append(T(x0 + aw + 13, y3, "prove it.", "sansb", fs, ACC_INK, extra='letter-spacing="-2"'))
    # sub
    sub = ("I'm Gurukiran S, an AI engineer. I build agentic systems with Python, FastAPI and "
           "LangGraph, and treat \u201cit said it's done\u201d as something to check, not believe.")
    for i, ln in enumerate(wrap(sub, "sans", 15.5, 455)):
        b.append(T(x0, 326 + i * 24, ln, "sans", 15.5, MUTED))
    b.append(T(x0, 326 + 3 * 24 + 4, "Recently completed: AI Platform Developer Intern @ SeedlingLabs", "mono", 11.5, DIM))

    # terminal
    tx, ty, tw_, th = 528, 92, 340, 300
    b.append(f'<rect x="{tx}" y="{ty}" width="{tw_}" height="{th}" rx="14" fill="{CARD}" stroke="{LINE}"/>')
    b.append(f'<path d="M{tx+14} {ty}h{tw_-28}a14 14 0 0 1 14 14v22h-{tw_}v-22a14 14 0 0 1 14-14z" fill="{BG2}"/>')
    b.append(f'<line x1="{tx}" y1="{ty+36}" x2="{tx+tw_}" y2="{ty+36}" stroke="{LINE}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        b.append(f'<circle cx="{tx+18+i*16}" cy="{ty+18}" r="5" fill="{c}"/>')
    b.append(T(tx + 72, ty + 22, "worker.run · invoice", "mono", 10.5, MUTED))
    b.append(f'<circle class="pulse" cx="{tx+tw_-62}" cy="{ty+18}" r="3.5" fill="{ACC}"/>')
    b.append(T(tx + tw_ - 52, ty + 22, "REPLAY", "mono", 9.5, ACC, extra='letter-spacing="1.2"'))
    rows = [("plan", BLUE, "read SOP · limit ₹50,000", MUTED),
            ("act", TEXT, "mail.open → INV-2291", TEXT),
            ("warn", AMBER, "over limit → human call", AMBER),
            ("ask", PINK, "finance.lead: approve?", PINK),
            ("obs", MUTED, "✓ approved", MUTED),
            ("act", TEXT, "erp.create_bill …", TEXT),
            ("err", RED, "500 Internal Server Error", RED),
            ("act", TEXT, "check before retry: 0 rows", TEXT),
            ("act", TEXT, "→ BILL-5512", TEXT),
            ("verify", BLUE, "different model checks …", MUTED),
            ("done", ACC, "✓ verified · 0 duplicates", ACC)]
    for i, (tag, tc, msg, mc) in enumerate(rows):
        y = ty + 62 + i * 20
        b.append(T(tx + 16, y, tag, "mono", 11, tc) + T(tx + 72, y, msg, "mono", 11, mc))
    b.append(f'<line x1="{tx}" y1="{ty+th-34}" x2="{tx+tw_}" y2="{ty+th-34}" stroke="{LINE}"/>')
    b.append(T(tx + 16, ty + th - 13, "steps 21 · cost $0.17 · verifier passed", "mono", 10.5, DIM))
    b.append(T(tx, ty + th + 22, "Illustrative replay of Acme Workforce's invoice scenario", "sans", 11.5, DIM))
    svg("hero.svg", W, H, "\n".join(b), ["sans", "sansb", "serif", "mono"], ANIM,
        "Gurukiran S — I build AI agents that do the work and prove it.")


# ---------------------------------------------------------------- buttons
def button(name, label, primary=False):
    w = width(label, "sansb", 15) + 44
    h = 46
    fill, fg, stroke = (ACC, ACC_INK, ACC) if primary else (CARD, TEXT, LINE2)
    body = (f'<rect x="1" y="1" width="{w-2:.1f}" height="{h-2}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            + T(w / 2, 29, label, "sansb", 15, fg, "middle"))
    svg(name, round(w), h, body, ["sansb"], label=label)


# ---------------------------------------------------------------- stats
def stats():
    W, H = 900, 128
    items = [("0", ACC, "false \u201cdone\u201ds in 27 live agent runs"),
             ("81", TEXT, "unit tests on one agent runtime, 29 on the safety gate"),
             ("5/5", TEXT, "correct safety stops: fraud, denied approval, out-of-role"),
             ("15+", TEXT, "built projects: agents, APIs, RAG systems, a Go service")]
    b = [card(W, H, BG)]
    cw = W / 4
    for i, (n, c, lbl) in enumerate(items):
        x = i * cw
        if i:
            b.append(f'<line x1="{x}" y1="1" x2="{x}" y2="{H-1}" stroke="{LINE}"/>')
        b.append(T(x + 24, 60, n, "sansb", 42, c, extra='letter-spacing="-1.5"'))
        for j, ln in enumerate(wrap(lbl, "sans", 13, cw - 44)):
            b.append(T(x + 24, 86 + j * 18, ln, "sans", 13, MUTED))
    svg("stats.svg", W, H, "\n".join(b), ["sans", "sansb"], label="Key numbers")


# ---------------------------------------------------------------- section heads
def head(name, eyebrow, title, italic):
    W, H = 900, 116
    b = [T(2, 24, eyebrow, "mono", 12.5, ACC, extra='letter-spacing="1"'),
         T(0, 76, title, "sansb", 44, TEXT, extra='letter-spacing="-1.5"'),
         T(width(title, "sansb", 44) - len(title) * 1.5 + 12, 76, italic, "serif", 48, MUTED)]
    svg(name, W, H, "\n".join(b), ["sansb", "serif", "mono"], label=f"{title} {italic}")


# ---------------------------------------------------------------- flagship
def flagship():
    W, H = 900, 400
    b = [card(W, H, CARD, glow=True, r=24)]
    p1, w1 = pill(32, 30, "Flagship", fg=ACC_INK, bg=ACC, border=ACC)
    p2, _ = pill(32 + w1 + 8, 30, "CentrAlign · Autonomous AI Task Worker")
    b += [p1, p2]
    b.append(T(32, 104, "Acme Workforce", "sansb", 40, TEXT, extra='letter-spacing="-1.5"'))
    lede = ("AI employees you hire with a role file. They work in real web apps through a real browser, "
            "stop and ask when a decision is yours, and only say \u201cdone\u201d after an independent "
            "verifier on a different model re-checks the live systems.")
    y = 138
    for ln in wrap(lede, "sans", 15, 470):
        b.append(T(32, y, ln, "sans", 15, MUTED)); y += 23
    y += 8
    for bl in ["Plans from company SOPs; acts in mail, ERP, a job portal and an ATS",
               "Recovers from server errors and fake \u201cSaved!\u201d toasts without duplicates",
               "Learns: one approved answer becomes a rule, so it stops asking"]:
        lines = wrap(bl, "sans", 13.5, 440)
        b.append(T(32, y, "→", "mono", 13, ACC))
        for ln in lines:
            b.append(T(54, y, ln, "sans", 13.5, MUTED)); y += 20
        y += 4
    b.append(chips(32, H - 52, ["Python", "Playwright", "Multi-model LLMs", "Evals", "CI"]))
    # metrics
    mx, my, mw, mh, g = 548, 30, 156, 88, 10
    ms = [("16/17", TEXT, "dev scenarios passed"), ("7/10", TEXT, "held-out runs, frozen before any run"),
          ("0", ACC, "false successes in 27 live runs"), ("$5.21", TEXT, "total eval spend")]
    for i, (v, c, l) in enumerate(ms):
        x = mx + (i % 2) * (mw + g); yy = my + (i // 2) * (mh + g)
        b.append(f'<rect x="{x}" y="{yy}" width="{mw}" height="{mh}" rx="14" fill="{BG2}" stroke="{LINE}"/>')
        b.append(T(x + 16, yy + 40, v, "sansb", 28, c, extra='letter-spacing="-1"'))
        for j, ln in enumerate(wrap(l, "sans", 11.5, mw - 30)):
            b.append(T(x + 16, yy + 62 + j * 15, ln, "sans", 11.5, MUTED))
    yy = my + 2 * (mh + g); ww = 2 * mw + g
    b.append(f'<rect x="{mx}" y="{yy}" width="{ww}" height="128" rx="14" fill="{BG2}" stroke="{LINE}"/>')
    b.append(T(mx + 16, yy + 26, "Learning loop: same invoice, before vs after one rule", "sans", 11.5, MUTED))
    for i, (v, l) in enumerate([("1 → 0", "questions"), ("27 → 20", "steps"), ("$.18 → $.10", "cost")]):
        x = mx + 16 + i * 98
        b.append(T(x, yy + 66, v, "mono", 14, ACC))
        b.append(T(x, yy + 88, l, "sans", 11.5, DIM))
    b.append(T(mx + 16, yy + 114, "View code, demo video and evidence reports ↗", "sans", 11.5, TEXT))
    svg("flagship.svg", W, H, "\n".join(b), ["sans", "sansb", "mono"], label="Acme Workforce")


# ---------------------------------------------------------------- project cards
def project(name, idx, tag, title, desc, stack, cta="View code ↗"):
    W, H = 440, 268
    b = [card(W, H, CARD, r=18)]
    b.append(T(24, 40, idx, "mono", 12.5, DIM))
    tw = width(tag, "mono", 11) + 20
    pl, _ = pill(W - 24 - tw, 22, tag, size=11)
    b.append(pl)
    b.append(T(24, 84, title, "sansb", 20, TEXT, extra='letter-spacing="-.5"'))
    y = 112
    for ln in wrap(desc, "sans", 13.5, W - 48)[:5]:
        b.append(T(24, y, ln, "sans", 13.5, MUTED)); y += 20
    b.append(chips(24, H - 76, stack))
    b.append(T(24, H - 22, cta, "sansb", 13.5, TEXT))
    b.append(f'<line x1="24" y1="{H-16}" x2="{24+width(cta,"sansb",13.5):.1f}" y2="{H-16}" stroke="{LINE2}"/>')
    svg(name, W, H, "\n".join(b), ["sans", "sansb", "mono"], label=title)


# ---------------------------------------------------------------- principles
def principles():
    W, H = 900, 200
    items = [("i.", "Verify, don't trust.", "An agent saying \u201cdone\u201d is a claim. A separate verifier re-checks the real system state."),
             ("ii.", "The LLM writes, code decides.", "Counting, limits and rules belong in code, where they can be tested."),
             ("iii.", "Write the evals first.", "Held-out tasks are frozen before the first run. No number without a measurement."),
             ("iv.", "Humans own the decisions.", "Money, people and anything irreversible get a checkpoint. Ask once, remember.")]
    b = [f'<line x1="0" y1="1" x2="{W}" y2="1" stroke="{LINE}"/>']
    cw = W / 4
    for i, (n, t, d) in enumerate(items):
        x = i * cw + (0 if i == 0 else 20)
        if i:
            b.append(f'<line x1="{i*cw}" y1="1" x2="{i*cw}" y2="{H}" stroke="{LINE}"/>')
        b.append(T(x, 44, n, "serif", 26, ACC))
        yy = 76
        for ln in wrap(t, "sansb", 16, cw - 34):
            b.append(T(x, yy, ln, "sansb", 16, TEXT)); yy += 21
        yy += 4
        for ln in wrap(d, "sans", 13, cw - 34):
            b.append(T(x, yy, ln, "sans", 13, MUTED)); yy += 19
    svg("principles.svg", W, H, "\n".join(b), ["sans", "sansb", "serif"], label="How I build")


# ---------------------------------------------------------------- marquee
def marquee():
    W, H = 900, 76
    words = ["Python", "FastAPI", "LangGraph", "RAG", "Qdrant", "pgvector", "Playwright",
             "TypeScript", "Next.js", "Go", "MCP", "Gemini · Groq · Claude"]
    parts, x = [], 0
    for _ in range(2):
        for w in words:
            parts.append(T(x, 48, w, "serif", 30, MUTED)); x += width(w, "serif", 30) + 22
            parts.append(T(x, 44, "✦", "sans", 14, ACC)); x += 36
    half = x / 2
    css = f".track{{animation:scroll 40s linear infinite}}@keyframes scroll{{to{{transform:translateX(-{half:.1f}px)}}}}" \
          "@media (prefers-reduced-motion:reduce){.track{animation:none}}"
    b = [f'<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
         f'<stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
         f'</linearGradient><mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>',
         f'<line x1="0" y1="1" x2="{W}" y2="1" stroke="{LINE}"/><line x1="0" y1="{H-1}" x2="{W}" y2="{H-1}" stroke="{LINE}"/>',
         f'<g mask="url(#m)"><g class="track">{"".join(parts)}</g></g>']
    svg("stack.svg", W, H, "\n".join(b), ["sans", "serif"], css, "Stack")


# ---------------------------------------------------------------- contact
def contact():
    W, H = 900, 300
    b = [card(W, H, BG, glow=True, r=24)]
    b.append(T(W / 2, 54, "05 — CONTACT", "mono", 12.5, ACC, "middle", 'letter-spacing="1"'))
    b.append(T(W / 2, 116, "Let's build something", "sansb", 50, TEXT, "middle", 'letter-spacing="-2"'))
    b.append(T(W / 2, 172, "that actually works.", "serif", 56, MUTED, "middle"))
    em = "sgurukiran1@gmail.com"
    ew = width(em, "sans", 26)
    b.append(T(W / 2, 228, em, "sans", 26, TEXT, "middle"))
    b.append(f'<rect x="{W/2-ew/2:.1f}" y="238" width="{ew:.1f}" height="2.5" fill="{ACC}"/>')
    b.append(T(W / 2, 270, "Open to AI engineering, agent and backend roles", "mono", 11.5, DIM, "middle"))
    svg("contact.svg", W, H, "\n".join(b), ["sans", "sansb", "serif", "mono"], label="Contact: sgurukiran1@gmail.com")


if __name__ == "__main__":
    hero(); stats(); flagship(); principles(); marquee(); contact()
    button("btn-portfolio.svg", "Portfolio ↗", True)
    button("btn-linkedin.svg", "LinkedIn ↗")
    button("btn-email.svg", "Email")
    button("btn-demo.svg", "Demo video ▶")
    head("h-work.svg", "01 — SELECTED WORK", "Things I've built", "and measured.")
    head("h-principles.svg", "02 — HOW I BUILD", "Four rules I", "actually follow.")
    head("h-stack.svg", "03 — STACK", "Tools I", "ship with.")
    project("p-research.svg", "02", "Techvruk · Challenge", "Autonomous Research Agent",
            "A LangGraph agent that plans sub-questions, uses tools in a ReAct loop, critiques its own "
            "findings and writes a cited report. It can only cite URLs a tool actually returned.",
            ["LangGraph", "FastAPI", "SQLite memory"])
    project("p-atlas.svg", "03", "Hackathon", "Atlas: Financial Analyst on Telegram",
            "No slash commands and no menus. Ask about a ticker, have it watch AMD for you, or drop in a "
            "chart screenshot or an earnings PDF and ask what it means.",
            ["FastAPI", "pgvector", "Gemini"])
    project("p-complaint.svg", "04", "AIVOA.AI · Live", "Pharma Complaint Copilot",
            "One chat box logs pharma complaints, corrects them in plain English and answers questions. "
            "A LangGraph router decides; the AI is the only thing that fills the form.",
            ["LangGraph", "Groq", "React"], "Live demo ↗")
    project("p-convin.svg", "05", "Convin · Take-home", "webhook-ingest: debugging Go",
            "A take-home simulating a production incident: duplicate call records, drifting counts, "
            "silently unprocessed recordings and in-flight work lost on every deploy. Root-caused and fixed.",
            ["Go", "Concurrency", "Idempotency"])
    project("p-meeting.svg", "06", "Personal · Live", "Meeting Intelligence",
            "An AI meeting assistant: transcription, summaries, action-item extraction and semantic "
            "search over past meetings, with vector-database memory for contextual retrieval.",
            ["FastAPI", "RAG", "Vector DB"], "Live demo ↗")
    project("p-lead.svg", "07", "SoftwareBrio · Take-home", "Lead Enrichment Agent",
            "Give it company domains. It crawls each public site with a headless browser and returns "
            "structured intelligence: overview, ICP, contact routes, leadership and a confidence score.",
            ["Playwright", "LLM extraction", "Python"])
