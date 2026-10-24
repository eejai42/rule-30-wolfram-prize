# Loop 16: bounded or slowly growing? Pushing the excess to onsets near 400

Loop 15 found the excess `L(T,a) - T` at most 56 for all words of periods 7 and 8 at every
completed onset (to 192), but the *minimum* excess among the few words reaching the far onsets
crept up (14, 17, 23 at onsets 128, 160, 192). With only one or two words that far out, a
bounded excess and one growing like `log T` cannot be told apart.

The live set of the search grows like 2^(zero-times before 2T), so the words that reach far are
those with one zero per period. This loop uses exactly those words, `a = 0 1^(p-1)` for
`p = 8, 10, 12, 16`, raises the live-set cap to 2^25 (the machine has 48 GB of memory; the
live set is transient and nothing large is written to disk), and steps the onset up until the
cap stops the search, which should be near `T ≈ 25 p`.

**H29 (stated before computing).** For `a = 0 1^(p-1)`, `p ∈ {8, 10, 12, 16}`, and every onset
`T ≥ 32` the enumeration completes, the excess `L(T,a) - T` is at most 64 (the loop 15 bound).

**F15.** The table of `L(T,a)`, excess and death cells for those words and onsets, with the
excess fitted against `T` and against `log2 T` so the next loop can see which law the far
onsets follow.

If H29 holds and the excess is flat, B5 for these words has a shape independent of `T` and the
induction is the next loop. If the excess grows, the growth law is the next hypothesis.
