# API And Data Contracts

SingNote does not expose an HTTP API in this repository. The relevant contracts
are the portable song data format and the internal validated domain model.

Canonical sources:
- [`src/singnote/domain/models.py`](../../src/singnote/domain/models.py)
- [`src/singnote/seeds.py`](../../src/singnote/seeds.py)

## Portable Song Schema

Top-level portable shape:

```yaml
song:
  id: wish-you-were-here
  title: Wish You Were Here
sections:
  - id: verse-1
    title: Verse 1
    lines:
      - lyrics: So, so you think you can tell,
        chords:
          - symbol: C
            anchor: So
          - symbol: D/F#
            anchor: tell
        melody_text: |
          So = C,B,G
          So = C
          you = B
        rhythm:
          pattern: 2-bar pickup
          emphasis: change chord mid-line
annotations: []
```

## Line-Level Fields

- `lyrics`: required
- `chords`: optional, either a simple symbol list or structured chord objects
- `roman_numerals`: optional
- `melody_text`: preferred shorthand authoring option
- `melody_packages`: optional explicit structured alternative
- `rhythm`: optional string or mapping

## Chord Placement Rules

For basic charts, use a simple list:

```yaml
chords: [C, G, Am]
```

For accurate chord-over-lyric placement, use objects:

```yaml
chords:
  - symbol: C
    anchor: So
  - symbol: G
    anchor: tell
  - symbol: Am
    offset: 12
```

- `symbol`: required chord label
- `anchor`: optional lyric text where the chord should appear
- `offset`: optional zero-based character column, used when an anchor is ambiguous
- `position`: optional legacy display hint, defaults to `before`

## Melody Package Rules

- package text cannot be empty
- a package must include at least one note
- note tokens must look like `C`, `Bb`, or `F#4`
- package order is list order

## Internal Domain Truth

The runtime domain model normalizes data into:

- lyric sections and segments
- melody packages on segments
- flattened `melody_notes` for compatibility

When summary docs and code disagree, the code in the canonical sources wins.
