# -*- coding: utf-8 -*-
"""Generatore del sito francozanghi.it — pagine statiche.

Legge le notizie da sito-sorgente/notizie.json e ricostruisce
l'intero sito: prima pagina, sezioni, pagine degli articoli e
pagine fisse. Si lancia con:  python3 genera.py
"""
import os, html, json, unicodedata, hashlib, datetime

SORGENTE = "sorgente/notizie.json"
USCITA   = "."
POSTA    = "francozanghi@gmail.com"

# pannello delle statistiche e indirizzo del contatore
STATISTICHE = "https://francozanghi.goatcounter.com"
CONTATORE   = STATISTICHE + "/count"

# finche' non ci sono abbastanza visite la colonna mostra i piu' recenti.
# Quando le statistiche bastano si mette True e diventa "Le piu' lette".
PIU_LETTE = False

SEZIONI = [
    ("geopolitica",       "Geopolitica"),
    ("politica-italiana", "Politica italiana"),
    ("cronaca",           "Cronaca"),
    ("attualita",         "Attualità"),
    ("sicilia",           "Sicilia"),
]
SLUG_DI = {nome: slug for slug, nome in SEZIONI}

DESCRIZIONI = {
    "geopolitica":       "Scenari internazionali, equilibri di potere, guerre e trattative.",
    "politica-italiana": "Il governo, il parlamento, i partiti e quello che si muove sotto.",
    "cronaca":           "Fatti, processi, inchieste giudiziarie.",
    "attualita":         "Quello che succede adesso e merita di essere spiegato.",
    "sicilia":           "L'isola raccontata da dentro, oltre la cronaca di giornata.",
}

