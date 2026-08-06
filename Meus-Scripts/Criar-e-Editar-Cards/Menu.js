// ============================================================
// SCRIPT 0 — Menu customizado no Sheets
// Roda automaticamente quando a planilha abre e adiciona um menu
// "PAME · Podio" com todas as funções dos outros scripts.
// ============================================================
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("PAME · Podio")
      .addSubMenu(
        SpreadsheetApp.getUi().createMenu("Descobrir IDs")
          .addItem("APP_ID do bd-candidatos", "menu_descobrirAppID")
          .addItem("Campos e items do bd-candidatos", "menu_descobrirCamposEItems")
          .addItem("Campos do app Dinâmica", "menu_descobrirCamposDinamica")
          .addItem("Campos do app Entrevistas com a DE", "menu_descobrirCamposDE")
      )
      .addSeparator()
      .addSubMenu(
        SpreadsheetApp.getUi().createMenu("Planilha → Podio")
          .addItem("Importar em massa (carga inicial)", "menu_importarEmMassa")
          .addItem("Atualizar fotos em massa", "menu_atualizarFotosNoPodio")
      )
      .addSubMenu(
        SpreadsheetApp.getUi().createMenu("Podio → Planilha")
          .addItem("Exportar Dinâmica pra planilha destino", "menu_exportarDinamicaParaPlanilha")
          .addItem("Exportar Entrevistas DE pra planilha destino", "menu_exportarDEParaPlanilha")
      )
      .addSeparator()
      .addSubMenu(
        SpreadsheetApp.getUi().createMenu("Resets")
          .addItem("Resetar resume da importação em massa", "menu_resetarResume")
          .addItem("Resetar resume das fotos", "menu_resetarResumeFotos")
      )
      .addSeparator()
      .addItem("Ver últimos logs", "menu_verLogs")
    .addToUi();
}

// ─── Wrappers ─────────────────────────────────────────────
// Cada wrapper chama a função original, captura o output do Logger
// e mostra num alert no fim — assim o usuário não precisa abrir o editor
// pra ver o resultado.

function menu_descobrirAppID()             { rodarComFeedback_("Descobrir APP_ID",             descobrirAppID); }
function menu_descobrirCamposEItems()      { rodarComFeedback_("Campos e items",               descobrirCamposEItems); }
function menu_descobrirCamposDinamica()    { rodarComFeedback_("Campos do app Dinâmica",       descobrirCamposDinamica); }
function menu_descobrirCamposDE()          { rodarComFeedback_("Campos do app Entrevistas DE", descobrirCamposDE); }
function menu_exportarDinamicaParaPlanilha(){ rodarComConfirmacao_("Exportar Dinâmica",
  "Isso vai LIMPAR a aba destino e reescrever com os dados do Podio. Continuar?",
  exportarDinamicaParaPlanilha); }
function menu_exportarDEParaPlanilha()     { rodarComConfirmacao_("Exportar Entrevistas DE",
  "Isso vai LIMPAR a aba destino e reescrever com os dados do Podio. Continuar?",
  exportarDEParaPlanilha); }
function menu_importarEmMassa()            { rodarComConfirmacao_("Importar em massa",
  "Vai criar items no Podio para cada linha sem item_id. Continuar?",
  importarEmMassa); }
function menu_atualizarFotosNoPodio()      { rodarComConfirmacao_("Atualizar fotos",
  "Vai baixar as fotos da planilha e subir no Podio (retoma de onde parou). Continuar?",
  atualizarFotosNoPodio); }
function menu_resetarResume()              { rodarComFeedback_("Reset importação",             resetarResume); }
function menu_resetarResumeFotos()         { rodarComFeedback_("Reset fotos",                  resetarResumeFotos); }

function menu_verLogs() {
  const logs = Logger.getLog();
  const ui = SpreadsheetApp.getUi();
  if (!logs || !logs.trim()) {
    ui.alert("Sem logs desta sessão. Rode alguma ação primeiro.");
    return;
  }
  ui.alert("Últimos logs", logs.slice(-1500), ui.ButtonSet.OK);
}

// ─── Helpers de execução ─────────────────────────────────
function rodarComFeedback_(titulo, fn) {
  const ui = SpreadsheetApp.getUi();
  Logger.clear();
  try {
    fn();
    const logs = Logger.getLog();
    ui.alert(titulo + " · OK", (logs || "Sem output.").slice(-1500), ui.ButtonSet.OK);
  } catch (err) {
    ui.alert(titulo + " · ERRO", String(err && err.message || err), ui.ButtonSet.OK);
  }
}

function rodarComConfirmacao_(titulo, pergunta, fn) {
  const ui = SpreadsheetApp.getUi();
  const resp = ui.alert(titulo, pergunta, ui.ButtonSet.YES_NO);
  if (resp !== ui.Button.YES) return;
  rodarComFeedback_(titulo, fn);
}
