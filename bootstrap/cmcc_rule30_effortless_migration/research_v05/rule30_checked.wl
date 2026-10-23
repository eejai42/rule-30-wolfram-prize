(* Prepared for external Wolfram Language reproduction; NOT executed here. *)
ClearAll[centerBits, diagonalBits];
centerBits[h_Integer?NonNegative] := Flatten[CellularAutomaton[30, {{1}, 0}, {h, {{0}}}]];
bits = centerBits[100000];
Print[{Length[bits], Total[bits], Count[bits, 0]}];
(* Expected: {100001, 50098, 49903}. Time zero is included. *)
If[Length[bits] != 100001 || Total[bits] != 50098, Abort[]];
Export["center_100000_wl.txt", StringJoin[ToString /@ bits] <> "\n", "Text"];
