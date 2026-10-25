import Lean

/-!
# Export the Rule 30 Prize kit's Lean environment as data

Run from the kit's root, so that `lake env` puts the kit's compiled modules on `LEAN_PATH`:

```
cd external/Rule30PrizeKit
lake env lean --run ../../lean/ExportKit.lean <out.json> [Module ...]
```

With no modules named it imports the whole kit. `--prefix=Rule30Submission` exports the declarations of
the modules under that root instead of the kit's (a submission compiled as `Rule30Submission`).

It imports `Rule30PrizeKit`, `Ruliology` and `Rule30Equivalents` and writes, for every module of the
kit (names under `Ruliology`, `Rule30Equivalents`, `Rule30PrizeKit`):

* the module, its kit imports and its declarations;
* for every named declaration: its kind, its statement as Lean prints it (and a proposition's
  definition), its docstring, its line, the
  named kit declarations it uses (through auxiliary ones such as `match_` and `proof_` lemmas), and the
  non-standard axioms it depends on (`sorryAx`, `Lean.ofReduceBool`, `Lean.trustCompiler`, any other
  `axiom`), followed through every import, Mathlib included.

Nothing here decides a status: `research/sources/sync.py` loads this file into the rulebook, and the
rulebook's formulas read it.
-/

open Lean Meta

namespace ExportKit

def kitRoots : List Name := [`Ruliology, `Rule30Equivalents, `Rule30PrizeKit]

def isKitModule (roots : List Name) (m : Name) : Bool := roots.any (·.isPrefixOf m)

def standardAxioms : List Name := [`propext, `Classical.choice, `Quot.sound]

def kindOf (env : Environment) (n : Name) : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo d => if d.type.isProp then "proposition" else if isStructure env n then "structure" else "def"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quot"
  | .inductInfo _ => if isStructure env n then "structure" else "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"

/-- Generated and implementation constants: not listed, but followed through for uses. -/
def isAuxiliary (env : Environment) (n : Name) (ci : ConstantInfo) : Bool :=
  n.isInternal || n.isInternalDetail || isAuxRecursor env n || isNoConfusion env n ||
  (ci matches .recInfo _) || (ci matches .ctorInfo _) || (ci matches .quotInfo _) ||
  (match n with
   | .str _ s => s == "eq_def" || s.startsWith "eq_" || s == "injEq" || s == "inj" || s == "sizeOf_spec"
   | _ => false)

def constantsOf (ci : ConstantInfo) : Array Name :=
  let fromType := ci.type.getUsedConstants
  match ci.value? (allowOpaque := true) with
  | some v => fromType ++ v.getUsedConstants
  | none => fromType

structure St where
  bad : Std.HashMap Name (Array Name) := {}
  uses : Std.HashMap Name (Array Name) := {}