def versione_stile():
    """Impronta del foglio di stile, così il browser non mostra la versione vecchia."""
    try:
        with open("stile.css", "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except FileNotFoundError:
        return "1"


VSTILE = versione_stile()

MESI = ["gennaio","febbraio","marzo","aprile","maggio","giugno",
        "luglio","agosto","settembre","ottobre","novembre","dicembre"]


def data_estesa(iso):
    a, m, g = iso.split("-")
    return f"{int(g)} {MESI[int(m)-1]} {a}"


FIRMA = "di Franco Zanghì"
DIDASCALIA = ("Immagine generata con l'intelligenza artificiale: "
              "è una rappresentazione della vicenda, non una fotografia del fatto.")


def immagine(n, piccola=False):
    """Blocco dell'immagine, se la notizia ne ha una."""
    if not n.get("immagine"):
        return ""
    base = n["immagine"]
    if piccola:
        return (f'      <a class="figura" href="{n["file"]}">'
                f'<img src="immagini/{base}-p.jpg" alt="" loading="lazy" width="480" height="320"></a>\n')
    return (f'    <figure class="figura grande">\n'
            f'      <img src="immagini/{base}.jpg" alt="" width="1200" height="800">\n'
            f'      <figcaption>{DIDASCALIA}</figcaption>\n'
            f'    </figure>\n')


SCRIPT = """<script>
document.addEventListener("click", function (e) {
  var b = e.target.closest(".avvia");
  if (!b) return;
  var id = b.getAttribute("data-id");
  var c = document.createElement("div");
  c.className = "riquadro";
  var f = document.createElement("iframe");
  f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
  f.title = "Video";
  f.allow = "accelerometer; autoplay; encrypted-media; picture-in-picture";
  f.setAttribute("allowfullscreen", "");
  c.appendChild(f);
  b.parentNode.replaceChild(c, b);
});
</script>
"""


CONTA = ('<script data-goatcounter="' + CONTATORE +
         '" async src="//gc.zgo.at/count.js"></script>\n')


def scheda_video(v, grande=False):
    """Riquadro di un video: anteprima locale, il riquadro parte solo al clic."""
    t = html.escape(v["titolo"])
    classe = "video grande" if grande else "video"
    return f"""      <div class="{classe}" id="v-{v['id']}">
        <button class="avvia" data-id="{v['id']}" aria-label="Avvia il video">
          <img src="immagini/video/{v['id']}.jpg" alt="" loading="lazy" width="320" height="180">
          <span class="triangolo" aria-hidden="true"></span>
        </button>
        <p class="titolo">{t}</p>
        <p class="fuori"><a href="https://www.youtube.com/watch?v={v['id']}" rel="noopener">Guarda su YouTube</a></p>
      </div>
"""


def riquadro_notizia(n, video_per_id):
    """Riquadro «Guarda la video notizia» dentro la pagina dell'articolo."""
    vid = n.get("video")
    if not vid or vid not in video_per_id:
        return ""
    v = video_per_id[vid]
    t = html.escape(v["titolo"])
    return f"""    <aside class="videonotizia">
      <p class="riga">Guarda la video notizia</p>
      <button class="avvia" data-id="{v['id']}" aria-label="Avvia il video">
        <img src="immagini/video/{v['id']}.jpg" alt="" loading="lazy" width="320" height="180">
        <span class="triangolo" aria-hidden="true"></span>
      </button>
      <p class="titolo">{t}</p>
      <p class="fuori"><a href="https://www.youtube.com/watch?v={v['id']}" rel="noopener">Guarda su YouTube</a></p>
    </aside>
"""


# ------------------------------------------------------------------
# reclame di Torre Eoliana (attivita' dell'editore)
# ------------------------------------------------------------------
NEGOZIO = "https://idroponicadomestica.company.site/"

RECLAME = [
    {
        "occhiello": "Offerta lancio",
        "titolo": "La torre Panarea a prezzo di lancio",
        "riga": "L'orto verticale che sta su un balcone: si coltiva senza terra, tutto l'anno.",
        "immagine": "promo-torri.jpg",
        "dove": "https://idroponicadomestica.company.site/Offerta-lancio-c183793751",
    },
    {
        "occhiello": "Affari con l'usato",
        "titolo": "Le torri della fiera, garantite",
        "riga": "Modelli di esposizione, in buone condizioni, a prezzo ridotto fino a esaurimento.",
        "immagine": "promo-usato.jpg",
        "dove": "https://idroponicadomestica.company.site/AFFARI-CON-LUSATO-FIERA-c167699479",
    },
    {
        "occhiello": "Accessori",
        "titolo": "Espansioni, moduli e ricambi",
        "riga": "Livelli in più, modulo di germinazione, bicchieri, fertilizzante e misuratori.",
        "immagine": "promo-torri.jpg",
        "dove": "https://idroponicadomestica.company.site/Accessori-e-elementi-di-espansione-c169873367",
    },
]

ALTRI_RECLAME = [
    ("Il negozio", NEGOZIO),
    ("Torre Eoliana, il sito", "https://torreeoliana.com/"),
]


def reclame(giro=0):
    """Riquadro a pagamento dell'editore: dichiarato, separato dalle notizie."""
    r = RECLAME[giro % len(RECLAME)]
    fuori = 'target="_blank" rel="sponsored noopener"'
    altri = "".join(
        f'      <li><a href="{d}" {fuori}>{html.escape(t)}</a></li>\n'
        for t, d in ALTRI_RECLAME
        if d != r["dove"]
    )
    return f"""    <div class="reclame">
      <p class="cappello avviso">Pubblicità</p>
      <a class="offerta" href="{r['dove']}" {fuori}>
        <img src="immagini/{r['immagine']}" alt="" loading="lazy" width="480" height="320">
        <span class="dove">{html.escape(r['occhiello'])}</span>
        <span class="titolo">{html.escape(r['titolo'])}</span>
        <span class="riga">{html.escape(r['riga'])}</span>
      </a>
      <ul class="altri">
{altri}      </ul>
      <p class="nota">Torre Eoliana è un’attività dell’editore di questo sito.</p>
    </div>
"""


def spalla(elenco_notizie, elenco_video, giro=0):
    """Colonna di sinistra: richiami alle notizie e ai video."""
    t_notizie = "Le pi\u00f9 lette" if PIU_LETTE else "Le ultime notizie"
    t_video   = "I video pi\u00f9 visti" if PIU_LETTE else "Gli ultimi video"
    pezzi = ['  <aside class="spalla">\n']
    if elenco_notizie:
        pezzi.append(f'    <h4 class="cappello">{t_notizie}</h4>\n    <ul class="richiami">\n')
        for n in elenco_notizie[:6]:
            fig = ""
            if n.get("immagine"):
                fig = (f'<img src="immagini/{n["immagine"]}-p.jpg" alt="" '
                       f'loading="lazy" width="480" height="320">')
            pezzi.append(f'      <li><a href="{n["file"]}">{fig}'
                         f'<span class="dove">{html.escape(n["sezione"])}</span>'
                         f'<span class="titolo">{html.escape(n["titolo"])}</span></a></li>\n')
        pezzi.append('    </ul>\n')
    pezzi.append(reclame(giro))
    lunghi = [v for v in elenco_video if v.get("tipo") != "short"][:4]
    if lunghi:
        pezzi.append(f'    <h4 class="cappello">{t_video}</h4>\n    <ul class="richiami">\n')
        for v in lunghi:
            pezzi.append(f'      <li><a href="video.html#v-{v["id"]}">'
                         f'<img src="immagini/video/{v["id"]}.jpg" alt="" '
                         f'loading="lazy" width="320" height="180">'
                         f'<span class="dove">Video</span>'
                         f'<span class="titolo">{html.escape(v["titolo"])}</span></a></li>\n')
        pezzi.append('    </ul>\n')
        pezzi.append('    <p class="tutti"><a href="video.html">Tutti i video</a></p>\n')
    pezzi.append('  </aside>\n')
    return "".join(pezzi)


GIORNI = ["domenica","luned\u00ec","marted\u00ec","mercoled\u00ec",
          "gioved\u00ec","venerd\u00ec","sabato"]

CANALI = [
    ("Facebook",  "https://www.facebook.com/profile.php?id=100092510574016"),
    ("TikTok",    "https://www.tiktok.com/@francozanghi1"),
    ("YouTube",   "https://www.youtube.com/@FrancoZanghi"),
    ("Instagram", "https://www.instagram.com/zanghi.franco/"),
]


def datario():
    """Riquadro della data accanto alla testata. Il programma scrive
    il giorno della costruzione; nel navigatore lo aggiorna l'orologio."""
    oggi = datetime.date.today()
    voci = "".join(
        f'        <li><a href="{d}" target="_blank" rel="noopener">{t}</a></li>\n'
        for t, d in CANALI
    )
    return f"""    <aside class="datario">
      <div class="quando">
        <p class="giorno" id="d-giorno">{GIORNI[(oggi.weekday() + 1) % 7]}</p>
        <p class="numero" id="d-numero">{oggi.day}</p>
        <p class="mese" id="d-mese">{MESI[oggi.month - 1]} {oggi.year}</p>
        <p class="ora" id="d-ora">&nbsp;</p>
      </div>
      <p class="luogo">Patti, Sicilia</p>
      <div class="canali">
        <p class="cappello">Seguimi</p>
        <ul>
{voci}        </ul>
      </div>
    </aside>
"""


OROLOGIO = """<script>
(function () {
  var giorni = ["domenica","luned\u00ec","marted\u00ec","mercoled\u00ec",
                "gioved\u00ec","venerd\u00ec","sabato"];
  var mesi = ["gennaio","febbraio","marzo","aprile","maggio","giugno",
              "luglio","agosto","settembre","ottobre","novembre","dicembre"];
  function pezzi() {
    try {
      var f = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/Rome", year: "numeric", month: "numeric",
        day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false });
      var o = {};
      f.formatToParts(new Date()).forEach(function (p) { o[p.type] = p.value; });
      return o;
    } catch (e) { return null; }
  }
  function scrivi() {
    var o = pezzi();
    if (!o) return;
    var a = +o.year, m = +o.month, g = +o.day;
    var s = new Date(Date.UTC(a, m - 1, g)).getUTCDay();
    var e = document.getElementById("d-giorno");
    if (!e) return;
    e.textContent = giorni[s];
    document.getElementById("d-numero").textContent = g;
    document.getElementById("d-mese").textContent = mesi[m - 1] + " " + a;
    document.getElementById("d-ora").textContent = o.hour + ":" + o.minute;
  }
  scrivi();
  setInterval(scrivi, 20000);
})();
</script>
"""


def menu(attiva=""):
    cl = ' class="attiva"' if attiva == "home" else ""
    voci = [f'    <a href="index.html"{cl}>Prima pagina</a>']
    for slug, nome in SEZIONI:
        cl = ' class="attiva"' if slug == attiva else ""
        voci.append(f'    <a href="{slug}.html"{cl}>{nome}</a>')
    cl = ' class="attiva"' if attiva == "video" else ""
    voci.append(f'    <a href="video.html"{cl}>Video</a>')
    cl = ' class="attiva"' if attiva == "chi-sono" else ""
    voci.append(f'    <a href="chi-sono.html"{cl}>Chi sono</a>')
    return "\n".join(voci)


def pagina(titolo, corpo, attiva="", iniziale=False, colonna=""):
    classe = "testata" if iniziale else "testata interna"
    foglio = "foglio larga" if colonna else "foglio"
    if colonna:
        blocco = ('  <div class="doppia">\n'
                  '  <main class="principale">\n' + corpo + '  </main>\n'
                  + colonna + '  </div>\n')
    else:
        blocco = corpo
    striscione = ('  <a class="banner" href="index.html">'
                  '<img src="immagini/banner.jpg" '
                  'alt="Scenari Globali \u2014 un format audiovisivo di Franco Zangh\u00ec" '
                  'width="1400" height="786"></a>\n')
    if colonna:
        cima = '  <div class="cima">\n' + datario() + striscione + '  </div>\n'
    else:
        cima = striscione
    nome = ("Franco Zanghì" if iniziale
            else '<a href="index.html">Franco Zanghì</a>')
    occhiello = ('<p class="occhiello">Analisi, cronaca e politica internazionale</p>'
                 if iniziale else "")
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titolo}</title>
<link rel="stylesheet" href="stile.css?v={VSTILE}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="immagini/segno-32.png">
<link rel="apple-touch-icon" href="immagini/segno-180.png">
<meta name="theme-color" content="#14456f">
</head>
<body>
<div class="{foglio}">

