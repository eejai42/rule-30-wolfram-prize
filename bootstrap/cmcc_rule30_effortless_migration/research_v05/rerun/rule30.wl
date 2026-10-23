(* Wolfram Language independent reproduction; not executed in this environment *)
T = 10000;
states = CellularAutomaton[30, {{1}, 0}, T];
center = states[[All, T + 1]];
{Length[center], Total[center], Count[center, 0]}
(* Expected: {10001, 5033, 4968}. Verify indexing for your WL version. *)
