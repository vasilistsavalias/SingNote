# Kakes Synitheies - Working Synthesis

This is the current brainstorm memory for adding `Kakes Synitheies` to SingNote. It compares two Kithara transcriptions and their comment threads without treating either one as final.

Sources:

- Version 1, Nikolas apo Rodo: https://kithara.to/stixoi/MTA4ODg3MjM1/kakes-synitheies-pasxalidis-miltiadis-lyrics
- Version 2, Greekrocker: https://kithara.to/stixoi/MzE1OTU1NzE1/kakes-synitheies-pasxalidis-miltiadis-lyrics

## Shared Ground

- Key: `G major`
- Core harmonic language: `G`, `Am`, `C`, `D`, `Em`, `Bm` or disputed `B`, plus occasional `B7`
- Main intro vocabulary: `G`, `Gsus4/G4`, `Am`, `C`, `D`
- Refrain backbone appears in both versions as a movement around `C D G Bm Em`
- Both versions support a folk-rock ballad feel rather than a rigid pop strum
- The crowd repeatedly asks for strumming, meaning this needs explicit lesson guidance in our `General` tab

## Most Likely Final Harmony Direction

Use Version 2 as the base skeleton, then apply comment-backed corrections. This is not just because Version 2 has a higher rating; several comments from both pages converge toward Version 2's choices.

Recommended working harmony:

- Intro: `G Gsus4 G Gsus4`, then `G Am C D`
- Verse opening: `G Am C D G`
- Long second verse phrase: `G Am C D C D`
- Bad-habits section: `Am Em D G D`
- Refrain entry: `C D G Bm Em`
- Refrain inner turn: `Am D B7 Em`
- Ending tag candidate: start with `Am D G`, then test `Am D C G` and `Am7 D C/Em7/Am7/D7 G`

## Comment Cross-Check

Comments that support Version 2:

- Version 2 has direct validation comments: one user calls it the correct version, another calls it a perfect rendering, and another says it is the best of the versions.
- Version 2's `G4`/`Gsus4` intro is independently supported by Version 1 comments that hear `G -> Gsus4 -> Gsus4/G -> Am C D` near the start.
- Version 2's `Am Em D...` area is supported by older Version 1 corrections saying that plain `C` is wrong on the "old things" phrase and that `Em D` works better.
- Version 2's `B7` color is supported by both its own chart and Version 1 comments that prefer `B7` over the `G/Bm` movement in one refrain phrase.

Comments that modify Version 2:

- The `Bm` in the refrain should not be treated as settled. One Version 1 commenter says it should be `B`, while one Version 2 commenter says the passage can be handled as an `F#` passing note into `Em` rather than a full `Bm` chord.
- `Am7` may replace `C` in the "too late for truths" ending.
- `D7` may be useful as a color chord where it sounds right, but should not be blindly inserted everywhere.
- The final cafe/cigarette tag has three candidates: `Am D G`, `D C G`, and the richer `Am7 D C/Em7/Am7/D7 G`.

Decision: start from Version 2, but mark `Bm`, `Am7`, `D7`, and the final tag as teacher-check points.

## Chord Disputes To Resolve By Ear

- `Bm` versus `B` versus `F#` passing-note treatment in the refrain
- `C` versus `Am7` in the "too late for truths" ending
- simple final tag versus richer passing-chord ending
- whether `D7` should be a real chord in the final chart or only a color suggestion
- whether the first verse should stay simplified like Version 1 or use the explicit repeated rows of Version 2

## Strumming Working Model

Initial SingNote `strumming_pattern` candidate:

`Accented D, D, D U D U, rest U D U, accented D U D U. Split the pattern when a chord changes mid-line. Keep the intro lighter and ringing.`

Simpler display candidate:

`D D U UDU DDU, with accents on phrase starts and split changes on C/D or Am/Em/D moves.`

This should be tested with the teacher because the comments show that rhythm is the main pain point for learners.

## What Goes Into The App Later

For the final `seed_data/songs/kakes-synitheies.yaml`, we still need:

- clean user-approved lyrics typed by us, not copied wholesale from Kithara
- melody packages from you or your teacher
- final chord placement per lyric line
- final strumming note for the `General` tab
- optional note in `tempo_notes` explaining that `G4` means `Gsus4`

## Temporary YAML Strategy

Do not add a live seed song yet unless we are comfortable showing incomplete melody. Instead, when ready, create:

`seed_data/songs/kakes-synitheies.yaml`

Suggested metadata:

```yaml
schema_version: 2
song:
  id: kakes-synitheies
  title: Κακές Συνήθειες
  artist: Μίλτος Πασχαλίδης
  description: "Working Greek singing lesson chart built from compared public chord transcriptions and teacher/student melody notes."
  key_signature: G major
  time_signature: 4/4
  tempo_bpm:
  tempo_notes: "G4 in source comments is treated as Gsus4. Tempo and exact feel still need listening confirmation."
  strumming_pattern: "Accented D, D, D U D U, rest U D U, accented D U D U. Split the pattern when chords change mid-line."
sections: []
```

## Next Decision

Before creating the live YAML, choose the base:

- `Base A`: simpler Version 1, easier for singing lesson use
- `Base B`: more detailed Version 2, probably closer harmonically
- `Hybrid`: Version 2 skeleton with Version 1's simplified ending where it feels cleaner

Current recommendation: `Hybrid`, with Version 2 as the skeleton.
