// ============================================================
// SCRIPT 7 — Exportar dados do app "Entrevistas com a DE" para outra planilha
// ============================================================
const APP_DE_SLUG = "entrevistas-com-a-de";       // ← confirme o slug na URL do app (exemplo: https://podio.com/fluxo-consultoria-2c2quifl81/pame-261/apps/[entrevistas-com-a-de] a parte em colchetes é o nosso slug)
const PLANILHA_DESTINO_DE_ID = "1vODvapC9_VVOzX4ABML18MOebWj6zlh4AECJler3iLw";        // ← ID da planilha destino (controle)
const ABA_DESTINO_DE = "Entrevista DE";                        // ← nome da aba na planilha controle

// Quais campos do app exportar e em que ordem (colunas da planilha)
// Preencha depois de rodar descobrirCamposDE()
const CAMPOS_EXPORTAR_DE = [
  "candidato",          // exemplo — ajuste com os external_ids reais - roda o passo 1 pra descobrir os external IDs
  "coordenacao",
  "sugestao",
  "feedback"
];

// ─── Passo 1: descobrir o APP_ID e os campos do app Entrevistas com a DE ───
function descobrirCamposDE() {
  const token = getPodioToken();
  const authHeader = { Authorization: "OAuth2 " + token };

  // Acha o app pelo slug no workspace
  const spaceUrl = "https://api.podio.com/space/url?url=" + encodeURIComponent(WORKSPACE_URL);
  const spaceResp = UrlFetchApp.fetch(spaceUrl, { method: "get", headers: authHeader, muteHttpExceptions: true });
  const spaceData = JSON.parse(spaceResp.getContentText());

  const appsResp = UrlFetchApp.fetch("https://api.podio.com/app/space/" + spaceData.space_id + "/", {
    method: "get", headers: authHeader, muteHttpExceptions: true
  });
  const apps = JSON.parse(appsResp.getContentText());
  const appAlvo = apps.find(function(app) { return app.url_label === APP_DE_SLUG; });

  if (!appAlvo) {
    Logger.log(" App '" + APP_DE_SLUG + "' não encontrado. Apps disponíveis:");
    apps.forEach(function(a) { Logger.log("  - " + a.url_label); });
    return;
  }

  Logger.log(" APP_ID do " + APP_DE_SLUG + ": " + appAlvo.app_id);
  Logger.log("(Cole esse número em APP_DE_ID abaixo)\n");

  // Lista os campos
  const appResp = UrlFetchApp.fetch("https://api.podio.com/app/" + appAlvo.app_id, {
    method: "get", headers: authHeader, muteHttpExceptions: true
  });
  const app = JSON.parse(appResp.getContentText());
  Logger.log("=== CAMPOS DO APP (use os external_id em CAMPOS_EXPORTAR_DE) ===");
  app.fields.filter(function(f) { return f.status === "active"; }).forEach(function(field) {
    Logger.log("  label: '" + field.label + "' | external_id: '" + field.external_id + "' | type: " + field.type);
  });
}

// ─── Passo 2: cole aqui o APP_ID descoberto ───
const APP_DE_ID = 0; // ← Cole o número descoberto pelo descobrirCamposDE()

// ─── Passo 3: exportar ───
function exportarDEParaPlanilha() {
  const token = getPodioToken();

  // 1. Busca todos os items do app Entrevistas com a DE
  const items = buscarItemsDoAppDE(APP_DE_ID, token);
  Logger.log("Items carregados: " + items.length);
  if (items.length === 0) { Logger.log("Nada a exportar."); return; }

  // 2. Abre a planilha destino
  const planilha = SpreadsheetApp.openById(PLANILHA_DESTINO_DE_ID);
  const sheet = planilha.getSheetByName(ABA_DESTINO_DE);
  if (!sheet) { Logger.log(" Aba '" + ABA_DESTINO_DE + "' não existe na planilha destino."); return; }

  // 3. Monta a matriz: cabeçalho + uma linha por item
  const cabecalho = ["item_id"].concat(CAMPOS_EXPORTAR_DE);
  const linhas = [cabecalho];

  items.forEach(function(item) {
    const linha = [item.item_id];
    CAMPOS_EXPORTAR_DE.forEach(function(externalId) {
      linha.push(extrairValorCampoDE(item, externalId));
    });
    linhas.push(linha);
  });

  // 4. Limpa a aba e escreve tudo de uma vez
  sheet.clearContents();
  sheet.getRange(1, 1, linhas.length, cabecalho.length).setValues(linhas);
  Logger.log(" Exportadas " + items.length + " linhas pra '" + ABA_DESTINO_DE + "'.");
}

// ─── Helpers ───
function buscarItemsDoAppDE(appId, token) {
  const items = [];
  let offset = 0;
  while (true) {
    const resp = UrlFetchApp.fetch("https://api.podio.com/item/app/" + appId + "/filter/", {
      method: "post",
      contentType: "application/json",
      headers: { Authorization: "OAuth2 " + token },
      payload: JSON.stringify({ limit: 500, offset: offset }),
      muteHttpExceptions: true
    });
    const data = JSON.parse(resp.getContentText());
    if (!data.items || data.items.length === 0) break;
    data.items.forEach(function(item) { items.push(item); });
    offset += data.items.length;
    if (offset >= data.total) break;
  }
  return items;
}

function extrairValorCampoDE(item, externalId) {
  const field = item.fields.find(function(f) { return f.external_id === externalId; });
  if (!field || !field.values || field.values.length === 0) return "";

  switch (field.type) {
    case "category":
      return field.values.map(function(v) { return v.value.text; }).join(", ");
    case "email":
    case "phone":
      return field.values.map(function(v) { return v.value; }).join(", ");
    case "date":
      return field.values[0].start || "";
    case "app":
      return field.values.map(function(v) { return v.value.title; }).join(", ");
    case "contact":
      return field.values.map(function(v) { return v.value.name; }).join(", ");
    default: // text — pode vir com HTML
      return limparHtmlDE(field.values[0].value);
  }
}

function limparHtmlDE(html) {
  if (!html) return "";
  let texto = String(html);

  // 1. Converte tags que significam quebra de linha
  texto = texto
    .replace(/<br\s*\/?>/gi, "\n")      // <br>, <br/>, <br />
    .replace(/<\/p>/gi, "\n")            // fim de parágrafo → quebra
    .replace(/<\/div>/gi, "\n")
    .replace(/<\/li>/gi, "\n")
    .replace(/<li[^>]*>/gi, "• ");       // itens de lista viram bullets

  // 2. Remove todas as outras tags
  texto = texto.replace(/<[^>]+>/g, "");

  // 3. Decodifica entidades HTML comuns
  texto = texto
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/&aacute;/gi, "á").replace(/&eacute;/gi, "é")
    .replace(/&iacute;/gi, "í").replace(/&oacute;/gi, "ó")
    .replace(/&uacute;/gi, "ú").replace(/&atilde;/gi, "ã")
    .replace(/&otilde;/gi, "õ").replace(/&ccedil;/gi, "ç")
    .replace(/&acirc;/gi, "â").replace(/&ecirc;/gi, "ê");

  // 4. Limpa quebras de linha excessivas e espaços nas pontas
  texto = texto
    .replace(/\n{3,}/g, "\n\n")   // 3+ quebras seguidas → 2
    .replace(/[ \t]+\n/g, "\n")   // espaços antes de quebra
    .trim();

  return texto;
}