/-- The non-standard axioms `n` depends on, memoized over the whole environment. -/
partial def badAxioms (env : Environment) (n : Name) : StateM St (Array Name) := do
  if let some r := (← get).bad.get? n then return r
  -- Mark first, so a cycle (mutual definitions) terminates.
  modify fun s => { s with bad := s.bad.insert n #[] }
  let r ← match env.find? n with
    | none => pure #[]
    | some (.axiomInfo _) => pure (if standardAxioms.contains n then #[] else #[n])
    | some ci => do
      let mut acc : Array Name := #[]
      for c in constantsOf ci do
        for a in (← badAxioms env c) do
          unless acc.contains a do acc := acc.push a
      pure acc
  modify fun s => { s with bad := s.bad.insert n r }
  return r

/-- The named kit constants `n` uses, looking through auxiliary kit constants. -/
partial def namedUses (env : Environment) (roots : List Name) (isNamed : Name → Bool) (n : Name) : StateM St (Array Name) := do
  if let some r := (← get).uses.get? n then return r
  modify fun s => { s with uses := s.uses.insert n #[] }
  let mut acc : Array Name := #[]
  if let some ci := env.find? n then
    for c in constantsOf ci do
      if c == n then continue
      if isNamed c then
        unless acc.contains c do acc := acc.push c
      else if let some idx := env.getModuleIdxFor? c then
        if isKitModule roots env.header.moduleNames[idx.toNat]! then
          for d in (← namedUses env roots isNamed c) do
            unless acc.contains d || d == n do acc := acc.push d
  modify fun s => { s with uses := s.uses.insert n acc }
  return acc

def shorten (s : String) : String :=
  (s.replace "Ruliology.CellularAutomata." "").replace "Rule30Equivalents." ""

def clip (s : String) (n : Nat) : String :=
  if s.length ≤ n then s else (s.take n).toString ++ " …"

unsafe def run (out : System.FilePath) (imports : Array Name) (roots : List Name) : IO Unit := do
  let env ← importModules (imports.map fun m => { module := m }) {} (trustLevel := 1024) (loadExts := true)
  let mods := env.header.moduleNames
  let kitIdx := (List.range mods.size).filter fun i => isKitModule roots mods[i]!
  -- Named constants of the exported modules and of the kit: what a use may point at.
  let roots' := roots ++ kitRoots
  let mut named : Std.HashSet Name := {}
  for i in (List.range mods.size).filter fun i => isKitModule roots' mods[i]! do
    let md := env.header.moduleData[i]!
    for n in md.constNames, ci in md.constants do
      unless isAuxiliary env n ci do named := named.insert n
  let isNamed := fun n => named.contains n
  let ctx : Core.Context := { fileName := "<export>", fileMap := default, maxHeartbeats := 0,
                              options := Options.empty.set `format.width (100 : Nat) }
  let mut st : St := {}
  let mut modulesJ : Array Json := #[]
  let mut declsJ : Array Json := #[]
  for i in kitIdx do
    let m := mods[i]!
    let md := env.header.moduleData[i]!
    let imps := md.imports.filter (fun imp => isKitModule kitRoots imp.module || isKitModule roots imp.module) |>.map (·.module.toString)
    let mut count := 0
    for n in md.constNames, ci in md.constants do
      unless isNamed n do continue
      count := count + 1
      let (bad, st1) := (badAxioms env n).run st
      let (uses, st2) := (namedUses env roots' isNamed n).run st1
      st := st2
      let doc ← findDocString? env n
      let (stmt, line, body) ← (do
          let f ← (Meta.ppExpr ci.type).run'
          let r ← findDeclarationRanges? n
          -- A proposition's definition is what it says: keep its body (an open statement such as Q01).
          let body ← match ci with
            | .defnInfo d => if d.type.isProp then pure (some ((← (Meta.ppExpr d.value).run').pretty 100)) else pure none
            | _ => pure none
          return (f.pretty 100, r.map (·.range.pos.line) |>.getD 0, body) : CoreM (String × Nat × Option String)).toIO ctx { env }
        |>.map (·.1)
      declsJ := declsJ.push <| Json.mkObj [
        ("name", toJson n.toString), ("module", toJson m.toString), ("kind", toJson (kindOf env n ci)),
        ("statement", toJson (clip (shorten stmt) 2000)), ("doc", toJson (doc.map (clip · 1500))),
        ("definition", toJson (body.map fun b => clip (shorten b) 2000)),
        ("line", toJson line), ("uses", toJson (uses.map (·.toString))),
        ("badAxioms", toJson (bad.map (·.toString)))]
    let mdoc := (getModuleDoc? env m).map (·.toList.map (·.doc)) |>.getD []
    modulesJ := modulesJ.push <| Json.mkObj [("name", toJson m.toString), ("imports", toJson imps),
      ("declarations", toJson count), ("moduleDocs", toJson (mdoc.map (clip · 4000)))]
  IO.FS.writeFile out <| Json.compress <| Json.mkObj [("modules", Json.arr modulesJ), ("declarations", Json.arr declsJ)]
  IO.println s!"exported {modulesJ.size} modules, {declsJ.size} declarations to {out}"

end ExportKit

unsafe def main (args : List String) : IO UInt32 := do
  initSearchPath (← findSysroot)
  enableInitializersExecution
  match args with
  | out :: rest =>
    let prefixes := rest.filterMap fun a => if a.startsWith "--prefix=" then some (a.drop 9).toString.toName else none
    let mods := rest.filter (!·.startsWith "--") |>.map (·.toName)
    let mods := if mods.isEmpty then [`Rule30PrizeKit, `Ruliology, `Rule30Equivalents] else mods
    ExportKit.run out mods.toArray (if prefixes.isEmpty then ExportKit.kitRoots else prefixes); return 0
  | _ => IO.eprintln "usage: lake env lean --run ExportKit.lean <out.json> [--prefix=Root]... [Module ...]"; return 2
