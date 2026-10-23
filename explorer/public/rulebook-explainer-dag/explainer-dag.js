/**
 * Portable Explainer DAG — vanilla-JS client for any HTML host. Feature-parity
 * port of rulebook-to-explainer-dag-react:
 *   • Provenance toggle pill (top-right)      — glyphs on/off; OFF still allows dbl-click
 *   • Narration slider (RuleSpeak®·English·Formula) — global, remembered
 *   • Settings gear (top-right)               — checkboxes gating which sections
 *                                               show in the hover card AND the page
 *   • Hover micro-page over cells             — sticky, dialect follows narration
 *   • Double-click a cell                     — opens the full DAG page
 *   • Full field page                         — hero + table link, rule (RuleTree),
 *                                               inputs, consumers (direct+transitive),
 *                                               ground-truth leaves
 * Requires: embedded-graph.js, dag-resolver.js, routing.js, dag.css
 */
(function (global) {
  const R = () => global.EffortlessDagResolver;

  // ════════════════════════════════════════════════════════════════════════
  //  CHROME i18n — the fixed UI text around every page (buttons, section
  //  titles, hover-card labels, tooltips), one dict per language registered in
  //  rulebook-rulespeak-core. This is deliberately NOT where the RuleSpeak®
  //  sentence bodies live: those are rendered per language at build time by the
  //  shared RuleSpeak® engine and baked into embedded-graph.js (rulespeakByLang).
  //  `lang` is set once, from init(), by whatever host page embeds this module —
  //  see tt() below.
  // ════════════════════════════════════════════════════════════════════════
  let lang = "en";
  const CHROME = {
    en: {
      back: "← back", backTitle: "Go back one step",
      home: "🏠 Home", homeTitle: "Leave the explainer — back to the app",
      tablesCrumb: "Tables",
      narrRulespeak: "RuleSpeak®", narrEnglish: "English", narrFormula: "Formula",
      narrRulespeakHint: "The declarative business rule (only if / must / priority)",
      narrEnglishHint: "The formula read as a plain English sentence",
      narrFormulaHint: "The raw spreadsheet-style formula, with clickable fields",
      narrAriaLabel: "How to explain this rule",
      gearTitle: "Settings — choose what shows in the hover card and on the field page",
      gearAriaLabel: "Settings",
      gearPopTitle: "Show in popup & on page",
      gearReset: "Reset to all on",
      elemDesc: "Description", elemDescHint: "The field's plain-language description.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "The declarative business rule.",
      elemEnglish: "English", elemEnglishHint: "The formula read as a plain sentence.",
      elemFormula: "Formula", elemFormulaHint: "The raw spreadsheet-style formula.",
      elemInputs: "Inputs", elemInputsHint: "The fields this one-line function calls.",
      elemConsumers: "Consumers", elemConsumersHint: "Fields whose function calls this one.",
      provOn: "Provenance · ON", provOff: "Provenance · off",
      provOnTitle: "Hide ƒ provenance glyphs. Double-click on cells still opens the DAG.",
      provOffTitle: "Show ƒ provenance glyphs on cells with explorable provenance.",
      cellHintOn: "Hover the badge to peek; double-click to open the full DAG page",
      cellHintOff: "Double-click to see provenance (toggle ƒ glyphs in header)",
      ontologyTitle: "The ontology",
      ontologyLead: "Every table in the rulebook. Click a table to see its columns.",
      fieldsCount: (n) => `${n} fields`, derivedCount: (n) => `${n} derived`, relCount: (n) => `${n} rel`,
      tableNotFound: "Table not found.", fieldNotFound: "Field not found in rulebook.",
      nullable: "nullable",
      hopsFromGround: (n) => (n === 1 ? "1 hop from ground truth" : `${n} hops from ground truth`),
      relationshipPointer: "Relationship pointer", groundTruth: "Ground truth",
      relPointerBody: (link) => `This field is a pointer to ${link}. It is not derived from anything else — it’s the link the rest of the DAG hangs off.`,
      relPointerBodyNoLink: "This field is a pointer to another table. It is not derived from anything else — it’s the link the rest of the DAG hangs off.",
      groundTruthBody: (dt) => `This cell is a leaf. It is <em>written</em> directly to the database (datatype <code>${dt}</code>) and is not computed from anything else. Everything else upstream eventually traces back to values like this one.`,
      openTable: (t) => `Open ${t} →`,
      ruleCardTitle: "This cell is the value of one declarative rule",
      oneLineFnCardTitle: "This cell is the value of one one-line function",
      inRuleSpeak: "In RuleSpeak®", inEnglish: "In English", asFormula: "As a formula",
      mechanicalFlag: "⚠︎ mechanical", mechanicalTitle: "Faithful but clunky wording — a flag for an optional reword pass",
      noRuleRendered: (t) => `No declarative rule was rendered for this ${t} field.`,
      obligations: "Obligations",
      ruleSpeakHintFormula: "This is the same logic the formula encodes, written as a business rule — rendered from the rulebook by the shared RuleSpeak® engine.",
      ruleSpeakHintNoFormula: "Rendered from the rulebook by the shared RuleSpeak® engine.",
      englishHint: "Each underlined field is itself a one-line function. Click any to drill in.",
      noFormulaSentence: (t) => `This ${t} has no spreadsheet formula to read as a sentence — it is a roll-up defined structurally over a relationship. Switch to <strong>RuleSpeak®</strong> to see how it’s defined.`,
      formulaHint: "Each chip is itself a one-line function. Click any chip to drill in.",
      noFormulaAtAll: (t) => `This ${t} has no spreadsheet formula — it is a roll-up defined structurally over a relationship. Switch to <strong>RuleSpeak®</strong> to see how it’s defined.`,
      inputsTitle: "Inputs", inputsLead: "Fields this one-line function calls.",
      groundTruthInline: (dt) => `Ground truth · datatype ${dt}`,
      consumersTitle: "Consumers",
      consumersDirect: "direct", consumersTransitive: "transitive",
      consumersEmpty: "Nothing else in the rulebook references this cell yet.",
      consumersLead: "Fields whose one-line function calls this one.",
      showTransitive: (n) => `Show ${n} transitive consumers (downstream of downstream)`,
      leavesTitle: "Ground truth at the leaves",
      leavesLead: "Ultimately, this cell’s value depends on these raw values. Editing any of these and rebuilding propagates here automatically.",
      hoverGroundTruth: (dt) => `Ground truth — written directly to the database${dt ? ` (datatype <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Relationship pointer — the link the rest of the DAG hangs off.",
      hoverNoRule: "No declarative rule rendered.",
      hoverNoFormula: "No formula — a structural roll-up. See RuleSpeak®.",
      hoverInputs: "Inputs",
      hoverHint: "Double-click the cell to open the full DAG page.",
    },
    ja: {
      back: "← 戻る", backTitle: "1つ前に戻る",
      home: "🏠 ホーム", homeTitle: "エクスプレイナーを離れてアプリに戻る",
      tablesCrumb: "テーブル",
      narrRulespeak: "RuleSpeak®", narrEnglish: "英語", narrFormula: "数式",
      narrRulespeakHint: "宣言的なビジネスルール（only if / must / priority）",
      narrEnglishHint: "数式を平易な英文として読んだもの",
      narrFormulaHint: "生の表計算形式の数式（クリックできるフィールド付き）",
      narrAriaLabel: "このルールの説明方法",
      gearTitle: "設定 — ホバーカードとフィールドページに表示する項目を選択",
      gearAriaLabel: "設定",
      gearPopTitle: "ポップアップとページに表示する項目",
      gearReset: "すべてオンに戻す",
      elemDesc: "説明", elemDescHint: "フィールドの平易な説明文。",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "宣言的なビジネスルール。",
      elemEnglish: "英語", elemEnglishHint: "数式を平易な文として読んだもの。",
      elemFormula: "数式", elemFormulaHint: "生の表計算形式の数式。",
      elemInputs: "入力", elemInputsHint: "この一行関数が呼び出しているフィールド。",
      elemConsumers: "参照元", elemConsumersHint: "この関数を呼び出しているフィールド。",
      provOn: "由来表示 · ON", provOff: "由来表示 · off",
      provOnTitle: "ƒ 由来バッジを非表示にします。セルのダブルクリックではDAGが開きます。",
      provOffTitle: "由来を確認できるセルに ƒ バッジを表示します。",
      cellHintOn: "バッジにカーソルを合わせるとプレビュー、ダブルクリックでDAGページを開きます",
      cellHintOff: "ダブルクリックで由来を確認（ヘッダーで ƒ バッジの表示を切替）",
      ontologyTitle: "オントロジー",
      ontologyLead: "ルールブック内のすべてのテーブル。テーブルをクリックすると列を確認できます。",
      fieldsCount: (n) => `${n} フィールド`, derivedCount: (n) => `${n} 算出`, relCount: (n) => `${n} リレーション`,
      tableNotFound: "テーブルが見つかりません。", fieldNotFound: "ルールブックにこのフィールドは見つかりません。",
      nullable: "null許可",
      hopsFromGround: (n) => `根拠データから ${n} ホップ`,
      relationshipPointer: "リレーションのポインタ", groundTruth: "根拠データ",
      relPointerBody: (link) => `このフィールドは ${link} へのポインタです。他の何かから導出されたものではなく、DAGの残りがぶら下がるリンクです。`,
      relPointerBodyNoLink: "このフィールドは別テーブルへのポインタです。他の何かから導出されたものではなく、DAGの残りがぶら下がるリンクです。",
      groundTruthBody: (dt) => `このセルは末端です。データベースに直接<em>書き込まれた</em>値（データ型 <code>${dt}</code>）で、他の何からも算出されていません。この先の上流はすべて、最終的にこのような値にたどり着きます。`,
      openTable: (t) => `${t} を開く →`,
      ruleCardTitle: "このセルは1つの宣言的ルールの値です",
      oneLineFnCardTitle: "このセルは1つの一行関数の値です",
      inRuleSpeak: "RuleSpeak® では", inEnglish: "英語では", asFormula: "数式として",
      mechanicalFlag: "⚠︎ 機械的", mechanicalTitle: "意味は正確ですが表現がぎこちない箇所です — 表現の見直し候補",
      noRuleRendered: (t) => `この ${t} フィールドには宣言的ルールが生成されませんでした。`,
      obligations: "義務（Obligations）",
      ruleSpeakHintFormula: "これは数式が表しているのと同じロジックを、ビジネスルールとして書き直したものです — 共有の RuleSpeak® エンジンがルールブックから生成しています。",
      ruleSpeakHintNoFormula: "共有の RuleSpeak® エンジンがルールブックから生成しています。",
      englishHint: "下線付きの各フィールドもそれ自体が一行関数です。クリックすると詳細を確認できます。",
      noFormulaSentence: (t) => `この ${t} には文として読める数式がありません — リレーションに基づいて構造的に定義されたロールアップです。定義内容を確認するには <strong>RuleSpeak®</strong> に切り替えてください。`,
      formulaHint: "各チップもそれ自体が一行関数です。クリックすると詳細を確認できます。",
      noFormulaAtAll: (t) => `この ${t} には数式がありません — リレーションに基づいて構造的に定義されたロールアップです。定義内容を確認するには <strong>RuleSpeak®</strong> に切り替えてください。`,
      inputsTitle: "入力", inputsLead: "この一行関数が呼び出しているフィールド。",
      groundTruthInline: (dt) => `根拠データ · データ型 ${dt}`,
      consumersTitle: "参照元",
      consumersDirect: "直接", consumersTransitive: "間接",
      consumersEmpty: "ルールブック内で、このセルを参照しているものは他にありません。",
      consumersLead: "この一行関数を呼び出しているフィールド。",
      showTransitive: (n) => `間接的な参照元を ${n} 件表示（さらに下流の下流）`,
      leavesTitle: "末端の根拠データ",
      leavesLead: "このセルの値は最終的にこれらの生データに依存しています。これらのいずれかを編集して再ビルドすると、自動的にここまで反映されます。",
      hoverGroundTruth: (dt) => `根拠データ — データベースに直接書き込まれます${dt ? `（データ型 <code>${dt}</code>）` : ""}。`,
      hoverRelPointer: "リレーションのポインタ — DAGの残りがぶら下がるリンクです。",
      hoverNoRule: "宣言的ルールは生成されませんでした。",
      hoverNoFormula: "数式がありません — 構造的なロールアップです。RuleSpeak® を参照してください。",
      hoverInputs: "入力",
      hoverHint: "セルをダブルクリックすると、DAGページ全体が開きます。",
      type_raw: "根拠データ", type_calculated: "算出", type_aggregation: "集計", type_relationship: "リレーション", type_lookup: "参照",
    },
    de: {
      back: "← zurück", backTitle: "Einen Schritt zurück",
      home: "🏠 Start", homeTitle: "Den Explainer verlassen — zurück zur App",
      tablesCrumb: "Tabellen",
      narrRulespeak: "RuleSpeak®", narrEnglish: "Englisch", narrFormula: "Formel",
      narrRulespeakHint: "Die deklarative Geschäftsregel (nur wenn / muss / Priorität)",
      narrEnglishHint: "Die Formel als einfacher englischer Satz gelesen",
      narrFormulaHint: "Die rohe Formel im Tabellenkalkulationsstil, mit anklickbaren Feldern",
      narrAriaLabel: "Wie diese Regel erklärt wird",
      gearTitle: "Einstellungen — wählen, was in der Hover-Karte und auf der Feldseite erscheint",
      gearAriaLabel: "Einstellungen",
      gearPopTitle: "Im Popup und auf der Seite anzeigen",
      gearReset: "Alles wieder einschalten",
      elemDesc: "Beschreibung", elemDescHint: "Die Beschreibung des Feldes in Alltagssprache.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "Die deklarative Geschäftsregel.",
      elemEnglish: "Englisch", elemEnglishHint: "Die Formel als einfacher Satz gelesen.",
      elemFormula: "Formel", elemFormulaHint: "Die rohe Formel im Tabellenkalkulationsstil.",
      elemInputs: "Eingaben", elemInputsHint: "Die Felder, die diese einzeilige Funktion aufruft.",
      elemConsumers: "Verwender", elemConsumersHint: "Felder, deren Funktion diese aufruft.",
      provOn: "Herkunft · AN", provOff: "Herkunft · aus",
      provOnTitle: "ƒ-Herkunftssymbole ausblenden. Ein Doppelklick auf Zellen öffnet den DAG weiterhin.",
      provOffTitle: "ƒ-Herkunftssymbole an Zellen mit nachvollziehbarer Herkunft anzeigen.",
      cellHintOn: "Symbol überfahren für eine Vorschau; Doppelklick öffnet die vollständige DAG-Seite",
      cellHintOff: "Doppelklick zeigt die Herkunft (ƒ-Symbole in der Kopfzeile umschalten)",
      ontologyTitle: "Die Ontologie",
      ontologyLead: "Jede Tabelle im Regelbuch. Klicken Sie auf eine Tabelle, um ihre Spalten zu sehen.",
      fieldsCount: (n) => `${n} Felder`, derivedCount: (n) => `${n} abgeleitet`, relCount: (n) => `${n} Bez.`,
      tableNotFound: "Tabelle nicht gefunden.", fieldNotFound: "Feld im Regelbuch nicht gefunden.",
      nullable: "NULL erlaubt",
      hopsFromGround: (n) => (n === 1 ? "1 Schritt von den Grunddaten" : `${n} Schritte von den Grunddaten`),
      relationshipPointer: "Beziehungszeiger", groundTruth: "Grunddaten",
      relPointerBody: (link) => `Dieses Feld ist ein Zeiger auf ${link}. Es wird aus nichts anderem abgeleitet — es ist die Verknüpfung, an der der Rest des DAG hängt.`,
      relPointerBodyNoLink: "Dieses Feld ist ein Zeiger auf eine andere Tabelle. Es wird aus nichts anderem abgeleitet — es ist die Verknüpfung, an der der Rest des DAG hängt.",
      groundTruthBody: (dt) => `Diese Zelle ist ein Blatt. Sie wird direkt in die Datenbank <em>geschrieben</em> (Datentyp <code>${dt}</code>) und aus nichts anderem berechnet. Alles andere weiter oben geht letztlich auf Werte wie diesen zurück.`,
      openTable: (t) => `${t} öffnen →`,
      ruleCardTitle: "Diese Zelle ist der Wert einer deklarativen Regel",
      oneLineFnCardTitle: "Diese Zelle ist der Wert einer einzeiligen Funktion",
      inRuleSpeak: "In RuleSpeak®", inEnglish: "Auf Englisch", asFormula: "Als Formel",
      mechanicalFlag: "⚠︎ mechanisch", mechanicalTitle: "Inhaltlich korrekt, aber holprig formuliert — ein Hinweis für eine optionale Überarbeitung",
      noRuleRendered: (t) => `Für dieses ${t}-Feld wurde keine deklarative Regel erzeugt.`,
      obligations: "Verpflichtungen",
      ruleSpeakHintFormula: "Dies ist dieselbe Logik, die die Formel ausdrückt, als Geschäftsregel formuliert — von der gemeinsamen RuleSpeak®-Engine aus dem Regelbuch erzeugt.",
      ruleSpeakHintNoFormula: "Von der gemeinsamen RuleSpeak®-Engine aus dem Regelbuch erzeugt.",
      englishHint: "Jedes unterstrichene Feld ist selbst eine einzeilige Funktion. Klicken Sie darauf, um tiefer einzusteigen.",
      noFormulaSentence: (t) => `Dieses ${t} hat keine Tabellenformel, die sich als Satz lesen ließe — es ist eine Aggregation, strukturell über eine Beziehung definiert. Wechseln Sie zu <strong>RuleSpeak®</strong>, um die Definition zu sehen.`,
      formulaHint: "Jeder Chip ist selbst eine einzeilige Funktion. Klicken Sie auf einen Chip, um tiefer einzusteigen.",
      noFormulaAtAll: (t) => `Dieses ${t} hat keine Tabellenformel — es ist eine Aggregation, strukturell über eine Beziehung definiert. Wechseln Sie zu <strong>RuleSpeak®</strong>, um die Definition zu sehen.`,
      inputsTitle: "Eingaben", inputsLead: "Felder, die diese einzeilige Funktion aufruft.",
      groundTruthInline: (dt) => `Grunddaten · Datentyp ${dt}`,
      consumersTitle: "Verwender",
      consumersDirect: "direkt", consumersTransitive: "transitiv",
      consumersEmpty: "Nichts anderes im Regelbuch verweist bisher auf diese Zelle.",
      consumersLead: "Felder, deren einzeilige Funktion diese aufruft.",
      showTransitive: (n) => `${n} transitive Verwender anzeigen (weiter stromabwärts)`,
      leavesTitle: "Grunddaten an den Blättern",
      leavesLead: "Letztlich hängt der Wert dieser Zelle von diesen Rohwerten ab. Wird einer davon geändert und neu gebaut, wirkt sich das automatisch hier aus.",
      hoverGroundTruth: (dt) => `Grunddaten — direkt in die Datenbank geschrieben${dt ? ` (Datentyp <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Beziehungszeiger — die Verknüpfung, an der der Rest des DAG hängt.",
      hoverNoRule: "Keine deklarative Regel erzeugt.",
      hoverNoFormula: "Keine Formel — eine strukturelle Aggregation. Siehe RuleSpeak®.",
      hoverInputs: "Eingaben",
      hoverHint: "Doppelklick auf die Zelle öffnet die vollständige DAG-Seite.",
      type_raw: "Grunddaten", type_calculated: "Berechnet", type_aggregation: "Aggregation", type_relationship: "Beziehung", type_lookup: "Nachschlagen",
    },
    es: {
      back: "← atrás", backTitle: "Volver un paso",
      home: "🏠 Inicio", homeTitle: "Salir del explicador — volver a la aplicación",
      tablesCrumb: "Tablas",
      narrRulespeak: "RuleSpeak®", narrEnglish: "Inglés", narrFormula: "Fórmula",
      narrRulespeakHint: "La regla de negocio declarativa (solo si / debe / prioridad)",
      narrEnglishHint: "La fórmula leída como una oración sencilla en inglés",
      narrFormulaHint: "La fórmula en bruto, estilo hoja de cálculo, con campos clicables",
      narrAriaLabel: "Cómo explicar esta regla",
      gearTitle: "Configuración — elige qué se muestra en la tarjeta emergente y en la página del campo",
      gearAriaLabel: "Configuración",
      gearPopTitle: "Mostrar en la ventana emergente y en la página",
      gearReset: "Volver a activar todo",
      elemDesc: "Descripción", elemDescHint: "La descripción del campo en lenguaje sencillo.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "La regla de negocio declarativa.",
      elemEnglish: "Inglés", elemEnglishHint: "La fórmula leída como una oración sencilla.",
      elemFormula: "Fórmula", elemFormulaHint: "La fórmula en bruto, estilo hoja de cálculo.",
      elemInputs: "Entradas", elemInputsHint: "Los campos a los que llama esta función de una línea.",
      elemConsumers: "Consumidores", elemConsumersHint: "Campos cuya función llama a esta.",
      provOn: "Procedencia · SÍ", provOff: "Procedencia · no",
      provOnTitle: "Ocultar los glifos ƒ de procedencia. El doble clic en las celdas sigue abriendo el DAG.",
      provOffTitle: "Mostrar los glifos ƒ de procedencia en las celdas con procedencia explorable.",
      cellHintOn: "Pasa el cursor sobre la insignia para ver un avance; doble clic para abrir la página DAG completa",
      cellHintOff: "Doble clic para ver la procedencia (activa los glifos ƒ en la cabecera)",
      ontologyTitle: "La ontología",
      ontologyLead: "Todas las tablas del libro de reglas. Haz clic en una tabla para ver sus columnas.",
      fieldsCount: (n) => `${n} campos`, derivedCount: (n) => `${n} derivados`, relCount: (n) => `${n} rel.`,
      tableNotFound: "Tabla no encontrada.", fieldNotFound: "Campo no encontrado en el libro de reglas.",
      nullable: "admite nulos",
      hopsFromGround: (n) => (n === 1 ? "a 1 salto de los datos base" : `a ${n} saltos de los datos base`),
      relationshipPointer: "Puntero de relación", groundTruth: "Datos base",
      relPointerBody: (link) => `Este campo es un puntero a ${link}. No se deriva de nada más: es el vínculo del que cuelga el resto del DAG.`,
      relPointerBodyNoLink: "Este campo es un puntero a otra tabla. No se deriva de nada más: es el vínculo del que cuelga el resto del DAG.",
      groundTruthBody: (dt) => `Esta celda es una hoja. Se <em>escribe</em> directamente en la base de datos (tipo de dato <code>${dt}</code>) y no se calcula a partir de nada más. Todo lo demás, aguas arriba, se remonta en última instancia a valores como este.`,
      openTable: (t) => `Abrir ${t} →`,
      ruleCardTitle: "Esta celda es el valor de una regla declarativa",
      oneLineFnCardTitle: "Esta celda es el valor de una función de una línea",
      inRuleSpeak: "En RuleSpeak®", inEnglish: "En inglés", asFormula: "Como fórmula",
      mechanicalFlag: "⚠︎ mecánico", mechanicalTitle: "Fiel pero con una redacción torpe — una señal para una revisión opcional",
      noRuleRendered: (t) => `No se generó ninguna regla declarativa para este campo ${t}.`,
      obligations: "Obligaciones",
      ruleSpeakHintFormula: "Es la misma lógica que codifica la fórmula, escrita como regla de negocio — generada a partir del libro de reglas por el motor compartido de RuleSpeak®.",
      ruleSpeakHintNoFormula: "Generada a partir del libro de reglas por el motor compartido de RuleSpeak®.",
      englishHint: "Cada campo subrayado es a su vez una función de una línea. Haz clic en cualquiera para profundizar.",
      noFormulaSentence: (t) => `Este ${t} no tiene una fórmula de hoja de cálculo que leer como oración: es un acumulado definido estructuralmente sobre una relación. Cambia a <strong>RuleSpeak®</strong> para ver cómo se define.`,
      formulaHint: "Cada chip es a su vez una función de una línea. Haz clic en cualquier chip para profundizar.",
      noFormulaAtAll: (t) => `Este ${t} no tiene fórmula de hoja de cálculo: es un acumulado definido estructuralmente sobre una relación. Cambia a <strong>RuleSpeak®</strong> para ver cómo se define.`,
      inputsTitle: "Entradas", inputsLead: "Campos a los que llama esta función de una línea.",
      groundTruthInline: (dt) => `Datos base · tipo de dato ${dt}`,
      consumersTitle: "Consumidores",
      consumersDirect: "directos", consumersTransitive: "transitivos",
      consumersEmpty: "Nada más en el libro de reglas hace referencia a esta celda todavía.",
      consumersLead: "Campos cuya función de una línea llama a esta.",
      showTransitive: (n) => `Mostrar ${n} consumidores transitivos (más abajo en la cadena)`,
      leavesTitle: "Datos base en las hojas",
      leavesLead: "En última instancia, el valor de esta celda depende de estos valores en bruto. Editar cualquiera de ellos y reconstruir se propaga aquí automáticamente.",
      hoverGroundTruth: (dt) => `Datos base — escritos directamente en la base de datos${dt ? ` (tipo de dato <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Puntero de relación — el vínculo del que cuelga el resto del DAG.",
      hoverNoRule: "No se generó ninguna regla declarativa.",
      hoverNoFormula: "Sin fórmula — un acumulado estructural. Consulta RuleSpeak®.",
      hoverInputs: "Entradas",
      hoverHint: "Haz doble clic en la celda para abrir la página DAG completa.",
      type_raw: "Datos base", type_calculated: "Calculado", type_aggregation: "Agregación", type_relationship: "Relación", type_lookup: "Búsqueda",
    },
    fr: {
      back: "← retour", backTitle: "Revenir d’une étape",
      home: "🏠 Accueil", homeTitle: "Quitter l’explorateur — retour à l’application",
      tablesCrumb: "Tables",
      narrRulespeak: "RuleSpeak®", narrEnglish: "Anglais", narrFormula: "Formule",
      narrRulespeakHint: "La règle métier déclarative (seulement si / doit / priorité)",
      narrEnglishHint: "La formule lue comme une phrase simple en anglais",
      narrFormulaHint: "La formule brute, façon tableur, avec des champs cliquables",
      narrAriaLabel: "Comment expliquer cette règle",
      gearTitle: "Paramètres — choisissez ce qui s’affiche dans la carte de survol et sur la page du champ",
      gearAriaLabel: "Paramètres",
      gearPopTitle: "Afficher dans la fenêtre et sur la page",
      gearReset: "Tout réactiver",
      elemDesc: "Description", elemDescHint: "La description du champ en langage courant.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "La règle métier déclarative.",
      elemEnglish: "Anglais", elemEnglishHint: "La formule lue comme une phrase simple.",
      elemFormula: "Formule", elemFormulaHint: "La formule brute, façon tableur.",
      elemInputs: "Entrées", elemInputsHint: "Les champs appelés par cette fonction d’une ligne.",
      elemConsumers: "Consommateurs", elemConsumersHint: "Les champs dont la fonction appelle celle-ci.",
      provOn: "Provenance · ACTIVÉE", provOff: "Provenance · désactivée",
      provOnTitle: "Masquer les glyphes ƒ de provenance. Un double-clic sur les cellules ouvre toujours le DAG.",
      provOffTitle: "Afficher les glyphes ƒ de provenance sur les cellules dont la provenance est explorable.",
      cellHintOn: "Survolez le badge pour un aperçu ; double-cliquez pour ouvrir la page DAG complète",
      cellHintOff: "Double-cliquez pour voir la provenance (activez les glyphes ƒ dans l’en-tête)",
      ontologyTitle: "L’ontologie",
      ontologyLead: "Toutes les tables du livre de règles. Cliquez sur une table pour voir ses colonnes.",
      fieldsCount: (n) => `${n} champs`, derivedCount: (n) => `${n} dérivés`, relCount: (n) => `${n} rel.`,
      tableNotFound: "Table introuvable.", fieldNotFound: "Champ introuvable dans le livre de règles.",
      nullable: "NULL autorisé",
      hopsFromGround: (n) => (n === 1 ? "à 1 saut des données de base" : `à ${n} sauts des données de base`),
      relationshipPointer: "Pointeur de relation", groundTruth: "Données de base",
      relPointerBody: (link) => `Ce champ est un pointeur vers ${link}. Il n’est dérivé de rien d’autre — c’est le lien auquel se rattache le reste du DAG.`,
      relPointerBodyNoLink: "Ce champ est un pointeur vers une autre table. Il n’est dérivé de rien d’autre — c’est le lien auquel se rattache le reste du DAG.",
      groundTruthBody: (dt) => `Cette cellule est une feuille. Elle est <em>écrite</em> directement dans la base de données (type <code>${dt}</code>) et n’est calculée à partir de rien d’autre. Tout le reste, en amont, remonte finalement à des valeurs comme celle-ci.`,
      openTable: (t) => `Ouvrir ${t} →`,
      ruleCardTitle: "Cette cellule est la valeur d’une règle déclarative",
      oneLineFnCardTitle: "Cette cellule est la valeur d’une fonction d’une ligne",
      inRuleSpeak: "En RuleSpeak®", inEnglish: "En anglais", asFormula: "Sous forme de formule",
      mechanicalFlag: "⚠︎ mécanique", mechanicalTitle: "Fidèle mais formulé maladroitement — un signal pour une reformulation facultative",
      noRuleRendered: (t) => `Aucune règle déclarative n’a été générée pour ce champ ${t}.`,
      obligations: "Obligations",
      ruleSpeakHintFormula: "C’est la même logique que celle de la formule, écrite comme une règle métier — générée à partir du livre de règles par le moteur RuleSpeak® partagé.",
      ruleSpeakHintNoFormula: "Générée à partir du livre de règles par le moteur RuleSpeak® partagé.",
      englishHint: "Chaque champ souligné est lui-même une fonction d’une ligne. Cliquez dessus pour approfondir.",
      noFormulaSentence: (t) => `Ce ${t} n’a pas de formule de tableur à lire comme une phrase — c’est un cumul défini structurellement sur une relation. Passez à <strong>RuleSpeak®</strong> pour voir sa définition.`,
      formulaHint: "Chaque puce est elle-même une fonction d’une ligne. Cliquez sur une puce pour approfondir.",
      noFormulaAtAll: (t) => `Ce ${t} n’a pas de formule de tableur — c’est un cumul défini structurellement sur une relation. Passez à <strong>RuleSpeak®</strong> pour voir sa définition.`,
      inputsTitle: "Entrées", inputsLead: "Champs appelés par cette fonction d’une ligne.",
      groundTruthInline: (dt) => `Données de base · type ${dt}`,
      consumersTitle: "Consommateurs",
      consumersDirect: "directs", consumersTransitive: "transitifs",
      consumersEmpty: "Rien d’autre dans le livre de règles ne fait encore référence à cette cellule.",
      consumersLead: "Champs dont la fonction d’une ligne appelle celle-ci.",
      showTransitive: (n) => `Afficher ${n} consommateurs transitifs (en aval de l’aval)`,
      leavesTitle: "Données de base aux feuilles",
      leavesLead: "En fin de compte, la valeur de cette cellule dépend de ces valeurs brutes. Modifier l’une d’elles puis reconstruire se propage ici automatiquement.",
      hoverGroundTruth: (dt) => `Données de base — écrites directement dans la base de données${dt ? ` (type <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Pointeur de relation — le lien auquel se rattache le reste du DAG.",
      hoverNoRule: "Aucune règle déclarative générée.",
      hoverNoFormula: "Pas de formule — un cumul structurel. Voir RuleSpeak®.",
      hoverInputs: "Entrées",
      hoverHint: "Double-cliquez sur la cellule pour ouvrir la page DAG complète.",
      type_raw: "Données de base", type_calculated: "Calculé", type_aggregation: "Agrégation", type_relationship: "Relation", type_lookup: "Recherche",
    },
    pt: {
      back: "← voltar", backTitle: "Voltar um passo",
      home: "🏠 Início", homeTitle: "Sair do explicador — voltar ao aplicativo",
      tablesCrumb: "Tabelas",
      narrRulespeak: "RuleSpeak®", narrEnglish: "Inglês", narrFormula: "Fórmula",
      narrRulespeakHint: "A regra de negócio declarativa (somente se / deve / prioridade)",
      narrEnglishHint: "A fórmula lida como uma frase simples em inglês",
      narrFormulaHint: "A fórmula bruta, estilo planilha, com campos clicáveis",
      narrAriaLabel: "Como explicar esta regra",
      gearTitle: "Configurações — escolha o que aparece no cartão flutuante e na página do campo",
      gearAriaLabel: "Configurações",
      gearPopTitle: "Mostrar no popup e na página",
      gearReset: "Reativar tudo",
      elemDesc: "Descrição", elemDescHint: "A descrição do campo em linguagem simples.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "A regra de negócio declarativa.",
      elemEnglish: "Inglês", elemEnglishHint: "A fórmula lida como uma frase simples.",
      elemFormula: "Fórmula", elemFormulaHint: "A fórmula bruta, estilo planilha.",
      elemInputs: "Entradas", elemInputsHint: "Os campos que esta função de uma linha chama.",
      elemConsumers: "Consumidores", elemConsumersHint: "Campos cuja função chama esta.",
      provOn: "Proveniência · LIGADA", provOff: "Proveniência · desligada",
      provOnTitle: "Ocultar os glifos ƒ de proveniência. O clique duplo nas células continua abrindo o DAG.",
      provOffTitle: "Mostrar os glifos ƒ de proveniência nas células com proveniência explorável.",
      cellHintOn: "Passe o cursor sobre o selo para uma prévia; clique duas vezes para abrir a página DAG completa",
      cellHintOff: "Clique duas vezes para ver a proveniência (ative os glifos ƒ no cabeçalho)",
      ontologyTitle: "A ontologia",
      ontologyLead: "Todas as tabelas do livro de regras. Clique em uma tabela para ver suas colunas.",
      fieldsCount: (n) => `${n} campos`, derivedCount: (n) => `${n} derivados`, relCount: (n) => `${n} rel.`,
      tableNotFound: "Tabela não encontrada.", fieldNotFound: "Campo não encontrado no livro de regras.",
      nullable: "aceita nulo",
      hopsFromGround: (n) => (n === 1 ? "a 1 salto dos dados de base" : `a ${n} saltos dos dados de base`),
      relationshipPointer: "Ponteiro de relação", groundTruth: "Dados de base",
      relPointerBody: (link) => `Este campo é um ponteiro para ${link}. Não é derivado de nada mais — é o vínculo do qual o resto do DAG depende.`,
      relPointerBodyNoLink: "Este campo é um ponteiro para outra tabela. Não é derivado de nada mais — é o vínculo do qual o resto do DAG depende.",
      groundTruthBody: (dt) => `Esta célula é uma folha. Ela é <em>gravada</em> diretamente no banco de dados (tipo de dado <code>${dt}</code>) e não é calculada a partir de nada mais. Todo o resto, a montante, remonta afinal a valores como este.`,
      openTable: (t) => `Abrir ${t} →`,
      ruleCardTitle: "Esta célula é o valor de uma regra declarativa",
      oneLineFnCardTitle: "Esta célula é o valor de uma função de uma linha",
      inRuleSpeak: "Em RuleSpeak®", inEnglish: "Em inglês", asFormula: "Como fórmula",
      mechanicalFlag: "⚠︎ mecânico", mechanicalTitle: "Fiel, mas com redação truncada — um sinal para uma revisão opcional",
      noRuleRendered: (t) => `Nenhuma regra declarativa foi gerada para este campo ${t}.`,
      obligations: "Obrigações",
      ruleSpeakHintFormula: "É a mesma lógica que a fórmula codifica, escrita como regra de negócio — gerada a partir do livro de regras pelo mecanismo compartilhado do RuleSpeak®.",
      ruleSpeakHintNoFormula: "Gerada a partir do livro de regras pelo mecanismo compartilhado do RuleSpeak®.",
      englishHint: "Cada campo sublinhado é, ele próprio, uma função de uma linha. Clique em qualquer um para detalhar.",
      noFormulaSentence: (t) => `Este ${t} não tem fórmula de planilha para ler como frase — é um agregado definido estruturalmente sobre uma relação. Mude para <strong>RuleSpeak®</strong> para ver como é definido.`,
      formulaHint: "Cada chip é, ele próprio, uma função de uma linha. Clique em qualquer chip para detalhar.",
      noFormulaAtAll: (t) => `Este ${t} não tem fórmula de planilha — é um agregado definido estruturalmente sobre uma relação. Mude para <strong>RuleSpeak®</strong> para ver como é definido.`,
      inputsTitle: "Entradas", inputsLead: "Campos que esta função de uma linha chama.",
      groundTruthInline: (dt) => `Dados de base · tipo de dado ${dt}`,
      consumersTitle: "Consumidores",
      consumersDirect: "diretos", consumersTransitive: "transitivos",
      consumersEmpty: "Nada mais no livro de regras faz referência a esta célula ainda.",
      consumersLead: "Campos cuja função de uma linha chama esta.",
      showTransitive: (n) => `Mostrar ${n} consumidores transitivos (mais abaixo na cadeia)`,
      leavesTitle: "Dados de base nas folhas",
      leavesLead: "Em última instância, o valor desta célula depende destes valores brutos. Editar qualquer um deles e reconstruir se propaga aqui automaticamente.",
      hoverGroundTruth: (dt) => `Dados de base — gravados diretamente no banco de dados${dt ? ` (tipo de dado <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Ponteiro de relação — o vínculo do qual o resto do DAG depende.",
      hoverNoRule: "Nenhuma regra declarativa gerada.",
      hoverNoFormula: "Sem fórmula — um agregado estrutural. Veja RuleSpeak®.",
      hoverInputs: "Entradas",
      hoverHint: "Clique duas vezes na célula para abrir a página DAG completa.",
      type_raw: "Dados de base", type_calculated: "Calculado", type_aggregation: "Agregação", type_relationship: "Relação", type_lookup: "Consulta",
    },
    it: {
      back: "← indietro", backTitle: "Torna indietro di un passo",
      home: "🏠 Home", homeTitle: "Esci dall’explainer — torna all’app",
      tablesCrumb: "Tabelle",
      narrRulespeak: "RuleSpeak®", narrEnglish: "Inglese", narrFormula: "Formula",
      narrRulespeakHint: "La regola di business dichiarativa (solo se / deve / priorità)",
      narrEnglishHint: "La formula letta come una semplice frase in inglese",
      narrFormulaHint: "La formula grezza, in stile foglio di calcolo, con campi cliccabili",
      narrAriaLabel: "Come spiegare questa regola",
      gearTitle: "Impostazioni — scegli cosa mostrare nella scheda al passaggio del mouse e nella pagina del campo",
      gearAriaLabel: "Impostazioni",
      gearPopTitle: "Mostra nel popup e nella pagina",
      gearReset: "Riattiva tutto",
      elemDesc: "Descrizione", elemDescHint: "La descrizione del campo in linguaggio semplice.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "La regola di business dichiarativa.",
      elemEnglish: "Inglese", elemEnglishHint: "La formula letta come una semplice frase.",
      elemFormula: "Formula", elemFormulaHint: "La formula grezza, in stile foglio di calcolo.",
      elemInputs: "Input", elemInputsHint: "I campi richiamati da questa funzione di una riga.",
      elemConsumers: "Utilizzatori", elemConsumersHint: "Campi la cui funzione richiama questa.",
      provOn: "Provenienza · ON", provOff: "Provenienza · off",
      provOnTitle: "Nascondi i glifi ƒ di provenienza. Il doppio clic sulle celle apre comunque il DAG.",
      provOffTitle: "Mostra i glifi ƒ di provenienza sulle celle con provenienza esplorabile.",
      cellHintOn: "Passa sopra il badge per un’anteprima; doppio clic per aprire la pagina DAG completa",
      cellHintOff: "Doppio clic per vedere la provenienza (attiva i glifi ƒ nell’intestazione)",
      ontologyTitle: "L’ontologia",
      ontologyLead: "Ogni tabella del libro delle regole. Fai clic su una tabella per vederne le colonne.",
      fieldsCount: (n) => `${n} campi`, derivedCount: (n) => `${n} derivati`, relCount: (n) => `${n} rel.`,
      tableNotFound: "Tabella non trovata.", fieldNotFound: "Campo non trovato nel libro delle regole.",
      nullable: "ammette null",
      hopsFromGround: (n) => (n === 1 ? "a 1 passaggio dai dati di base" : `a ${n} passaggi dai dati di base`),
      relationshipPointer: "Puntatore di relazione", groundTruth: "Dati di base",
      relPointerBody: (link) => `Questo campo è un puntatore a ${link}. Non deriva da nient’altro — è il collegamento a cui è appeso il resto del DAG.`,
      relPointerBodyNoLink: "Questo campo è un puntatore a un’altra tabella. Non deriva da nient’altro — è il collegamento a cui è appeso il resto del DAG.",
      groundTruthBody: (dt) => `Questa cella è una foglia. Viene <em>scritta</em> direttamente nel database (tipo di dato <code>${dt}</code>) e non è calcolata da nient’altro. Tutto il resto, a monte, risale in definitiva a valori come questo.`,
      openTable: (t) => `Apri ${t} →`,
      ruleCardTitle: "Questa cella è il valore di una regola dichiarativa",
      oneLineFnCardTitle: "Questa cella è il valore di una funzione di una riga",
      inRuleSpeak: "In RuleSpeak®", inEnglish: "In inglese", asFormula: "Come formula",
      mechanicalFlag: "⚠︎ meccanico", mechanicalTitle: "Fedele ma formulato in modo goffo — un segnale per una revisione facoltativa",
      noRuleRendered: (t) => `Non è stata generata alcuna regola dichiarativa per questo campo ${t}.`,
      obligations: "Obblighi",
      ruleSpeakHintFormula: "È la stessa logica codificata dalla formula, scritta come regola di business — generata dal libro delle regole dal motore RuleSpeak® condiviso.",
      ruleSpeakHintNoFormula: "Generata dal libro delle regole dal motore RuleSpeak® condiviso.",
      englishHint: "Ogni campo sottolineato è a sua volta una funzione di una riga. Fai clic su uno qualsiasi per approfondire.",
      noFormulaSentence: (t) => `Questo ${t} non ha una formula da foglio di calcolo da leggere come frase — è un aggregato definito strutturalmente su una relazione. Passa a <strong>RuleSpeak®</strong> per vedere come è definito.`,
      formulaHint: "Ogni chip è a sua volta una funzione di una riga. Fai clic su un chip per approfondire.",
      noFormulaAtAll: (t) => `Questo ${t} non ha una formula da foglio di calcolo — è un aggregato definito strutturalmente su una relazione. Passa a <strong>RuleSpeak®</strong> per vedere come è definito.`,
      inputsTitle: "Input", inputsLead: "Campi richiamati da questa funzione di una riga.",
      groundTruthInline: (dt) => `Dati di base · tipo di dato ${dt}`,
      consumersTitle: "Utilizzatori",
      consumersDirect: "diretti", consumersTransitive: "transitivi",
      consumersEmpty: "Nient’altro nel libro delle regole fa ancora riferimento a questa cella.",
      consumersLead: "Campi la cui funzione di una riga richiama questa.",
      showTransitive: (n) => `Mostra ${n} utilizzatori transitivi (più a valle)`,
      leavesTitle: "Dati di base alle foglie",
      leavesLead: "In definitiva, il valore di questa cella dipende da questi valori grezzi. Modificarne uno e ricompilare si propaga qui automaticamente.",
      hoverGroundTruth: (dt) => `Dati di base — scritti direttamente nel database${dt ? ` (tipo di dato <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Puntatore di relazione — il collegamento a cui è appeso il resto del DAG.",
      hoverNoRule: "Nessuna regola dichiarativa generata.",
      hoverNoFormula: "Nessuna formula — un aggregato strutturale. Vedi RuleSpeak®.",
      hoverInputs: "Input",
      hoverHint: "Fai doppio clic sulla cella per aprire la pagina DAG completa.",
      type_raw: "Dati di base", type_calculated: "Calcolato", type_aggregation: "Aggregazione", type_relationship: "Relazione", type_lookup: "Ricerca",
    },
    nl: {
      back: "← terug", backTitle: "Eén stap terug",
      home: "🏠 Start", homeTitle: "De explainer verlaten — terug naar de app",
      tablesCrumb: "Tabellen",
      narrRulespeak: "RuleSpeak®", narrEnglish: "Engels", narrFormula: "Formule",
      narrRulespeakHint: "De declaratieve bedrijfsregel (alleen als / moet / prioriteit)",
      narrEnglishHint: "De formule gelezen als een eenvoudige Engelse zin",
      narrFormulaHint: "De ruwe spreadsheetformule, met aanklikbare velden",
      narrAriaLabel: "Hoe deze regel uit te leggen",
      gearTitle: "Instellingen — kies wat er in de hoverkaart en op de veldpagina verschijnt",
      gearAriaLabel: "Instellingen",
      gearPopTitle: "Tonen in popup en op pagina",
      gearReset: "Alles weer aanzetten",
      elemDesc: "Beschrijving", elemDescHint: "De beschrijving van het veld in gewone taal.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "De declaratieve bedrijfsregel.",
      elemEnglish: "Engels", elemEnglishHint: "De formule gelezen als een eenvoudige zin.",
      elemFormula: "Formule", elemFormulaHint: "De ruwe spreadsheetformule.",
      elemInputs: "Invoer", elemInputsHint: "De velden die deze eenregelige functie aanroept.",
      elemConsumers: "Afnemers", elemConsumersHint: "Velden waarvan de functie deze aanroept.",
      provOn: "Herkomst · AAN", provOff: "Herkomst · uit",
      provOnTitle: "ƒ-herkomstsymbolen verbergen. Dubbelklikken op cellen opent de DAG nog steeds.",
      provOffTitle: "ƒ-herkomstsymbolen tonen op cellen met verkenbare herkomst.",
      cellHintOn: "Beweeg over het symbool voor een voorbeeld; dubbelklik om de volledige DAG-pagina te openen",
      cellHintOff: "Dubbelklik om de herkomst te zien (ƒ-symbolen aan/uit in de kopbalk)",
      ontologyTitle: "De ontologie",
      ontologyLead: "Elke tabel in het regelboek. Klik op een tabel om de kolommen te zien.",
      fieldsCount: (n) => `${n} velden`, derivedCount: (n) => `${n} afgeleid`, relCount: (n) => `${n} rel.`,
      tableNotFound: "Tabel niet gevonden.", fieldNotFound: "Veld niet gevonden in het regelboek.",
      nullable: "NULL toegestaan",
      hopsFromGround: (n) => (n === 1 ? "1 stap van de basisgegevens" : `${n} stappen van de basisgegevens`),
      relationshipPointer: "Relatieverwijzing", groundTruth: "Basisgegevens",
      relPointerBody: (link) => `Dit veld is een verwijzing naar ${link}. Het is nergens anders van afgeleid — het is de koppeling waaraan de rest van de DAG hangt.`,
      relPointerBodyNoLink: "Dit veld is een verwijzing naar een andere tabel. Het is nergens anders van afgeleid — het is de koppeling waaraan de rest van de DAG hangt.",
      groundTruthBody: (dt) => `Deze cel is een blad. Ze wordt rechtstreeks naar de database <em>geschreven</em> (gegevenstype <code>${dt}</code>) en wordt nergens anders uit berekend. Al het andere stroomopwaarts gaat uiteindelijk terug op waarden zoals deze.`,
      openTable: (t) => `${t} openen →`,
      ruleCardTitle: "Deze cel is de waarde van één declaratieve regel",
      oneLineFnCardTitle: "Deze cel is de waarde van één eenregelige functie",
      inRuleSpeak: "In RuleSpeak®", inEnglish: "In het Engels", asFormula: "Als formule",
      mechanicalFlag: "⚠︎ mechanisch", mechanicalTitle: "Correct maar stroef geformuleerd — een signaal voor een optionele herformulering",
      noRuleRendered: (t) => `Voor dit ${t}-veld is geen declaratieve regel gegenereerd.`,
      obligations: "Verplichtingen",
      ruleSpeakHintFormula: "Dit is dezelfde logica als in de formule, geschreven als bedrijfsregel — door de gedeelde RuleSpeak®-engine uit het regelboek gegenereerd.",
      ruleSpeakHintNoFormula: "Door de gedeelde RuleSpeak®-engine uit het regelboek gegenereerd.",
      englishHint: "Elk onderstreept veld is zelf een eenregelige functie. Klik erop om verder in te zoomen.",
      noFormulaSentence: (t) => `Deze ${t} heeft geen spreadsheetformule om als zin te lezen — het is een aggregatie die structureel over een relatie is gedefinieerd. Schakel over naar <strong>RuleSpeak®</strong> om te zien hoe die is gedefinieerd.`,
      formulaHint: "Elke chip is zelf een eenregelige functie. Klik op een chip om verder in te zoomen.",
      noFormulaAtAll: (t) => `Deze ${t} heeft geen spreadsheetformule — het is een aggregatie die structureel over een relatie is gedefinieerd. Schakel over naar <strong>RuleSpeak®</strong> om te zien hoe die is gedefinieerd.`,
      inputsTitle: "Invoer", inputsLead: "Velden die deze eenregelige functie aanroept.",
      groundTruthInline: (dt) => `Basisgegevens · gegevenstype ${dt}`,
      consumersTitle: "Afnemers",
      consumersDirect: "direct", consumersTransitive: "transitief",
      consumersEmpty: "Nog niets anders in het regelboek verwijst naar deze cel.",
      consumersLead: "Velden waarvan de eenregelige functie deze aanroept.",
      showTransitive: (n) => `${n} transitieve afnemers tonen (verder stroomafwaarts)`,
      leavesTitle: "Basisgegevens aan de bladeren",
      leavesLead: "Uiteindelijk hangt de waarde van deze cel af van deze ruwe waarden. Een ervan bewerken en opnieuw bouwen werkt hier automatisch door.",
      hoverGroundTruth: (dt) => `Basisgegevens — rechtstreeks naar de database geschreven${dt ? ` (gegevenstype <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Relatieverwijzing — de koppeling waaraan de rest van de DAG hangt.",
      hoverNoRule: "Geen declaratieve regel gegenereerd.",
      hoverNoFormula: "Geen formule — een structurele aggregatie. Zie RuleSpeak®.",
      hoverInputs: "Invoer",
      hoverHint: "Dubbelklik op de cel om de volledige DAG-pagina te openen.",
      type_raw: "Basisgegevens", type_calculated: "Berekend", type_aggregation: "Aggregatie", type_relationship: "Relatie", type_lookup: "Opzoeking",
    },
    ru: {
      back: "← назад", backTitle: "Вернуться на шаг назад",
      home: "🏠 Главная", homeTitle: "Выйти из обозревателя — вернуться в приложение",
      tablesCrumb: "Таблицы",
      narrRulespeak: "RuleSpeak®", narrEnglish: "Английский", narrFormula: "Формула",
      narrRulespeakHint: "Декларативное бизнес-правило (только если / должен / приоритет)",
      narrEnglishHint: "Формула, прочитанная как простое предложение на английском",
      narrFormulaHint: "Исходная формула в стиле электронной таблицы, с кликабельными полями",
      narrAriaLabel: "Как объяснить это правило",
      gearTitle: "Настройки — выберите, что показывать во всплывающей карточке и на странице поля",
      gearAriaLabel: "Настройки",
      gearPopTitle: "Показывать во всплывающем окне и на странице",
      gearReset: "Снова включить всё",
      elemDesc: "Описание", elemDescHint: "Описание поля простым языком.",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "Декларативное бизнес-правило.",
      elemEnglish: "Английский", elemEnglishHint: "Формула, прочитанная как простое предложение.",
      elemFormula: "Формула", elemFormulaHint: "Исходная формула в стиле электронной таблицы.",
      elemInputs: "Входы", elemInputsHint: "Поля, которые вызывает эта однострочная функция.",
      elemConsumers: "Потребители", elemConsumersHint: "Поля, функция которых вызывает эту.",
      provOn: "Происхождение · ВКЛ", provOff: "Происхождение · выкл",
      provOnTitle: "Скрыть значки происхождения ƒ. Двойной щелчок по ячейкам по-прежнему открывает DAG.",
      provOffTitle: "Показывать значки происхождения ƒ на ячейках, происхождение которых можно изучить.",
      cellHintOn: "Наведите на значок для предпросмотра; двойной щелчок открывает полную страницу DAG",
      cellHintOff: "Двойной щелчок — посмотреть происхождение (значки ƒ включаются в заголовке)",
      ontologyTitle: "Онтология",
      ontologyLead: "Все таблицы свода правил. Щёлкните таблицу, чтобы увидеть её столбцы.",
      fieldsCount: (n) => `полей: ${n}`, derivedCount: (n) => `производных: ${n}`, relCount: (n) => `связей: ${n}`,
      tableNotFound: "Таблица не найдена.", fieldNotFound: "Поле не найдено в своде правил.",
      nullable: "допускает NULL",
      hopsFromGround: (n) => `шагов от исходных данных: ${n}`,
      relationshipPointer: "Указатель связи", groundTruth: "Исходные данные",
      relPointerBody: (link) => `Это поле — указатель на ${link}. Оно ни из чего не выводится — это связь, на которой держится остальной DAG.`,
      relPointerBodyNoLink: "Это поле — указатель на другую таблицу. Оно ни из чего не выводится — это связь, на которой держится остальной DAG.",
      groundTruthBody: (dt) => `Эта ячейка — лист. Она <em>записывается</em> прямо в базу данных (тип данных <code>${dt}</code>) и ни из чего не вычисляется. Всё остальное выше по цепочке в итоге сводится к таким значениям.`,
      openTable: (t) => `Открыть ${t} →`,
      ruleCardTitle: "Эта ячейка — значение одного декларативного правила",
      oneLineFnCardTitle: "Эта ячейка — значение одной однострочной функции",
      inRuleSpeak: "В RuleSpeak®", inEnglish: "На английском", asFormula: "В виде формулы",
      mechanicalFlag: "⚠︎ механически", mechanicalTitle: "Точно, но неуклюже сформулировано — отметка для необязательной правки",
      noRuleRendered: (t) => `Для этого поля типа ${t} декларативное правило не создано.`,
      obligations: "Обязательства",
      ruleSpeakHintFormula: "Это та же логика, что заложена в формуле, записанная как бизнес-правило — создано из свода правил общим движком RuleSpeak®.",
      ruleSpeakHintNoFormula: "Создано из свода правил общим движком RuleSpeak®.",
      englishHint: "Каждое подчёркнутое поле само является однострочной функцией. Щёлкните любое, чтобы перейти к нему.",
      noFormulaSentence: (t) => `У этого поля типа ${t} нет формулы, которую можно прочитать как предложение, — это свёртка, определённая структурно через связь. Переключитесь на <strong>RuleSpeak®</strong>, чтобы увидеть её определение.`,
      formulaHint: "Каждый чип сам является однострочной функцией. Щёлкните любой чип, чтобы перейти к нему.",
      noFormulaAtAll: (t) => `У этого поля типа ${t} нет формулы — это свёртка, определённая структурно через связь. Переключитесь на <strong>RuleSpeak®</strong>, чтобы увидеть её определение.`,
      inputsTitle: "Входы", inputsLead: "Поля, которые вызывает эта однострочная функция.",
      groundTruthInline: (dt) => `Исходные данные · тип данных ${dt}`,
      consumersTitle: "Потребители",
      consumersDirect: "прямых", consumersTransitive: "транзитивных",
      consumersEmpty: "Пока ничто в своде правил не ссылается на эту ячейку.",
      consumersLead: "Поля, однострочная функция которых вызывает эту.",
      showTransitive: (n) => `Показать транзитивных потребителей: ${n} (ниже по цепочке)`,
      leavesTitle: "Исходные данные в листьях",
      leavesLead: "В конечном счёте значение этой ячейки зависит от этих исходных значений. Если изменить любое из них и пересобрать, изменение автоматически дойдёт сюда.",
      hoverGroundTruth: (dt) => `Исходные данные — записываются прямо в базу данных${dt ? ` (тип данных <code>${dt}</code>)` : ""}.`,
      hoverRelPointer: "Указатель связи — связь, на которой держится остальной DAG.",
      hoverNoRule: "Декларативное правило не создано.",
      hoverNoFormula: "Нет формулы — структурная свёртка. См. RuleSpeak®.",
      hoverInputs: "Входы",
      hoverHint: "Дважды щёлкните ячейку, чтобы открыть полную страницу DAG.",
      type_raw: "Исходные данные", type_calculated: "Вычисляемое", type_aggregation: "Агрегат", type_relationship: "Связь", type_lookup: "Подстановка",
    },
    zh: {
      back: "← 返回", backTitle: "后退一步",
      home: "🏠 首页", homeTitle: "离开解释器 — 返回应用",
      tablesCrumb: "表",
      narrRulespeak: "RuleSpeak®", narrEnglish: "英语", narrFormula: "公式",
      narrRulespeakHint: "声明式业务规则（仅当 / 必须 / 优先级）",
      narrEnglishHint: "将公式读作一句简单的英文",
      narrFormulaHint: "原始的电子表格式公式，字段可点击",
      narrAriaLabel: "如何解释此规则",
      gearTitle: "设置 — 选择悬停卡片和字段页面中显示的内容",
      gearAriaLabel: "设置",
      gearPopTitle: "在弹窗和页面中显示",
      gearReset: "全部重新开启",
      elemDesc: "描述", elemDescHint: "字段的通俗描述。",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "声明式业务规则。",
      elemEnglish: "英语", elemEnglishHint: "将公式读作一句简单的句子。",
      elemFormula: "公式", elemFormulaHint: "原始的电子表格式公式。",
      elemInputs: "输入", elemInputsHint: "此单行函数调用的字段。",
      elemConsumers: "使用方", elemConsumersHint: "其函数调用此函数的字段。",
      provOn: "溯源 · 开", provOff: "溯源 · 关",
      provOnTitle: "隐藏 ƒ 溯源标记。双击单元格仍会打开 DAG。",
      provOffTitle: "在可追溯来源的单元格上显示 ƒ 溯源标记。",
      cellHintOn: "悬停标记可预览；双击打开完整的 DAG 页面",
      cellHintOff: "双击查看溯源（在页头切换 ƒ 标记）",
      ontologyTitle: "本体",
      ontologyLead: "规则手册中的所有表。点击某个表查看其列。",
      fieldsCount: (n) => `${n} 个字段`, derivedCount: (n) => `${n} 个派生`, relCount: (n) => `${n} 个关系`,
      tableNotFound: "未找到该表。", fieldNotFound: "规则手册中未找到该字段。",
      nullable: "可为空",
      hopsFromGround: (n) => `距基础数据 ${n} 跳`,
      relationshipPointer: "关系指针", groundTruth: "基础数据",
      relPointerBody: (link) => `此字段是指向 ${link} 的指针。它不由其他任何内容派生——它是 DAG 其余部分所依附的链接。`,
      relPointerBodyNoLink: "此字段是指向另一个表的指针。它不由其他任何内容派生——它是 DAG 其余部分所依附的链接。",
      groundTruthBody: (dt) => `此单元格是叶节点。它直接<em>写入</em>数据库（数据类型 <code>${dt}</code>），不由其他任何内容计算得出。上游的一切最终都可追溯到这样的值。`,
      openTable: (t) => `打开 ${t} →`,
      ruleCardTitle: "此单元格是一条声明式规则的值",
      oneLineFnCardTitle: "此单元格是一个单行函数的值",
      inRuleSpeak: "RuleSpeak® 表述", inEnglish: "英语表述", asFormula: "公式表述",
      mechanicalFlag: "⚠︎ 机械化", mechanicalTitle: "含义准确但措辞生硬 — 可选择性改写的标记",
      noRuleRendered: (t) => `未为此 ${t} 字段生成声明式规则。`,
      obligations: "义务",
      ruleSpeakHintFormula: "这是公式所表达的同一逻辑，以业务规则的形式写出 — 由共享的 RuleSpeak® 引擎根据规则手册生成。",
      ruleSpeakHintNoFormula: "由共享的 RuleSpeak® 引擎根据规则手册生成。",
      englishHint: "每个带下划线的字段本身都是一个单行函数。点击任意字段可深入查看。",
      noFormulaSentence: (t) => `此 ${t} 没有可读作句子的电子表格公式 — 它是通过关系结构化定义的汇总。切换到 <strong>RuleSpeak®</strong> 查看其定义。`,
      formulaHint: "每个标签本身都是一个单行函数。点击任意标签可深入查看。",
      noFormulaAtAll: (t) => `此 ${t} 没有电子表格公式 — 它是通过关系结构化定义的汇总。切换到 <strong>RuleSpeak®</strong> 查看其定义。`,
      inputsTitle: "输入", inputsLead: "此单行函数调用的字段。",
      groundTruthInline: (dt) => `基础数据 · 数据类型 ${dt}`,
      consumersTitle: "使用方",
      consumersDirect: "直接", consumersTransitive: "间接",
      consumersEmpty: "规则手册中目前没有其他内容引用此单元格。",
      consumersLead: "其单行函数调用此函数的字段。",
      showTransitive: (n) => `显示 ${n} 个间接使用方（下游的下游）`,
      leavesTitle: "叶节点处的基础数据",
      leavesLead: "归根结底，此单元格的值取决于这些原始值。编辑其中任何一个并重新构建，变化都会自动传播到这里。",
      hoverGroundTruth: (dt) => `基础数据 — 直接写入数据库${dt ? `（数据类型 <code>${dt}</code>）` : ""}。`,
      hoverRelPointer: "关系指针 — DAG 其余部分所依附的链接。",
      hoverNoRule: "未生成声明式规则。",
      hoverNoFormula: "无公式 — 结构化汇总。请参阅 RuleSpeak®。",
      hoverInputs: "输入",
      hoverHint: "双击单元格打开完整的 DAG 页面。",
      type_raw: "基础数据", type_calculated: "计算", type_aggregation: "聚合", type_relationship: "关系", type_lookup: "查找",
    },
    hi: {
      back: "← वापस", backTitle: "एक कदम पीछे जाएँ",
      home: "🏠 होम", homeTitle: "एक्सप्लेनर छोड़ें — ऐप पर वापस जाएँ",
      tablesCrumb: "तालिकाएँ",
      narrRulespeak: "RuleSpeak®", narrEnglish: "अंग्रेज़ी", narrFormula: "सूत्र",
      narrRulespeakHint: "घोषणात्मक व्यावसायिक नियम (केवल यदि / अनिवार्य / प्राथमिकता)",
      narrEnglishHint: "सूत्र को एक सरल अंग्रेज़ी वाक्य के रूप में पढ़ा गया",
      narrFormulaHint: "स्प्रेडशीट-शैली का मूल सूत्र, क्लिक करने योग्य फ़ील्ड के साथ",
      narrAriaLabel: "इस नियम को कैसे समझाएँ",
      gearTitle: "सेटिंग्स — चुनें कि होवर कार्ड और फ़ील्ड पेज पर क्या दिखे",
      gearAriaLabel: "सेटिंग्स",
      gearPopTitle: "पॉपअप और पेज पर दिखाएँ",
      gearReset: "सब फिर से चालू करें",
      elemDesc: "विवरण", elemDescHint: "फ़ील्ड का सरल भाषा में विवरण।",
      elemRulespeak: "RuleSpeak®", elemRulespeakHint: "घोषणात्मक व्यावसायिक नियम।",
      elemEnglish: "अंग्रेज़ी", elemEnglishHint: "सूत्र को एक सरल वाक्य के रूप में पढ़ा गया।",
      elemFormula: "सूत्र", elemFormulaHint: "स्प्रेडशीट-शैली का मूल सूत्र।",
      elemInputs: "इनपुट", elemInputsHint: "वे फ़ील्ड जिन्हें यह एक-पंक्ति फ़ंक्शन कॉल करता है।",
      elemConsumers: "उपभोक्ता", elemConsumersHint: "वे फ़ील्ड जिनका फ़ंक्शन इसे कॉल करता है।",
      provOn: "उत्पत्ति · चालू", provOff: "उत्पत्ति · बंद",
      provOnTitle: "ƒ उत्पत्ति चिह्न छिपाएँ। सेल पर डबल-क्लिक करने से DAG फिर भी खुलता है।",
      provOffTitle: "जिन सेल की उत्पत्ति देखी जा सकती है, उन पर ƒ उत्पत्ति चिह्न दिखाएँ।",
      cellHintOn: "झलक के लिए बैज पर होवर करें; पूरा DAG पेज खोलने के लिए डबल-क्लिक करें",
      cellHintOff: "उत्पत्ति देखने के लिए डबल-क्लिक करें (हेडर में ƒ चिह्न चालू/बंद करें)",
      ontologyTitle: "ऑन्टोलॉजी",
      ontologyLead: "नियम-पुस्तिका की हर तालिका। किसी तालिका के कॉलम देखने के लिए उस पर क्लिक करें।",
      fieldsCount: (n) => `${n} फ़ील्ड`, derivedCount: (n) => `${n} व्युत्पन्न`, relCount: (n) => `${n} संबंध`,
      tableNotFound: "तालिका नहीं मिली।", fieldNotFound: "नियम-पुस्तिका में फ़ील्ड नहीं मिला।",
      nullable: "NULL स्वीकार्य",
      hopsFromGround: (n) => `मूल डेटा से ${n} चरण दूर`,
      relationshipPointer: "संबंध सूचक", groundTruth: "मूल डेटा",
      relPointerBody: (link) => `यह फ़ील्ड ${link} की ओर एक सूचक है। यह किसी और चीज़ से व्युत्पन्न नहीं है — यही वह कड़ी है जिस पर शेष DAG टिका है।`,
      relPointerBodyNoLink: "यह फ़ील्ड किसी अन्य तालिका की ओर एक सूचक है। यह किसी और चीज़ से व्युत्पन्न नहीं है — यही वह कड़ी है जिस पर शेष DAG टिका है।",
      groundTruthBody: (dt) => `यह सेल एक पत्ती है। इसे सीधे डेटाबेस में <em>लिखा</em> जाता है (डेटा प्रकार <code>${dt}</code>) और यह किसी और चीज़ से गणना नहीं किया जाता। ऊपर की हर चीज़ अंततः ऐसे ही मानों तक पहुँचती है।`,
      openTable: (t) => `${t} खोलें →`,
      ruleCardTitle: "यह सेल एक घोषणात्मक नियम का मान है",
      oneLineFnCardTitle: "यह सेल एक एक-पंक्ति फ़ंक्शन का मान है",
      inRuleSpeak: "RuleSpeak® में", inEnglish: "अंग्रेज़ी में", asFormula: "सूत्र के रूप में",
      mechanicalFlag: "⚠︎ यांत्रिक", mechanicalTitle: "अर्थ सही है पर शब्द-रचना अटपटी है — वैकल्पिक पुनर्लेखन के लिए संकेत",
      noRuleRendered: (t) => `इस ${t} फ़ील्ड के लिए कोई घोषणात्मक नियम नहीं बनाया गया।`,
      obligations: "दायित्व",
      ruleSpeakHintFormula: "यह वही तर्क है जो सूत्र में है, व्यावसायिक नियम के रूप में लिखा गया — साझा RuleSpeak® इंजन द्वारा नियम-पुस्तिका से बनाया गया।",
      ruleSpeakHintNoFormula: "साझा RuleSpeak® इंजन द्वारा नियम-पुस्तिका से बनाया गया।",
      englishHint: "रेखांकित हर फ़ील्ड स्वयं एक एक-पंक्ति फ़ंक्शन है। विस्तार से देखने के लिए किसी पर भी क्लिक करें।",
      noFormulaSentence: (t) => `इस ${t} का कोई स्प्रेडशीट सूत्र नहीं है जिसे वाक्य की तरह पढ़ा जा सके — यह किसी संबंध पर संरचनात्मक रूप से परिभाषित एक समेकन है। इसकी परिभाषा देखने के लिए <strong>RuleSpeak®</strong> पर जाएँ।`,
      formulaHint: "हर चिप स्वयं एक एक-पंक्ति फ़ंक्शन है। विस्तार से देखने के लिए किसी भी चिप पर क्लिक करें।",
      noFormulaAtAll: (t) => `इस ${t} का कोई स्प्रेडशीट सूत्र नहीं है — यह किसी संबंध पर संरचनात्मक रूप से परिभाषित एक समेकन है। इसकी परिभाषा देखने के लिए <strong>RuleSpeak®</strong> पर जाएँ।`,
      inputsTitle: "इनपुट", inputsLead: "वे फ़ील्ड जिन्हें यह एक-पंक्ति फ़ंक्शन कॉल करता है।",
      groundTruthInline: (dt) => `मूल डेटा · डेटा प्रकार ${dt}`,
      consumersTitle: "उपभोक्ता",
      consumersDirect: "प्रत्यक्ष", consumersTransitive: "अप्रत्यक्ष",
      consumersEmpty: "नियम-पुस्तिका में अभी कोई और चीज़ इस सेल का संदर्भ नहीं देती।",
      consumersLead: "वे फ़ील्ड जिनका एक-पंक्ति फ़ंक्शन इसे कॉल करता है।",
      showTransitive: (n) => `${n} अप्रत्यक्ष उपभोक्ता दिखाएँ (आगे की शृंखला में)`,
      leavesTitle: "पत्तियों पर मूल डेटा",
      leavesLead: "अंततः इस सेल का मान इन मूल मानों पर निर्भर करता है। इनमें से किसी को बदलकर फिर से बिल्ड करने पर बदलाव अपने-आप यहाँ तक पहुँचता है।",
      hoverGroundTruth: (dt) => `मूल डेटा — सीधे डेटाबेस में लिखा गया${dt ? ` (डेटा प्रकार <code>${dt}</code>)` : ""}।`,
      hoverRelPointer: "संबंध सूचक — वह कड़ी जिस पर शेष DAG टिका है।",
      hoverNoRule: "कोई घोषणात्मक नियम नहीं बनाया गया।",
      hoverNoFormula: "कोई सूत्र नहीं — एक संरचनात्मक समेकन। RuleSpeak® देखें।",
      hoverInputs: "इनपुट",
      hoverHint: "पूरा DAG पेज खोलने के लिए सेल पर डबल-क्लिक करें।",
      type_raw: "मूल डेटा", type_calculated: "गणना किया गया", type_aggregation: "समेकन", type_relationship: "संबंध", type_lookup: "लुकअप",
    },
  };
  function tt(key, ...args) {
    const dict = CHROME[lang] || CHROME.en;
    const entry = key in dict ? dict[key] : CHROME.en[key];
    return typeof entry === "function" ? entry(...args) : entry;
  }

  let config = { mode: "hash", basePath: "/rulebook-explainer-dag" };
  let routing = null;
  const CLOSE_DELAY_MS = 220;
  const CARD_W = 360;
  const SAFETY = 15;
  const GAP = 8;
  const MARGIN = 12;
  const EST_CARD_H = 300;
  let hoverCloseTimer = null;
  let activeHoverCard = null;

  // The page currently on screen, so a prefs change (narration / gear / glyphs)
  // can re-render IT — host-agnostic. Outlet/hash hosts and framework hosts that
  // render into their own container (e.g. the Angular DagFieldComponent's <div>)
  // both work, because we replay the exact last render call rather than relying
  // on a global outlet or the URL hash.
  let lastRender = null; // { kind: "index"|"table"|"field", container, table, field }
  function rerenderCurrent() {
    if (!lastRender || !lastRender.container || !lastRender.container.isConnected) return false;
    const { kind, container, table, field } = lastRender;
    if (kind === "field") renderFieldPage(container, table, field);
    else if (kind === "table") renderTablePage(container, table);
    else renderTablesIndex(container);
    return true;
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }
  function humanizeField(name) { return R().humanizeField(name); }

  // Guarantee `routing` exists before any renderer runs. A host that calls a
  // render method (e.g. renderFieldPage) BEFORE init() — common with framework
  // routers that mount a component on hard-load before the explainer's own
  // init has run — would otherwise hit a null `routing` and render nothing (the
  // "works only after navigating away and back" bug). We lazily build a default
  // hash-routing so the first paint always works; a later init() with custom
  // routing replaces it.
  function ensureRouting() {
    if (routing) return routing;
    routing = global.EffortlessExplainerRouting.createRouting({
      mode: (config && config.mode) || "hash",
      hashPrefix: config && config.hashPrefix,
      fieldPath: config && config.fieldPath,
      tablePath: config && config.tablePath,
      indexPath: config && config.indexPath,
      homePath: config && config.homePath,
      htmxFieldUrl: config && config.htmxFieldUrl,
      routing: config && config.routing,
    });
    return routing;
  }

  // ════════════════════════════════════════════════════════════════════════
  //  PREFS — single source of truth (localStorage + a custom event), read
  //  synchronously so the first paint is already correct. Mirrors React
  //  lib/dagPrefs.ts plus the doc-element gating the gear controls.
  // ════════════════════════════════════════════════════════════════════════
  const PREFS_EVENT = "dag-prefs-changed";
  // Kept as the original key so existing hosts (e.g. the demo) stay compatible.
  const GLYPHS_KEY = "effortless-explainer-glyphs-on";
  const MODE_KEY = "dag.narrationMode";
  const ELEM_KEY = "dag.docElements";

  const NARRATION_MODES = ["rulespeak", "english", "formula"];
  const DEFAULT_MODE = "rulespeak";

  // The independent doc-element toggles the gear exposes. `key` drives the
  // page container class (show-<key>) and the hover-card section visibility.
  const DOC_ELEMENTS = [
    { key: "desc",      labelKey: "elemDesc",      hintKey: "elemDescHint" },
    { key: "rulespeak", labelKey: "elemRulespeak", hintKey: "elemRulespeakHint" },
    { key: "english",   labelKey: "elemEnglish",   hintKey: "elemEnglishHint" },
    { key: "formula",   labelKey: "elemFormula",   hintKey: "elemFormulaHint" },
    { key: "inputs",    labelKey: "elemInputs",    hintKey: "elemInputsHint" },
    { key: "consumers", labelKey: "elemConsumers", hintKey: "elemConsumersHint" },
  ];
  // Inputs defaults OFF: the RuleSpeak®/English/Formula card right above the
  // field page's Inputs section already names and links every one of those
  // same fields, so showing them again by default is pure repetition. The
  // gear still offers it for whoever wants the grid view.
  const DEFAULT_ELEMS = { desc: true, rulespeak: true, english: true, formula: true, inputs: false, consumers: true };

  const prefs = (function () {
    function glyphsOn() {
      return localStorage.getItem(GLYPHS_KEY) !== "false"; // default ON (host-friendly)
    }
    function setGlyphs(on) {
      localStorage.setItem(GLYPHS_KEY, on ? "true" : "false");
      fire();
    }
    function narrationMode() {
      const v = localStorage.getItem(MODE_KEY);
      return v && NARRATION_MODES.includes(v) ? v : DEFAULT_MODE;
    }
    function setNarrationMode(mode) {
      if (!NARRATION_MODES.includes(mode)) return;
      localStorage.setItem(MODE_KEY, mode);
      fire();
    }
    function docElements() {
      try {
        const raw = JSON.parse(localStorage.getItem(ELEM_KEY) || "null");
        if (raw && typeof raw === "object") return Object.assign({}, DEFAULT_ELEMS, raw);
      } catch { /* fall through */ }
      return Object.assign({}, DEFAULT_ELEMS);
    }
    function setDocElement(key, on) {
      const next = docElements();
      next[key] = !!on;
      localStorage.setItem(ELEM_KEY, JSON.stringify(next));
      fire();
    }
    function resetDocElements() {
      localStorage.removeItem(ELEM_KEY);
      fire();
    }
    // The space-separated `show-<key>` classes for the page container, computed
    // synchronously so the field page paints with the right sections up front.
    function docElementClasses() {
      const e = docElements();
      return DOC_ELEMENTS.filter((d) => e[d.key]).map((d) => `show-${d.key}`).join(" ");
    }
    function fire() { window.dispatchEvent(new Event(PREFS_EVENT)); }
    function subscribe(cb) {
      window.addEventListener(PREFS_EVENT, cb);
      window.addEventListener("storage", cb);
      return () => {
        window.removeEventListener(PREFS_EVENT, cb);
        window.removeEventListener("storage", cb);
      };
    }
    return {
      glyphsOn, setGlyphs, narrationMode, setNarrationMode,
      docElements, setDocElement, resetDocElements, docElementClasses, subscribe,
    };
  })();

  // ════════════════════════════════════════════════════════════════════════
  //  SHARED RENDER HELPERS
  // ════════════════════════════════════════════════════════════════════════

  function ruleSpeakFor(table, field) { return R().ruleSpeakForField(table, field, lang); }

  function renderFieldLink(table, field, label, className) {
    const a = document.createElement("a");
    a.href = routing.fieldHref(table, field);
    a.className = className || "dag-link";
    a.textContent = label;
    a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      routing.navigate(table, field);
    });
    return a;
  }
  function renderTableLink(table, label, className) {
    const a = document.createElement("a");
    a.href = routing.tableHref(table);
    a.className = className || "dag-link";
    a.textContent = label;
    a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      routing.navigateTable(table);
    });
    return a;
  }

  // ── Markdown emphasis (**kw**, *em*) → HTML, with field-ref linkification.
  // Mirrors React lib/rulespeak.ts (renderRuleMarkdown / linkifyText / renderRuleRich).
  function indexOfWord(hay, needle) {
    const lc = hay.toLowerCase(), target = needle.toLowerCase();
    let from = 0;
    while (from <= lc.length - target.length) {
      const idx = lc.indexOf(target, from);
      if (idx < 0) return -1;
      const before = idx === 0 ? "" : lc[idx - 1];
      const after = idx + target.length >= lc.length ? "" : lc[idx + target.length];
      if ((!before || !/[a-z0-9]/i.test(before)) && (!after || !/[a-z0-9]/i.test(after))) return idx;
      from = idx + 1;
    }
    return -1;
  }
  // Returns HTML string. refs become clickable fc-inline spans.
  function linkifyHtml(text, refs) {
    if (!text) return "";
    const sorted = (refs || []).filter((r) => r.label).slice().sort((a, b) => b.label.length - a.label.length);
    if (!sorted.length) return esc(text);
    let out = "", rest = text;
    while (true) {
      let bestIdx = -1, bestRef = null;
      for (const r of sorted) {
        const idx = indexOfWord(rest, r.label);
        if (idx >= 0 && (bestIdx === -1 || idx < bestIdx)) { bestIdx = idx; bestRef = r; if (idx === 0) break; }
      }
      if (bestIdx === -1 || !bestRef) { out += esc(rest); break; }
      if (bestIdx > 0) out += esc(rest.slice(0, bestIdx));
      const matched = rest.slice(bestIdx, bestIdx + bestRef.label.length);
      const tone = bestRef.tone || "calc";
      out += `<a class="fc-inline fc-inline-${tone}" href="${esc(refHref(bestRef.table, bestRef.field))}" data-ref-table="${esc(bestRef.table)}" data-ref-field="${esc(bestRef.field)}">${esc(matched)}</a>`;
      rest = rest.slice(bestIdx + bestRef.label.length);
    }
    return out;
  }
  // Bold/italic markdown + ref linkification inside the plain segments.
  function renderRuleRichHtml(md, refs) {
    if (!md) return "";
    const re = /\*\*([^*]+)\*\*|\*([^*]+)\*/g;
    let out = "", last = 0, m;
    while ((m = re.exec(md)) !== null) {
      if (m.index > last) out += linkifyHtml(md.slice(last, m.index), refs);
      if (m[1] !== undefined) out += `<strong class="dag-rs-kw">${esc(m[1])}</strong>`;
      else if (m[2] !== undefined) out += `<em>${esc(m[2])}</em>`;
      last = re.lastIndex;
    }
    if (last < md.length) out += linkifyHtml(md.slice(last), refs);
    return out;
  }
  // Tag each rulespeak ref with the referenced field's tone so links are color-coded.
  function tonedRefs(rs) {
    if (!rs || !rs.refs) return [];
    return rs.refs.map((r) => {
      const f = R().fieldOf(R().rulebook(), r.table, r.field);
      return Object.assign({}, r, { tone: R().typeTone((f && f.type) || "raw") });
    });
  }

  // ── Formula AST → HTML (clickable chips). Mirrors lib/renderJsx.tsx. ─────────
  const BINOP_LABEL = { "+": "+", "-": "−", "*": "×", "/": "÷", "&": "&", "=": "=", "<>": "≠", "<": "<", ">": ">", "<=": "≤", ">=": "≥" };
  function fmtNum(n) {
    if (Number.isInteger(n) && Math.abs(n) >= 1000) return n.toLocaleString("en-US");
    return String(n);
  }
  // Real href for a ref link (so chips/pills/inline refs behave like links —
  // cursor, focus, cmd/middle-click open-in-new-tab — and don't go dead if a JS
  // handler ever fails to bind). The click handler still intercepts for SPA nav.
  function refHref(table, field) {
    try { return (routing && routing.fieldHref) ? routing.fieldHref(table, field) : `#/dag/${encodeURIComponent(table)}/${encodeURIComponent(field)}`; }
    catch { return `#/dag/${encodeURIComponent(table)}/${encodeURIComponent(field)}`; }
  }
  function tableHrefSafe(table) {
    try { return (routing && routing.tableHref) ? routing.tableHref(table) : `#/dag/${encodeURIComponent(table)}`; }
    catch { return `#/dag/${encodeURIComponent(table)}`; }
  }
  function chipHtml(table, field, pageTable) {
    const node = R().fieldOf(R().rulebook(), table, field);
    const type = (node && node.type) || "raw";
    const tone = R().typeTone(type);
    const glyph = R().typeGlyph(type);
    const showTable = table && table !== pageTable;
    return `<a class="fc fc-${tone} fc-chip" href="${esc(refHref(table, field))}" data-ref-table="${esc(table)}" data-ref-field="${esc(field)}">` +
      `<span class="fc-glyph">${esc(glyph)}</span>` +
      (showTable ? `<span class="fc-table">${esc(table)}.</span>` : "") +
      `<span class="fc-name">${esc(humanizeField(field))}</span></a>`;
  }
  function formulaNodeHtml(node, pageTable, top) {
    switch (node.kind) {
      case "ref": return chipHtml(node.table || pageTable, node.field, pageTable);
      case "num": return `<span class="fx-num">${esc(fmtNum(node.value))}</span>`;
      case "str": return `<span class="fx-str">“${esc(node.value)}”</span>`;
      case "bool": return `<span class="fx-bool">${node.value ? "TRUE" : "FALSE"}</span>`;
      case "unary": return `−${formulaNodeHtml(node.arg, pageTable, false)}`;
      case "binop": {
        const inner = `${formulaNodeHtml(node.left, pageTable, false)} <span class="fx-op">${esc(BINOP_LABEL[node.op] || node.op)}</span> ${formulaNodeHtml(node.right, pageTable, false)}`;
        return top ? inner : `(${inner})`;
      }
      case "call": {
        const args = node.args.map((a, i) =>
          (i > 0 ? `<span class="fx-comma">,&nbsp;</span>` : "") + formulaNodeHtml(a, pageTable, false)).join("");
        return `<span class="fx-fn">${esc(node.fn.toLowerCase())}</span><span class="fx-paren">(</span>${args}<span class="fx-paren">)</span>`;
      }
    }
    return "";
  }
  function formulaHtml(formula, pageTable) {
    const ast = R().tryParseFormula(formula);
    if (!ast) return `<code class="fx-raw">${esc(formula)}</code>`;
    return `<span class="fx"><span class="fx-eq">= </span>${formulaNodeHtml(ast, pageTable, true)}</span>`;
  }

  // ── RuleTree (priority ladders / AND-OR) → HTML. Mirrors components/RuleTree.tsx.
  function ruleTreeHtml(node, refs) {
    // Connector words come from the language pack (baked per language into
    // embedded-graph.js) — the same words the RuleSpeak® document uses.
    const cx = R().ruleSpeakConnectors(lang);
    function group(n) {
      const label = `${n.kind === "all" ? cx.allOf : cx.anyOf}:`;
      const items = (n.children || []).map((ch) => `<li class="dag-rt-child">${cond(ch)}</li>`).join("");
      return `<span class="dag-rt-group dag-rt-${n.kind}"><span class="dag-rt-group-label">${esc(label)}</span><ul class="dag-rt-children">${items}</ul></span>`;
    }
    function cond(n) {
      if (n.kind === "leaf") return `<span class="dag-rt-leaf">${linkifyHtml(n.text || "", refs)}</span>`;
      return group(n);
    }
    function val(text) { return `<strong class="dag-rt-val">${linkifyHtml(text || "", refs)}</strong>`; }
    function render(n) {
      if (n.kind === "priority") {
        let html = "";
        if (n.headline) html += `<p class="dag-rt-headline">${linkifyHtml(n.headline, refs)}</p>`;
        if (n.cases && n.cases.length) {
          html += "<ol class=\"dag-rt-cases\">";
          for (const c of n.cases) {
            const isElse = c.when == null;
            // Word order mirrors HtmlDocRenderer (value, then the connector) — the
            // packs' connector words were written for that position.
            if (isElse) html += `<li class="dag-rt-case dag-rt-else"><span class="dag-rt-case-val">${val(c.value)}</span><span class="dag-rt-if"> ${esc(cx.otherwise)}</span></li>`;
            else html += `<li class="dag-rt-case"><span class="dag-rt-case-val">${val(c.value)}</span><span class="dag-rt-if"> ${esc(cx.if)} </span>${cond(c.when)}</li>`;
          }
          html += "</ol>";
        }
        if (n.children && n.children.length) {
          html += `<div class="dag-rt-cond-block">${n.children.map((ch) => `<div>${cond(ch)}</div>`).join("")}</div>`;
        }
        return `<div class="dag-rt-priority">${html}</div>`;
      }
      if (n.kind === "all" || n.kind === "any") return group(n);
      return `<span class="dag-rt-leaf">${linkifyHtml(n.text || "", refs)}</span>`;
    }
    return `<div class="dag-rt">${render(node)}</div>`;
  }

  // Wire data-ref-table/field links (chips + inline refs + rule-tree refs) to navigation.
  function wireRefLinks(root) {
    root.querySelectorAll("[data-ref-table][data-ref-field]").forEach((a) => {
      a.addEventListener("click", (e) => {
        if (e.metaKey || e.ctrlKey || e.shiftKey) return;
        e.preventDefault();
        routing.navigate(a.getAttribute("data-ref-table"), a.getAttribute("data-ref-field"));
      });
    });
  }

  function typeBadgeHtml(type, size) {
    const tone = R().typeTone(type);
    const label = tt("type_" + type) || R().typeLabel(type);
    return `<span class="tb tb-${tone} tb-${size || "md"}"><span class="tb-glyph">${esc(R().typeGlyph(type))}</span><span class="tb-label">${esc(label)}</span></span>`;
  }

  // ════════════════════════════════════════════════════════════════════════
  //  HEADER (back / home / crumbs + narration slider + gear)
  // ════════════════════════════════════════════════════════════════════════
  function renderHeader(crumbs) {
    const bar = document.createElement("div");
    bar.className = "dag-topbar";

    const left = document.createElement("div");
    left.className = "dag-nav-left";
    const back = document.createElement("button");
    back.type = "button"; back.className = "dag-back"; back.textContent = tt("back");
    back.title = tt("backTitle"); back.onclick = () => routing.onBack();
    left.appendChild(back);
    const home = document.createElement("button");
    home.type = "button"; home.className = "dag-home"; home.textContent = tt("home");
    home.title = tt("homeTitle"); home.onclick = () => routing.onHome();
    left.appendChild(home);

    if (crumbs && crumbs.length) {
      const trail = document.createElement("span");
      trail.className = "dag-crumb-trail";
      const sep0 = document.createElement("span"); sep0.className = "dag-crumb-sep"; sep0.textContent = "·";
      trail.appendChild(sep0);
      crumbs.forEach((c, i) => {
        if (i > 0) { const s = document.createElement("span"); s.className = "dag-crumb-sep"; s.textContent = "›"; trail.appendChild(s); }
        if (typeof c === "string") {
          const span = document.createElement("span"); span.className = "dag-crumb-text"; span.textContent = c; trail.appendChild(span);
        } else if (c.index) {
          const a = document.createElement("a"); a.className = "dag-crumb-index-link"; a.href = routing.cfg.mode === "hash" ? "#/dag" : indexPath();
          a.textContent = c.label || tt("tablesCrumb");
          a.onclick = (e) => { if (e.metaKey || e.ctrlKey) return; e.preventDefault(); routing.navigateTable(""); };
          trail.appendChild(a);
        } else if (c.table) {
          trail.appendChild(renderTableLink(c.table, c.table, "dag-crumb-table-link"));
        }
      });
      left.appendChild(trail);
    }
    bar.appendChild(left);

    const right = document.createElement("div");
    right.className = "dag-nav-right";
    right.appendChild(renderNarrationSlider());
    right.appendChild(renderGear());
    bar.appendChild(right);
    return bar;
  }

  // The global 3-way RuleSpeak®·English·Formula segmented control. Built fresh
  // per render (not a module-level constant) so it always reflects the
  // current `lang`.
  function narrationOptions() {
    return [
      { value: "rulespeak", label: tt("narrRulespeak"), hint: tt("narrRulespeakHint") },
      { value: "english",   label: tt("narrEnglish"),   hint: tt("narrEnglishHint") },
      { value: "formula",   label: tt("narrFormula"),   hint: tt("narrFormulaHint") },
    ];
  }
  function renderNarrationSlider() {
    const seg = document.createElement("div");
    seg.className = "dag-narr-seg"; seg.setAttribute("role", "radiogroup");
    seg.setAttribute("aria-label", tt("narrAriaLabel"));
    const mode = prefs.narrationMode();
    for (const o of narrationOptions()) {
      const b = document.createElement("button");
      b.type = "button"; b.setAttribute("role", "radio");
      b.setAttribute("aria-checked", String(mode === o.value));
      b.className = `dag-narr-seg-opt${mode === o.value ? " is-active" : ""} dag-narr-${o.value}`;
      b.title = o.hint; b.textContent = o.label;
      b.onclick = () => prefs.setNarrationMode(o.value);
      seg.appendChild(b);
    }
    return seg;
  }

  // The settings gear: a ⚙︎ button opening a popup of independent doc-element
  // checkboxes. Controls which sections show in the hover card AND the field page.
  function renderGear() {
    const wrap = document.createElement("div");
    wrap.className = "dag-gear-wrap";
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "dag-gear"; btn.textContent = "⚙︎";
    btn.title = tt("gearTitle");
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", tt("gearAriaLabel"));
    wrap.appendChild(btn);

    let pop = null;
    function close() {
      if (pop) { pop.remove(); pop = null; }
      btn.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", onDocClick, true);
    }
    function onDocClick(e) { if (!wrap.contains(e.target)) close(); }
    function open() {
      pop = document.createElement("div");
      pop.className = "dag-gear-pop";
      const title = document.createElement("div");
      title.className = "dag-gear-pop-title"; title.textContent = tt("gearPopTitle");
      pop.appendChild(title);
      const elems = prefs.docElements();
      for (const d of DOC_ELEMENTS) {
        const label = document.createElement("label");
        label.className = "dag-gear-opt";
        const cb = document.createElement("input");
        cb.type = "checkbox"; cb.checked = !!elems[d.key];
        cb.onchange = () => prefs.setDocElement(d.key, cb.checked);
        const lab = document.createElement("span");
        lab.className = "dag-gear-opt-label"; lab.textContent = tt(d.labelKey);
        const hint = document.createElement("span");
        hint.className = "dag-gear-opt-hint"; hint.textContent = tt(d.hintKey);
        label.appendChild(cb); label.appendChild(lab); label.appendChild(hint);
        pop.appendChild(label);
      }
      const reset = document.createElement("button");
      reset.type = "button"; reset.className = "dag-gear-reset"; reset.textContent = tt("gearReset");
      reset.onclick = () => { prefs.resetDocElements(); };
      pop.appendChild(reset);
      wrap.appendChild(pop);
      btn.setAttribute("aria-expanded", "true");
      // Defer so the opening click doesn't immediately close it.
      setTimeout(() => document.addEventListener("click", onDocClick, true), 0);
    }
    btn.onclick = (e) => { e.stopPropagation(); if (pop) close(); else open(); };
    return wrap;
  }

  function indexPath() {
    return global.EffortlessExplainerRouting.indexPath(routing.cfg);
  }

  // ════════════════════════════════════════════════════════════════════════
  //  PAGES
  // ════════════════════════════════════════════════════════════════════════
  function renderTablesIndex(container) {
    ensureRouting();
    lastRender = { kind: "index", container };
    container.innerHTML = "";
    container.className = "dag-page " + prefs.docElementClasses();
    container.appendChild(renderHeader([{ index: true }]));

    const hero = document.createElement("header");
    hero.className = "dag-hero dag-hero-calc";
    hero.innerHTML = `<h1 class="dag-title">${esc(tt("ontologyTitle"))}</h1>` +
      `<p class="dag-subtitle"><span class="dag-subtitle-human">${esc(tt("ontologyLead"))}</span></p>`;
    container.appendChild(hero);

    const grid = document.createElement("div");
    grid.className = "dag-table-grid";
    for (const t of R().listTables()) {
      const card = renderTableLink(t.table, "", "dag-table-card");
      card.innerHTML =
        `<span class="dag-table-card-name">${esc(t.table)}</span>` +
        `<span class="dag-table-card-human">${esc(humanizeField(t.table))}</span>` +
        `<span class="dag-table-card-meta">${esc(tt("fieldsCount", t.fieldCount))} · ${esc(tt("derivedCount", t.derivedCount))} · ${esc(tt("relCount", t.relationshipCount))}</span>` +
        (t.description ? `<span class="dag-table-card-desc">${esc(t.description)}</span>` : "");
      grid.appendChild(card);
    }
    container.appendChild(grid);
    wireRefLinks(container);
  }

  function renderTablePage(container, table) {
    ensureRouting();
    lastRender = { kind: "table", container, table };
    container.innerHTML = "";
    container.className = "dag-page " + prefs.docElementClasses();
    container.appendChild(renderHeader([{ index: true }, { table }]));
    if (!R().tableExists(table)) {
      const d = document.createElement("div"); d.className = "muted"; d.textContent = tt("tableNotFound");
      container.appendChild(d); return;
    }
    const mode = prefs.narrationMode();
    const hero = document.createElement("header");
    hero.className = "dag-hero dag-hero-rel";
    const desc = R().tableDescription(table);
    hero.innerHTML = `<h1 class="dag-title">${esc(table)}</h1>` +
      `<p class="dag-subtitle"><span class="dag-subtitle-human">${esc(humanizeField(table))}</span></p>` +
      (desc ? `<p class="dag-description">${esc(desc)}</p>` : "");
    container.appendChild(hero);

    const list = document.createElement("div");
    list.className = "dag-col-list";
    for (const col of R().tableColumns(table)) {
      const row = renderFieldLink(table, col.field, "", `dag-col dag-col-${R().typeTone(col.type)}`);
      let explain = "";
      if (col.type !== "raw" && col.type !== "relationship") {
        if (mode === "rulespeak") {
          const rs = ruleSpeakFor(table, col.field);
          if (rs && rs.rule) explain = renderRuleRichHtml(rs.rule, tonedRefs(rs));
        }
        if (!explain) {
          const eng = R().englishForFormula(col.formula);
          if (eng) explain = esc(eng) + ".";
        }
      }
      if (!explain && col.description) explain = esc(col.description);
      row.innerHTML =
        `<span class="dag-col-head">${typeBadgeHtml(col.type, "sm")}` +
        `<span class="dag-col-name">${esc(col.field)}</span>` +
        `<span class="dag-col-human">${esc(humanizeField(col.field))}</span>` +
        (col.nullable ? `<span class="dag-pill dag-pill-muted">${esc(tt("nullable"))}</span>` : "") + `</span>` +
        (explain ? `<span class="dag-col-explain">${explain}</span>` : "") +
        (col.type === "relationship" && col.relatedTo
          ? `<span class="dag-col-rel">→ <a class="dag-col-rel-link" href="${esc(tableHrefSafe(col.relatedTo))}" data-table-link="${esc(col.relatedTo)}">${esc(col.relatedTo)}</a></span>` : "");
      list.appendChild(row);
    }
    container.appendChild(list);
    // Relationship → related-table links inside column rows.
    container.querySelectorAll("[data-table-link]").forEach((a) => {
      a.addEventListener("click", (e) => {
        if (e.metaKey || e.ctrlKey) return; e.preventDefault();
        e.stopPropagation();
        routing.navigateTable(a.getAttribute("data-table-link"));
      });
    });
    wireRefLinks(container);
  }

  function renderFieldPage(container, table, field) {
    ensureRouting();
    lastRender = { kind: "field", container, table, field };
    container.innerHTML = "";
    container.className = "dag-page " + prefs.docElementClasses();
    const dag = R().resolveDag(table, field);
    if (!dag) {
      container.appendChild(renderHeader([{ index: true }, { table }, field]));
      const d = document.createElement("div"); d.className = "muted"; d.textContent = tt("fieldNotFound");
      container.appendChild(d); return;
    }
    const mode = prefs.narrationMode();
    const elems = prefs.docElements();
    const tone = R().typeTone(dag.type);
    const rs = ruleSpeakFor(table, field);
    const refs = tonedRefs(rs);

    container.appendChild(renderHeader([{ index: true }, { table: dag.table }, dag.field]));

    // Hero (with the owning table as a link).
    const hero = document.createElement("header");
    hero.className = `dag-hero dag-hero-${tone}`;
    let metaPills = typeBadgeHtml(dag.type, "md");
    if (dag.depth > 0) metaPills += `<span class="dag-pill dag-pill-depth">${esc(tt("hopsFromGround", dag.depth))}</span>`;
    metaPills += `<span class="dag-pill">${esc(dag.datatype)}</span>`;
    if (dag.nullable) metaPills += `<span class="dag-pill dag-pill-muted">${esc(tt("nullable"))}</span>`;
    hero.innerHTML =
      `<div class="dag-hero-meta">${metaPills}</div>` +
      `<h1 class="dag-title">${esc(dag.field)}</h1>` +
      `<p class="dag-subtitle"><a class="dag-subtitle-table dag-subtitle-table-link" href="${esc(tableHrefSafe(dag.table))}" data-table-link="${esc(dag.table)}">${esc(dag.table)}</a> · <span class="dag-subtitle-human">${esc(humanizeField(dag.field))}</span></p>` +
      (dag.description ? `<p class="dag-description elem elem-desc">${esc(dag.description)}</p>` : "");
    container.appendChild(hero);

    // The rule card.
    if (dag.type === "raw" || dag.type === "relationship") {
      container.appendChild(renderGroundTruthCard(dag));
    } else if (mode === "rulespeak") {
      container.appendChild(renderRuleSpeakCard(dag, rs, refs));
    } else if (mode === "english") {
      container.appendChild(renderEnglishCard(dag, refs));
    } else {
      container.appendChild(renderFormulaCard(dag));
    }

    if (elems.inputs && dag.upstream.length) container.appendChild(renderInputsSection(dag.upstream, mode));
    container.appendChild(renderConsumersSection(dag.downstream, dag.consumerTransitive));
    if (dag.leaves.length) container.appendChild(renderLeavesSection(dag.leaves));

    // Wire all navigation.
    container.querySelectorAll("[data-table-link]").forEach((a) => {
      a.addEventListener("click", (e) => { if (e.metaKey || e.ctrlKey) return; e.preventDefault(); routing.navigateTable(a.getAttribute("data-table-link")); });
    });
    wireRefLinks(container);
  }

  function renderGroundTruthCard(dag) {
    const sec = document.createElement("section");
    sec.className = "dag-card dag-gt";
    const isRel = dag.type === "relationship";
    let body;
    if (isRel) {
      body = dag.relatedTo
        ? tt("relPointerBody", `<a class="dag-gt-rel-link" href="${esc(tableHrefSafe(dag.relatedTo))}" data-table-link="${esc(dag.relatedTo)}">${esc(dag.relatedTo)}</a>`)
        : tt("relPointerBodyNoLink");
    } else {
      body = tt("groundTruthBody", esc(dag.datatype));
    }
    sec.innerHTML =
      `<div class="dag-gt-glyph">${esc(R().typeGlyph(dag.type))}</div>` +
      `<div><h3 class="dag-gt-title">${esc(isRel ? tt("relationshipPointer") : tt("groundTruth"))}</h3>` +
      `<p class="dag-gt-body">${body}</p>` +
      (isRel && dag.relatedTo ? `<p class="dag-gt-rel-cta"><a class="dag-gt-rel-btn" href="${esc(tableHrefSafe(dag.relatedTo))}" data-table-link="${esc(dag.relatedTo)}">${esc(tt("openTable", dag.relatedTo))}</a></p>` : "") +
      `</div>`;
    return sec;
  }

  // Some packs end their own sentences (ja "。", hi "।"); add a period only when
  // the rendered rule does not already end in sentence-final punctuation.
  function ruleSentenceHtml(rule, refs) {
    const end = /[.。।!?！？]$/.test(String(rule).replace(/[*_\s]+$/, "")) ? "" : ".";
    return renderRuleRichHtml(rule, refs) + end;
  }

  function renderRuleSpeakCard(dag, rs, refs) {
    const sec = document.createElement("section");
    sec.className = "dag-card dag-rulespeak elem elem-rulespeak";
    let inner = `<h3 class="dag-card-title">${esc(tt("ruleCardTitle"))}</h3>`;
    if (rs && rs.rule) {
      const mech = rs.mechanical ? ` <span class="dag-rs-mech" title="${esc(tt("mechanicalTitle"))}"> ${esc(tt("mechanicalFlag"))}</span>` : "";
      const ruleBody = rs.structure
        ? `<div class="dag-english-text">${ruleTreeHtml(rs.structure, refs)}</div>`
        : `<p class="dag-english-text">${ruleSentenceHtml(rs.rule, refs)}</p>`;
      inner += `<div class="dag-english dag-rs-rule"><span class="dag-english-label">${esc(tt("inRuleSpeak"))}${mech}</span>${ruleBody}</div>`;
    } else {
      inner += `<p class="dag-english-text muted">${esc(tt("noRuleRendered", dag.type))}</p>`;
    }
    const obls = R().obligationsForField(dag.table, dag.field, lang);
    if (obls.length) {
      inner += `<div class="dag-rs-obligations"><span class="dag-english-label">${esc(tt("obligations"))}</span><ul class="dag-rs-obl-list">` +
        obls.map((o) => `<li class="dag-rs-obl dag-rs-obl-${o.severity || "hard"}">${renderRuleRichHtml(o.markdown, refs)}</li>`).join("") +
        `</ul></div>`;
    }
    inner += `<p class="dag-formula-hint muted">${esc(dag.formula ? tt("ruleSpeakHintFormula") : tt("ruleSpeakHintNoFormula"))}</p>`;
    sec.innerHTML = inner;
    return sec;
  }

  function renderEnglishCard(dag, refs) {
    const sec = document.createElement("section");
    sec.className = "dag-card dag-formula elem elem-english";
    const english = R().englishForFormula(dag.formula);
    let inner = `<h3 class="dag-card-title">${esc(tt("oneLineFnCardTitle"))}</h3>`;
    if (english) {
      inner += `<div class="dag-english"><span class="dag-english-label">${esc(tt("inEnglish"))}</span><p class="dag-english-text">${linkifyHtml(english, refs)}.</p></div>` +
        `<p class="dag-formula-hint muted">${esc(tt("englishHint"))}</p>`;
    } else {
      inner += `<p class="dag-english-text muted">${tt("noFormulaSentence", esc(dag.type))}</p>`;
    }
    sec.innerHTML = inner;
    return sec;
  }

  function renderFormulaCard(dag) {
    const sec = document.createElement("section");
    sec.className = "dag-card dag-formula elem elem-formula";
    let inner = `<h3 class="dag-card-title">${esc(tt("oneLineFnCardTitle"))}</h3>`;
    if (dag.formula) {
      inner += `<div class="dag-formula-syntax"><span class="dag-formula-label">${esc(tt("asFormula"))}</span><div class="dag-formula-code">${formulaHtml(dag.formula, dag.table)}</div></div>` +
        `<p class="dag-formula-hint muted">${esc(tt("formulaHint"))}</p>`;
    } else {
      inner += `<p class="dag-english-text muted">${tt("noFormulaAtAll", esc(dag.type))}</p>`;
    }
    sec.innerHTML = inner;
    return sec;
  }

  function renderInputsSection(upstream, mode) {
    const sec = document.createElement("section");
    sec.className = "dag-section elem elem-inputs";
    sec.innerHTML = `<h2 class="dag-section-title">▼ ${esc(tt("inputsTitle"))} <span class="dag-count">${upstream.length}</span></h2>` +
      `<p class="dag-section-lead muted">${esc(tt("inputsLead"))}</p>`;
    const grid = document.createElement("div");
    grid.className = "dag-input-grid";
    for (const u of upstream) {
      const tone = R().typeTone(u.type);
      const card = renderFieldLink(u.table, u.field, "", `dag-input dag-input-${tone}`);
      let explain = "";
      if (mode === "rulespeak") {
        const rs = ruleSpeakFor(u.table, u.field);
        if (rs && rs.rule) explain = `<span class="dag-input-english dag-input-rulespeak">${renderRuleRichHtml(rs.rule, tonedRefs(rs))}</span>`;
      }
      if (!explain) {
        const eng = R().englishForFormula(u.formula);
        if (eng) explain = `<span class="dag-input-english">${esc(eng)}.</span>`;
      }
      if (!explain && u.description) explain = `<span class="dag-input-desc">${esc(u.description)}</span>`;
      if (!explain && u.type === "raw") explain = `<span class="dag-input-desc muted">${esc(tt("groundTruthInline", u.datatype))}</span>`;
      card.innerHTML =
        `<span class="dag-input-head">${typeBadgeHtml(u.type, "sm")}` +
        `<span class="dag-input-name">${esc(u.field)}</span>` +
        `<span class="dag-input-table">${esc(u.table)}</span></span>` + explain;
      grid.appendChild(card);
    }
    sec.appendChild(grid);
    return sec;
  }

  function pillHtml(table, field) {
    const node = R().fieldOf(R().rulebook(), table, field);
    const type = (node && node.type) || "raw";
    const tone = R().typeTone(type);
    return `<a class="fc fc-${tone} fc-pill" href="${esc(refHref(table, field))}" data-ref-table="${esc(table)}" data-ref-field="${esc(field)}">` +
      `<span class="fc-glyph">${esc(R().typeGlyph(type))}</span>` +
      `<span class="fc-table">${esc(table)}.</span>` +
      `<span class="fc-name">${esc(humanizeField(field))}</span></a>`;
  }

  function renderConsumersSection(direct, transitive) {
    const sec = document.createElement("section");
    sec.className = "dag-section elem elem-consumers";
    const transitiveOnly = (transitive || []).filter((t) => !direct.some((d) => d.table === t.table && d.field === t.field));
    if (!direct.length && !transitiveOnly.length) {
      sec.innerHTML = `<h2 class="dag-section-title">▼ ${esc(tt("consumersTitle"))} <span class="dag-count">0</span></h2>` +
        `<p class="muted">${esc(tt("consumersEmpty"))}</p>`;
      return sec;
    }
    let inner = `<h2 class="dag-section-title">▼ ${esc(tt("consumersTitle"))} <span class="dag-count">${direct.length} ${esc(tt("consumersDirect"))}</span>` +
      (transitiveOnly.length ? `<span class="dag-count dag-count-muted">+${transitiveOnly.length} ${esc(tt("consumersTransitive"))}</span>` : "") + `</h2>` +
      `<p class="dag-section-lead muted">${esc(tt("consumersLead"))}</p>`;
    if (direct.length) {
      inner += `<div class="dag-pill-row">${direct.map((d) => pillHtml(d.table, d.field)).join("")}</div>`;
    }
    if (transitiveOnly.length) {
      inner += `<details class="dag-transitive"><summary>${esc(tt("showTransitive", transitiveOnly.length))}</summary>` +
        `<div class="dag-pill-row dag-pill-row-faded">${transitiveOnly.map((t) => pillHtml(t.table, t.field)).join("")}</div></details>`;
    }
    sec.innerHTML = inner;
    return sec;
  }

  function renderLeavesSection(leaves) {
    const sec = document.createElement("section");
    sec.className = "dag-section dag-section-leaves";
    sec.innerHTML = `<h2 class="dag-section-title">▼ ${esc(tt("leavesTitle"))} <span class="dag-count">${leaves.length}</span></h2>` +
      `<p class="dag-section-lead muted">${esc(tt("leavesLead"))}</p>` +
      `<div class="dag-pill-row">${leaves.map((l) => pillHtml(l.table, l.field)).join("")}</div>`;
    return sec;
  }

  // ════════════════════════════════════════════════════════════════════════
  //  MODAL (routing mode === "modal")
  // ════════════════════════════════════════════════════════════════════════
  function ensureModal() {
    let modal = document.getElementById("effortless-explainer-modal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "effortless-explainer-modal";
    modal.className = "dag-modal hidden";
    modal.innerHTML =
      '<div class="dag-modal-backdrop"></div><div class="dag-modal-panel"><button type="button" class="dag-modal-close">×</button><div id="effortless-explainer-modal-body"></div></div>';
    document.body.appendChild(modal);
    modal.querySelector(".dag-modal-backdrop").onclick = closeModal;
    modal.querySelector(".dag-modal-close").onclick = closeModal;
    return modal;
  }
  function openModal(table, field) {
    const modal = ensureModal();
    renderFieldPage(modal.querySelector("#effortless-explainer-modal-body"), table, field);
    modal.classList.remove("hidden");
  }
  function closeModal() {
    const modal = document.getElementById("effortless-explainer-modal");
    if (modal) modal.classList.add("hidden");
  }

  // ════════════════════════════════════════════════════════════════════════
  //  HOVER MICRO-PAGE over cells (sticky; dialect follows narration + gear)
  // ════════════════════════════════════════════════════════════════════════
  function cancelHoverClose() {
    if (hoverCloseTimer !== null) { clearTimeout(hoverCloseTimer); hoverCloseTimer = null; }
  }
  function removeHoverCard() {
    if (activeHoverCard) { activeHoverCard.remove(); activeHoverCard = null; }
  }
  function scheduleHoverClose() {
    cancelHoverClose();
    hoverCloseTimer = setTimeout(() => { removeHoverCard(); hoverCloseTimer = null; }, CLOSE_DELAY_MS);
  }
  function positionHoverCard(shell, anchor) {
    const vw = window.innerWidth, vh = window.innerHeight;
    const cardW = Math.min(CARD_W, vw - 2 * MARGIN);
    const cardLeft = Math.min(Math.max(anchor.right - cardW, MARGIN), vw - cardW - MARGIN);
    const spaceBelow = vh - anchor.bottom - GAP - MARGIN;
    const spaceAbove = anchor.top - GAP - MARGIN;
    const placeBelow = spaceBelow >= EST_CARD_H || spaceBelow >= spaceAbove;
    const maxH = Math.max(120, placeBelow ? spaceBelow : spaceAbove);
    let cardTop = placeBelow ? anchor.bottom + GAP : anchor.top - GAP - Math.min(EST_CARD_H, maxH);
    cardTop = Math.min(Math.max(cardTop, MARGIN), vh - MARGIN - Math.min(EST_CARD_H, maxH));
    shell.style.position = "fixed";
    shell.style.left = `${cardLeft - SAFETY}px`;
    shell.style.top = `${cardTop - SAFETY}px`;
    shell.style.setProperty("--dag-card-maxh", `${Math.round(maxH)}px`);
  }

  function hoverDialectHtml(dag, mode, elems) {
    // Raw / relationship cells have no rule to narrate.
    if (dag.type === "raw") {
      return `<span class="dag-hovercard-gt">${tt("hoverGroundTruth", dag.datatype ? esc(dag.datatype) : "")}</span>`;
    }
    if (dag.type === "relationship") {
      return `<span class="dag-hovercard-gt">${esc(tt("hoverRelPointer"))}</span>`;
    }
    if (mode === "rulespeak" && elems.rulespeak) {
      const rs = ruleSpeakFor(dag.table, dag.field);
      const body = rs && rs.rule
        ? `<span class="dag-hovercard-english-text">${ruleSentenceHtml(rs.rule, tonedRefs(rs))}</span>`
        : `<span class="dag-hovercard-english-text dag-hovercard-muted">${esc(tt("hoverNoRule"))}</span>`;
      return `<span class="dag-hovercard-english"><span class="dag-hovercard-label">${esc(tt("inRuleSpeak"))}</span>${body}</span>`;
    }
    if (mode === "english" && elems.english) {
      const rs = ruleSpeakFor(dag.table, dag.field);
      const eng = R().englishForFormula(dag.formula);
      const body = eng
        ? `<span class="dag-hovercard-english-text">${linkifyHtml(eng, tonedRefs(rs))}.</span>`
        : `<span class="dag-hovercard-english-text dag-hovercard-muted">${esc(tt("hoverNoFormula"))}</span>`;
      return `<span class="dag-hovercard-english"><span class="dag-hovercard-label">${esc(tt("inEnglish"))}</span>${body}</span>`;
    }
    if (mode === "formula" && elems.formula) {
      const body = dag.formula
        ? `<span class="dag-hovercard-formula-code">${formulaHtml(dag.formula, dag.table)}</span>`
        : `<span class="dag-hovercard-english-text dag-hovercard-muted">${esc(tt("hoverNoFormula"))}</span>`;
      return `<span class="dag-hovercard-formula"><span class="dag-hovercard-label">${esc(tt("asFormula"))}</span>${body}</span>`;
    }
    return ""; // current dialect disabled in settings → show nothing for it
  }

  function openHoverCard(table, field, anchor) {
    cancelHoverClose();
    removeHoverCard();
    const dag = R().resolveDag(table, field);
    if (!dag || !anchor) return;
    const tone = R().typeTone(dag.type);
    const mode = prefs.narrationMode();
    const elems = prefs.docElements();

    const shell = document.createElement("span");
    shell.className = "dag-hovercard-shell dag-hovercard-shell-fixed";
    shell.addEventListener("mouseenter", cancelHoverClose);
    shell.addEventListener("mouseleave", scheduleHoverClose);

    let inputsHtml = "";
    if (elems.inputs && dag.upstream.length) {
      inputsHtml = `<span class="dag-hovercard-inputs"><span class="dag-hovercard-label">${esc(tt("hoverInputs"))} <span class="dag-hovercard-count">${dag.upstream.length}</span></span>` +
        `<span class="dag-hovercard-input-row">${dag.upstream.map((u) => pillHtml(u.table, u.field)).join("")}</span></span>`;
    }

    shell.innerHTML =
      `<span class="dag-hovercard dag-hovercard-${tone}" role="dialog">` +
      `<span class="dag-hovercard-head">${typeBadgeHtml(dag.type, "sm")}` +
      `<span class="dag-hovercard-where"><span class="dag-hovercard-table">${esc(table)}</span>` +
      `<span class="dag-hovercard-dot">·</span><span class="dag-hovercard-field">${esc(humanizeField(field))}</span></span></span>` +
      (elems.desc && dag.description ? `<span class="dag-hovercard-desc">${esc(dag.description)}</span>` : "") +
      hoverDialectHtml(dag, mode, elems) +
      inputsHtml +
      `<span class="dag-hovercard-hint">${esc(tt("hoverHint"))}</span>` +
      `</span>`;

    wireRefLinks(shell);
    positionHoverCard(shell, anchor);
    document.body.appendChild(shell);
    activeHoverCard = shell;
  }

  function attachHoverToGlyph(glyphEl, table, field) {
    glyphEl.addEventListener("mouseenter", () => openHoverCard(table, field, glyphEl.getBoundingClientRect()));
    glyphEl.addEventListener("mouseleave", scheduleHoverClose);
  }

  // ════════════════════════════════════════════════════════════════════════
  //  INLINE CELL ENHANCEMENT (data-er-dag="Table.Field")
  // ════════════════════════════════════════════════════════════════════════
  function dagType(table, field) {
    const f = R().fieldOf(R().rulebook(), table, field);
    return (f && f.type) || "calculated";
  }
  function enhanceCells(root) {
    ensureRouting();
    root = root || document;
    const glyphsOn = prefs.glyphsOn();
    root.querySelectorAll("[data-er-dag]").forEach((el) => {
      if (el.dataset.erEnhanced) return;
      const spec = el.dataset.erDag;
      if (!spec || !spec.includes(".")) return;
      const [table, field] = spec.split(".", 2);
      if (!R().isDerivedField(table, field)) return;
      el.dataset.erEnhanced = "1";
      el.classList.add("dag-cell");
      if (!glyphsOn) el.classList.add("dag-cell-quiet");
      el.title = glyphsOn ? tt("cellHintOn") : tt("cellHintOff");

      const tone = R().typeTone(dagType(table, field));
      const badge = document.createElement("span");
      badge.className = "dag-cell-badge-wrap";
      const link = renderFieldLink(table, field, "", `dag-cell-fx dag-cell-fx-${tone}`);
      const glyph = document.createElement("span");
      glyph.className = "dag-cell-fx-glyph";
      glyph.textContent = R().typeGlyph(dagType(table, field));
      link.appendChild(glyph);
      attachHoverToGlyph(glyph, table, field);
      badge.appendChild(link);
      el.appendChild(badge);

      el.addEventListener("dblclick", (e) => {
        if (e.target.closest("a, button, input, select, textarea")) return;
        e.preventDefault();
        routing.navigate(table, field);
      });
    });
  }

  // ════════════════════════════════════════════════════════════════════════
  //  ROUTING DISPATCH
  // ════════════════════════════════════════════════════════════════════════
  function parseHashRoute() {
    const h = (window.location.hash || "").replace(/^#/, "");
    const m = h.match(/^\/dag\/([^/]+)(?:\/([^/]+))?/);
    if (!m) return null;
    return { table: decodeURIComponent(m[1]), field: m[2] ? decodeURIComponent(m[2]) : null };
  }
  function parsePathRoute() {
    const path = window.location.pathname;
    const m = path.match(/\/dag\/?([^/]*)\/?([^/]*)/);
    if (!m) return null;
    return { table: m[1] ? decodeURIComponent(m[1]) : null, field: m[2] ? decodeURIComponent(m[2]) : null };
  }
  function renderFromHash() {
    const outlet = document.getElementById("effortless-explainer-outlet");
    if (!outlet) return;
    const route = routing.cfg.mode === "path" ? parsePathRoute() : parseHashRoute();
    if (!route || (!route.table && !route.field)) { renderTablesIndex(outlet); return; }
    if (route.table && route.field) renderFieldPage(outlet, route.table, route.field);
    else if (route.table) renderTablePage(outlet, route.table);
    else renderTablesIndex(outlet);
  }

  // ════════════════════════════════════════════════════════════════════════
  //  PROVENANCE TOGGLE PILL (styled — glyph + label + knob; is-on/is-off)
  // ════════════════════════════════════════════════════════════════════════
  function setGlyphsOn(on) {
    prefs.setGlyphs(on);
    document.querySelectorAll(".dag-cell").forEach((el) => el.classList.toggle("dag-cell-quiet", !on));
  }
  function syncTogglePill(btn) {
    const on = prefs.glyphsOn();
    btn.className = `dag-toggle ${on ? "is-on" : "is-off"}`;
    btn.title = on ? tt("provOnTitle") : tt("provOffTitle");
    btn.setAttribute("aria-pressed", String(on));
    btn.innerHTML =
      `<span class="dag-toggle-glyph">ƒ</span>` +
      `<span class="dag-toggle-label">${esc(on ? tt("provOn") : tt("provOff"))}</span>` +
      `<span class="dag-toggle-knob" aria-hidden="true"></span>`;
  }
  function mountToggle(container) {
    container = container || document.body;
    const btn = document.createElement("button");
    btn.type = "button";
    syncTogglePill(btn);
    btn.onclick = () => setGlyphsOn(!prefs.glyphsOn());
    // Keep the pill in sync if prefs change elsewhere.
    prefs.subscribe(() => syncTogglePill(btn));
    container.appendChild(btn);
    return btn;
  }

  // ════════════════════════════════════════════════════════════════════════
  //  INIT
  // ════════════════════════════════════════════════════════════════════════
  let _outletWired = false;
  let _prefsWired = false;
  function init(opts) {
    config = Object.assign({}, config, opts || {});
    lang = CHROME[config.lang] ? config.lang : "en";
    routing = global.EffortlessExplainerRouting.createRouting({
      mode: config.mode || "hash",
      lang,
      hashPrefix: config.hashPrefix,
      fieldPath: config.fieldPath,
      tablePath: config.tablePath,
      indexPath: config.indexPath,
      homePath: config.homePath,
      htmxFieldUrl: config.htmxFieldUrl,
      routing: config.routing,
    });

    if (config.enhance !== false) enhanceCells(document);
    if (config.mountToggle) {
      mountToggle(typeof config.mountToggle === "string" ? document.querySelector(config.mountToggle) : config.mountToggle);
    }

    // Re-render the page on screen when a pref changes (narration mode, gear
    // doc-element toggles, glyphs) so the choice takes effect live. Wired ONCE
    // and host-agnostic: outlet/hash hosts re-render from the hash, while hosts
    // that render into their own container (frameworks) re-render that same
    // container via lastRender. Without this, a framework host's narration
    // slider / gear would appear dead because nothing re-rendered.
    if (!_prefsWired) {
      prefs.subscribe(() => {
        if (document.getElementById("effortless-explainer-outlet")) renderFromHash();
        else rerenderCurrent();
      });
      _prefsWired = true;
    }

    if (document.getElementById("effortless-explainer-outlet")) {
      renderFromHash();
      if (!_outletWired) {
        window.addEventListener("hashchange", renderFromHash);
        _outletWired = true;
      }
    }

    return { routing, enhanceCells, renderFromHash, openModal, closeModal, setGlyphsOn, rerenderCurrent };
  }

  global.EffortlessExplainer = {
    init,
    enhanceCells,
    renderTablesIndex,
    renderTablePage,
    renderFieldPage,
    renderFromHash,
    openModal,
    closeModal,
    setGlyphsOn,
    mountToggle,
    rerenderCurrent,
    prefs,
  };
})(typeof window !== "undefined" ? window : globalThis);
