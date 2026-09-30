W, H = 1280, 420
TITLE = "Sketch: how SHUCHI sanitises USB files at the air gap"
SEED = 42

BOX_W, BOX_H, GAP = 166, 88, 82
ROW_Y = 130
XS = [61 + i * (BOX_W + GAP) for i in range(5)]
CENTRE = [x + BOX_W / 2 for x in XS]
MID_Y = ROW_Y + BOX_H / 2

TRUST_Y, TRUST_H = 300, 70
AIR_X = (XS[3] + BOX_W + XS[4]) / 2


def draw(k):
    k.title("how SHUCHI works")

    # the air gap: only a rebuilt copy crosses it
    y = 100
    while y < 376:
        k.r.line(AIR_X, y, AIR_X, min(y + 13, 376), k.T["muted"], 2, double=False)
        y += 24
    k.hand(AIR_X, 90, "air gap", 22, k.T["muted"], "middle")

    stages = [
        ("dirty USB", "warm"),
        ("Intake", "warm"),
        ("Scan", "warm"),
        ("Rebuild", "cool"),
        ("clean USB", "cool"),
    ]
    for x, (label, tone) in zip(XS, stages):
        k.r.rect(x, ROW_Y, BOX_W, BOX_H, k.T["ink"], fill=k.T[tone], gap=11)
        k.hand(x + BOX_W / 2, ROW_Y + 57, label, 30, k.T["ink"], "middle")

    for i, note in enumerate(["read only", "true type", "verdict", "clean copy"]):
        start, end = XS[i] + BOX_W + 6, XS[i + 1] - 8
        k.r.arrow([(start, MID_Y), (end, MID_Y)], k.T["ink"], 2)
        if note != "clean copy":
            k.hand((start + end) / 2, MID_Y + 25, note, 20, k.T["muted"], "middle")

    # every step is signed and logged
    k.r.rect(XS[1], TRUST_Y, XS[3] + BOX_W - XS[1], TRUST_H,
             k.T["ink"], fill=k.T["cool"], gap=11)
    k.hand((XS[1] + XS[3] + BOX_W) / 2, TRUST_Y + 45,
           "TPM 2.0 receipt  +  hash-chain WORM log", 26, k.T["ink"], "middle")

    for cx in CENTRE[1:4]:
        top, bot = ROW_Y + BOX_H + 6, TRUST_Y - 8
        k.r.arrow([(cx, top), (cx, (top + bot) / 2), (cx, bot)], k.T["ink"], 2)
