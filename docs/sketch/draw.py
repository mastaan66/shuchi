W, H = 1280, 440
TITLE = "Sketch: how SHUCHI sanitises USB files at the air gap"
SEED = 42


def draw(k):
    k.title("how SHUCHI works")

    k.r.rect(80, 100, 200, 80, k.T["ink"], fill=k.T["cool"], gap=11)
    k.hand(180, 155, "dirty USB", 28, k.T["ink"], "middle")

    k.r.line(300, 140, 400, 140, k.T["ink"], 2)
    k.r.arrow([(400, 140), (480, 140)], k.T["ink"], 2)

    k.r.rect(480, 90, 200, 100, k.T["ink"], fill=k.T["warm"], gap=11)
    k.hand(580, 145, "Intake", 28, k.T["ink"], "middle")

    k.r.line(700, 140, 800, 140, k.T["ink"], 2)
    k.r.arrow([(800, 140), (880, 140)], k.T["ink"], 2)

    k.r.rect(880, 90, 200, 100, k.T["ink"], fill=k.T["cool"], gap=11)
    k.hand(980, 145, "Scan", 28, k.T["ink"], "middle")

    k.r.line(1100, 140, 1180, 140, k.T["ink"], 2)
    k.r.arrow([(1180, 140), (1260, 140)], k.T["ink"], 2)

    k.r.rect(100, 260, 200, 100, k.T["ink"], fill=k.T["warm"], gap=11)
    k.hand(200, 315, "Rebuild", 28, k.T["ink"], "middle")

    k.r.line(320, 310, 420, 310, k.T["ink"], 2)
    k.r.arrow([(420, 310), (500, 310)], k.T["ink"], 2)

    k.r.rect(500, 260, 200, 100, k.T["ink"], fill=k.T["cool"], gap=11)
    k.hand(600, 315, "TPM Sign", 28, k.T["ink"], "middle")

    k.r.line(720, 310, 820, 310, k.T["ink"], 2)
    k.r.arrow([(820, 310), (900, 310)], k.T["ink"], 2)

    k.r.rect(900, 260, 200, 100, k.T["ink"], fill=k.T["warm"], gap=11)
    k.hand(1000, 315, "Clean USB", 28, k.T["ink"], "middle")

    k.r.line(1120, 310, 1200, 310, k.T["ink"], 2)
    k.r.arrow([(1200, 310), (1260, 310)], k.T["ink"], 2)

    k.r.rect(100, 400, 200, 56, k.T["ink"], fill=k.T["cool"], gap=11)
    k.hand(200, 428, "WORM Log", 24, k.T["ink"], "middle")

    k.r.line(320, 360, 420, 360, k.T["ink"], 2)
    k.r.arrow([(420, 360), (500, 360)], k.T["ink"], 2)

    k.r.rect(500, 400, 200, 56, k.T["ink"], fill=k.T["cool"], gap=11)
    k.hand(600, 428, "Receipt", 24, k.T["ink"], "middle")