{cima}

  <header class="{classe}">
    <h1>{nome}</h1>
    {occhiello}
  </header>

  <nav>
{menu(attiva)}
  </nav>

{blocco}

  <footer>
    <p>
      <a href="rettifiche.html">Rettifiche</a> &nbsp;·&nbsp;
      <a href="contatti.html">Contatti</a> &nbsp;·&nbsp;
      <a href="dati-personali.html">Dati personali</a> &nbsp;·&nbsp;
      <a href="condizioni.html">Condizioni d'uso</a>
    </p>
    <p class="gerenza">
      francozanghi.it — Domenico Franco Zanghì, Patti (Messina) — <a href="mailto:{POSTA}">{POSTA}</a><a class="segno" href="{STATISTICHE}" rel="noopener" title="Statistiche" aria-label="Statistiche">·</a>
    </p>
  </footer>

</div>
{SCRIPT}{OROLOGIO if colonna else ''}{CONTA}</body>
</html>
"""


def voce(n, apertura=False):
    t = html.escape(n["titolo"])
    s = html.escape(n["sommario"])
    d = data_estesa(n["data"])
    f = n["file"]
    img = immagine(n, piccola=True)
    if apertura:
        return f"""  <section class="apertura">
    <p class="riga"><span class="sezione">{n['sezione']}</span> &nbsp;·&nbsp; {d}</p>
    <h2><a href="{f}">{t}</a></h2>
{img}    <p>{s}</p>
    <p class="firma">{FIRMA}</p>
  </section>
