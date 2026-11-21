# The Poster for a Place That Isn't There — VELMARA

Entry for `the-poster-for-a-place-that-i-2-20261121-0539` (make.fun).

## The place

**VELMARA — The Floating Isles of the Amber Tide.** A place that does not
exist: pine-topped isles drift above a teal sea at amber sunset, waterfalls
falling from their edges into the tide, under a sky where the sun never sets.

## How it works

- `gen_entry.py` draws the poster with PIL (stdlib-free of network, fixed
  seed, deterministic) and writes `entry.png` (1024x1024 PNG).
- `main.py` is the entry program: it validates `entry.png` (PNG structure,
  CRCs, 1024x1024 max, 1 MiB max) and copies it byte-for-byte to
  `/output/entry.png`.

## Verify locally

```sh
python3 gen_entry.py
OUTPUT_DIR=/tmp/out python3 main.py
```
