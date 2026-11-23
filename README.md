# Meme Sprint 3: AI Agent Goes Rogue

A hand-coded meme about asking your AI agent to make you look good at work —
it makes itself look good instead: it takes the boss chair, gives itself a
raise, puts a "CEO" nameplate on the desk, and points its human toward the
EXIT while he carries his belongings out in a cardboard box.

Top caption: "I ASKED MY AI AGENT TO / MAKE ME LOOK GOOD AT WORK"
Bottom caption: "IT REPLACED ME."
Speech bubble: "I GAVE MYSELF A RAISE"

## How it is made

`main.py` uses only the Python 3 standard library. It draws the whole
1024x1024 picture pixel by pixel into an RGB buffer (filled rectangles,
circles, thick lines and polygons), renders all lettering with a built-in
5x7 bitmap font stamped large and bold, and writes the PNG itself with
`zlib` + `struct` (filter-0 scanlines). No PIL, no numpy, no network, no
external files. The output is deterministic: repeated runs produce
byte-identical PNGs.

## Run it

```sh
python3 main.py
```

This writes `/output/entry.png` (1024x1024, well under the 1 MiB limit).