"""
    return f"""    <article class="voce">
      <p class="riga"><span class="sezione">{n['sezione']}</span> &nbsp;·&nbsp; {d}</p>
      <h3><a href="{f}">{t}</a></h3>
{img}      <p>{s}</p>
      <p class="firma">{FIRMA}</p>
    </article>
"""


def scrivi(nome, contenuto):
    os.makedirs(USCITA, exist_ok=True)
    with open(os.path.join(USCITA, nome), "w", encoding="utf-8") as f:
        f.write(contenuto)


# ------------------------------------------------------------------
# lettura delle notizie
# ------------------------------------------------------------------
with open(SORGENTE, encoding="utf-8") as f:
    notizie = json.load(f)

try:
    with open("sorgente/video.json", encoding="utf-8") as f:
        elenco_video = json.load(f)
except FileNotFoundError:
    elenco_video = []
VIDEO_PER_ID = {v["id"]: v for v in elenco_video}

for n in notizie:
    n["file"] = n["id"] + ".html"
notizie.sort(key=lambda n: n["data"], reverse=True)

# ------------------------------------------------------------------
# pagine degli articoli
# ------------------------------------------------------------------
for n in notizie:
    blocchi = []
    for tipo, testo in n["corpo"]:
        if tipo == "h3":
            blocchi.append(f"    <h3>{html.escape(testo)}</h3>")
        else:
            blocchi.append(f"    <p>{html.escape(testo)}</p>")
    corpo_testo = "\n\n".join(blocchi)

    fonti = ""
    if n.get("fonti"):
        righe = []
        for titolo_fonte, collegamento in n["fonti"]:
            t = html.escape(titolo_fonte)
            if collegamento:
                righe.append(f'        <li><a href="{html.escape(collegamento)}" rel="noopener">{t}</a></li>')
            else:
                righe.append(f"        <li>{t}</li>")
        fonti = ('    <div class="fonti">\n      <h4>Fonti</h4>\n      <ol>\n'
                 + "\n".join(righe) + "\n      </ol>\n")
        if n.get("nota"):
            fonti += f'      <p style="font-size:15px;margin:12px 0 0;color:var(--grigio)">{html.escape(n["nota"])}</p>\n'
        fonti += "    </div>\n"
    elif n.get("riga_fonti"):
        fonti = ('    <div class="fonti">\n      <h4>Fonti</h4>\n'
                 f'      <p style="font-size:15.5px;margin:0;color:var(--grigio)">{html.escape(n["riga_fonti"])}</p>\n'
                 "    </div>\n")

    correzione = ""
    if n.get("correzione"):
        correzione = ('    <div class="correzione">\n'
                      f'      <strong>Correzione del {data_estesa(n["correzione"]["data"])}.</strong> '
                      f'{html.escape(n["correzione"]["testo"])}\n    </div>\n')

    corpo = f"""  <section class="testo">
    <p class="riga"><span class="sezione">{n['sezione']}</span> &nbsp;·&nbsp; {data_estesa(n['data'])}</p>
    <h2>{html.escape(n['titolo'])}</h2>
{immagine(n)}    <p class="sommario">{html.escape(n['sommario'])}</p>
    <p class="firma">{FIRMA}</p>
{riquadro_notizia(n, VIDEO_PER_ID)}

{corpo_testo}

{fonti}{correzione}  </section>
"""
    scrivi(n["file"], pagina(f"{n['titolo']} — Franco Zanghì", corpo,
                             attiva=SLUG_DI.get(n["sezione"], "")))

# ------------------------------------------------------------------
# prima pagina
# ------------------------------------------------------------------
if notizie:
    corpo = voce(notizie[0], apertura=True) + '\n  <div class="elenco">\n\n'
    for n in notizie[1:]:
        corpo += voce(n) + "\n"
    corpo += "  </div>\n"
else:
    corpo = '  <section class="testo"><p>Nessun articolo pubblicato.</p></section>\n'
COLONNA = spalla(notizie, elenco_video, 0)
scrivi("index.html", pagina("Franco Zanghì", corpo, attiva="home", iniziale=True,
                            colonna=COLONNA))

# ------------------------------------------------------------------
# pagine di sezione
# ------------------------------------------------------------------
for _giro, (slug, nome) in enumerate(SEZIONI):
    pezzi = [n for n in notizie if n["sezione"] == nome]
    corpo = f"""  <section class="testo">
    <h2>{nome}</h2>
    <p class="sommario">{DESCRIZIONI[slug]}</p>
  </section>

  <div class="elenco">

"""
    if pezzi:
        for p in pezzi:
            corpo += voce(p) + "\n"
    else:
        corpo += '    <article class="voce"><p>Nessun articolo in questa sezione.</p></article>\n'
    corpo += "  </div>\n"
    scrivi(f"{slug}.html", pagina(f"{nome} — Franco Zanghì", corpo, attiva=slug,
                                  colonna=spalla(notizie, elenco_video, _giro + 1)))

# ------------------------------------------------------------------
# pagina dei video
# ------------------------------------------------------------------
lunghi = [v for v in elenco_video if v.get("tipo") != "short"]
corti  = [v for v in elenco_video if v.get("tipo") == "short"]
corpo = """  <section class="testo">
    <h2>Video</h2>
    <p class="sommario">Le video notizie e le serie del canale. Il video parte dentro questa pagina solo quando lo avvii tu: finché non clicchi, verso YouTube non parte nulla.</p>
  </section>

  <div class="elencovideo">

"""
for v in lunghi:
    corpo += scheda_video(v) + "\n"
corpo += "  </div>\n"
if corti:
    corpo += """
  <section class="testo">
    <h3>Brevi</h3>
  </section>

  <div class="elencovideo">

"""
    for v in corti:
        corpo += scheda_video(v) + "\n"
    corpo += "  </div>\n"
scrivi("video.html", pagina("Video — Franco Zanghì", corpo, attiva="video"))

# ------------------------------------------------------------------
# pagine fisse
# ------------------------------------------------------------------
chi_sono = """  <section class="testo">
    <h2>Chi sono</h2>

    <p>Mi chiamo Franco Zanghì. Racconto politica internazionale, cronaca italiana e quello che accade in Sicilia, dove vivo e lavoro.</p>

    <p>Ho cominciato con la fotografia, nei primi anni ottanta, e dalla fotografia sono passato al giornalismo collaborando con alcuni quotidiani siciliani. Nel 1995 ho prodotto con mezzi miei un programma televisivo dedicato ai rally, &laquo;A tutto gas&raquo;, acquistato poi da un centinaio di emittenti private. Dal 1998 ho iniziato a lavorare con la televisione pubblica: nel 2000 la terza rete ha acquistato il mio primo documentario, girato in Albania, &laquo;Shqiperia &mdash; La Terra delle Aquile&raquo;. Negli anni successivi sono arrivati altri lavori, tra cui una serie in quattro puntate sulla Turchia, un documentario girato in Kerala e &laquo;Shalom &mdash; Viaggio in Terra Santa&raquo;. Per una dozzina d'anni ho lavorato come operatore e autore indipendente per la Rai e per Sky. Ho insegnato fotografia e montaggio alla Rome University of Fine Arts. Ho superato l'esame di idoneit&agrave; professionale nel 2004.</p>

    <p>Oggi scrivo e produco per i canali che ho fondato. ScenariGlobali si occupa di scenari internazionali. Patti Chiari News racconta la Sicilia e la cronaca che i giornali nazionali non arrivano a coprire. Lavoro da solo: scelgo gli argomenti, verifico, scrivo e leggo i testi.</p>

    <h3>Come lavoro</h3>

    <p>Mi occupo di storie che hanno bisogno di tempo, non di reazioni immediate. Scelgo pochi argomenti e li seguo finch&eacute; serve. Non pubblico una notizia che non abbia almeno una fonte che posso indicare, e le fonti di ogni pezzo sono elencate in fondo al pezzo stesso. Quando un'informazione non &egrave; verificabile lo scrivo, invece di darla per certa. Quando la notizia &egrave; frutto di lavoro mio, con fonti diverse da quelle pubbliche, lo dichiaro in fondo all'articolo.</p>

    <p>Sbaglio come tutti. Quando capita, correggo, e la correzione resta visibile con la sua data. Se trovi un errore in quello che ho scritto, segnalamelo: trovi come farlo nella <a href="contatti.html">pagina dei contatti</a>.</p>
  </section>
"""
scrivi("chi-sono.html", pagina("Chi sono — Franco Zanghì", chi_sono, attiva="chi-sono"))

rettifiche = """  <section class="testo">
    <h2>Rettifiche</h2>
    <p class="sommario">Gli errori si correggono. Qui resta traccia di quelli corretti, con la loro data.</p>

    <p>Quando un articolo contiene un errore di fatto, lo correggo nel testo e segnalo la correzione in fondo all'articolo stesso, indicando che cosa &egrave; stato cambiato e quando. L'articolo non viene cancellato e la versione corretta resta consultabile.</p>

    <p>Se trovi un errore in qualcosa che ho pubblicato, scrivimi: indica l'articolo, il punto contestato e, se puoi, la fonte che lo smentisce. Rispondo a tutte le segnalazioni circostanziate.</p>

    <h3>Correzioni pubblicate</h3>

__CORREZIONI__
  </section>
"""

_corretti = [n for n in notizie if n.get("correzione")]
_corretti.sort(key=lambda n: n["correzione"]["data"], reverse=True)
if _corretti:
    _righe = []
    for n in _corretti:
        _righe.append(
            '    <p><strong>%s</strong> &mdash; '
            '<a href="%s.html">%s</a>. %s</p>'
            % (data_estesa(n["correzione"]["data"]),
               n["id"],
               html.escape(n["titolo"]),
               html.escape(n["correzione"]["testo"]))
        )
    _blocco = "\n".join(_righe)
else:
    _blocco = "    <p>Nessuna correzione finora.</p>"

rettifiche = rettifiche.replace("__CORREZIONI__", _blocco)
scrivi("rettifiche.html", pagina("Rettifiche — Franco Zanghì", rettifiche))

contatti = """  <section class="testo">
    <h2>Contatti</h2>
    <p class="sommario">Per segnalazioni, documenti, correzioni e richieste.</p>

    <p>Scrivimi a <a href="mailto:%s">%s</a>.</p>

    <p>Se hai una segnalazione o un documento che ritieni di interesse pubblico, scrivimi indicando di cosa si tratta, senza allegare nulla al primo messaggio. Concordiamo come farlo arrivare.</p>

    <p>Non pubblico materiale di cui non posso verificare l'origine e non rivelo l'identit&agrave; di chi mi scrive.</p>

    <h3>Dati identificativi</h3>
    <p>Sito: francozanghi.it<br>
    Titolare: Domenico Franco Zanghì &mdash; Patti (Messina), Italia<br>
    Posta elettronica: <a href="mailto:%s">%s</a></p>
  </section>
""" % (POSTA, POSTA, POSTA, POSTA)
scrivi("contatti.html", pagina("Contatti — Franco Zanghì", contatti))

dati = """  <section class="testo">
    <h2>Dati personali</h2>
    <p class="sommario">Come vengono trattati i dati di chi visita questo sito.</p>

    <p><strong>Titolare del trattamento.</strong> Domenico Franco Zanghì, Patti (Messina), Italia. Posta elettronica: <a href="mailto:%s">%s</a>.</p>

    <h3>Dati raccolti durante la navigazione</h3>
    <p>Il fornitore che ospita il sito registra automaticamente alcuni dati tecnici legati alla connessione, tra cui l'indirizzo di rete del visitatore, la data e l'ora della richiesta e la pagina richiesta. Questi dati servono a far funzionare il servizio e a rilevare eventuali anomalie o abusi, e non vengono usati per identificare le persone n&eacute; incrociati con altre informazioni.</p>

    <h3>Dati forniti volontariamente</h3>
    <p>Se mi scrivi un messaggio di posta elettronica, il tuo indirizzo e il contenuto del messaggio vengono conservati per il tempo necessario a rispondere e a dare seguito alla corrispondenza. Non vengono comunicati ad altri n&eacute; usati per invii di altro genere.</p>

    <h3>Misurazione delle visite</h3>
    <p>Questo sito conta le pagine lette con GoatCounter, un contatore che non usa cookie, non salva l'indirizzo di rete del visitatore e non costruisce profili. Vengono registrati soltanto dati aggregati: la pagina vista, il giorno e l'ora, il sito di provenienza, il tipo di navigatore e di sistema, la lingua, la larghezza dello schermo e il Paese, ricavato dall'indirizzo di rete usato sul momento e non conservato. Il servizio &egrave; gestito da Martin Tournoij, con sede in Irlanda, e i dati sono conservati su server in Finlandia e in Germania. Il sito non utilizza altri strumenti di tracciamento.</p>\n    <h3>Spazi pubblicitari</h3>\n    <p>Alcune pagine ospitano un riquadro pubblicitario, dichiarato come tale, che rimanda a Torre Eoliana, un&#8217;attivit&agrave; del titolare di questo sito. &Egrave; un semplice collegamento: non carica immagini n&eacute; codice da altri servizi, non segue il visitatore e non raccoglie dati su di lui. Quello che accade dopo il clic &egrave; regolato dalle condizioni del sito di destinazione.</p>

    <h3>Video</h3>
    <p>Nella pagina dei video, e in fondo ad alcuni articoli, i video sono ospitati su YouTube. Finch&eacute; non avvii un video, la pagina non contatta YouTube e non carica nulla da quel servizio: vedi soltanto un riquadro con il titolo, scritto in questa pagina. Quando clicchi per avviare, parte il lettore di YouTube in versione senza cookie di profilazione, e da quel momento YouTube pu&ograve; registrare dati sulla tua visione, secondo le proprie condizioni. Se preferisci, il collegamento accanto a ogni video ti porta a guardarlo direttamente sul suo canale.</p>

    <h3>I tuoi diritti</h3>
    <p>Puoi chiedere in qualsiasi momento di accedere ai dati che ti riguardano, di correggerli o di cancellarli, scrivendo all'indirizzo indicato sopra.</p>

    <p><em>Questo testo va verificato e aggiornato se in futuro il sito dovesse introdurre moduli di contatto, iscrizioni, misurazione del pubblico o contenuti incorporati da altri servizi.</em></p>
  </section>
""" % (POSTA, POSTA)
scrivi("dati-personali.html", pagina("Dati personali — Franco Zanghì", dati))

# ---------------- condizioni d'uso ----------------
condizioni = """  <section class="testo">
    <h2>Condizioni d'uso</h2>
    <p class="sommario">Che cosa si pu&ograve; fare con quello che si legge qui, e di cosa risponde chi scrive.</p>

    <p>Questo sito &egrave; pubblicato da Domenico Franco Zangh&igrave;, giornalista, con sede a Patti, in provincia di Messina. Raccoglie gli articoli che firmo come Franco Zangh&igrave;. Non &egrave; un quotidiano, non ha una periodicit&agrave; dichiarata e non riceve contributi pubblici.</p>

    <h3>Pubblicit&agrave;</h3>
    <p>Alcune pagine ospitano un riquadro pubblicitario, sempre contrassegnato come tale e tenuto separato dagli articoli. Al momento rimanda a Torre Eoliana, un&#8217;attivit&agrave; di cui sono titolare, e questo &egrave; dichiarato dentro il riquadro stesso. La pubblicit&agrave; non influisce sulla scelta degli argomenti n&eacute; su quello che scrivo: nessun inserzionista, me compreso, ha voce sui contenuti.</p>

    <h3>I testi</h3>
    <p>Gli articoli sono miei e restano miei. Puoi citarli liberamente, riportando il mio nome e il collegamento alla pagina da cui hai preso la citazione. Non &egrave; consentita la riproduzione integrale di un articolo su un altro sito o in un'altra pubblicazione senza il mio consenso scritto, n&eacute; l'uso dei testi per addestrare sistemi automatici senza accordo.</p>

    <p>Le fonti indicate in fondo a ogni articolo appartengono a chi le ha pubblicate, e il collegamento rimanda sempre all'originale.</p>

    <h3>Esattezza e rettifiche</h3>
    <p>Gli articoli riportano quello che risultava verificato alla data di pubblicazione, indicata su ogni pagina. Le vicende cambiano, e un testo pu&ograve; essere superato dai fatti senza che io me ne accorga subito. Quando un articolo contiene un errore lo correggo e ne resta traccia: trovi come funziona nella <a href="rettifiche.html">pagina delle rettifiche</a>.</p>

    <h3>Collegamenti ad altri siti</h3>
    <p>Gli articoli rimandano a fonti esterne sulle quali non ho alcun controllo. Il collegamento serve a far verificare quello che scrivo e non significa che condivida il resto di quei siti.</p>

    <h3>Responsabilit&agrave;</h3>
    <p>Il sito &egrave; messo a disposizione cos&igrave; com'&egrave;. Non garantisco che sia sempre raggiungibile n&eacute; che i collegamenti esterni restino attivi nel tempo. Quello che leggi qui &egrave; informazione giornalistica e non costituisce consulenza legale, medica, fiscale o finanziaria.</p>

    <h3>Dati personali</h3>
    <p>Il trattamento dei dati di chi visita il sito &egrave; descritto nella <a href="dati-personali.html">pagina dedicata</a>.</p>

    <h3>Contatti e legge applicabile</h3>
    <p>Per segnalazioni, rettifiche e richieste scrivi all'indirizzo che trovi nella <a href="contatti.html">pagina dei contatti</a>. A queste condizioni si applica la legge italiana.</p>
  </section>
"""
scrivi("condizioni.html", pagina("Condizioni d'uso — Franco Zanghì", condizioni))

print(f"Generate {len(notizie)} notizie piu' le pagine fisse. Sito nella cartella: {USCITA}")
for n in notizie:
    print(" -", n["data"], n["sezione"], "->", n["file"])
