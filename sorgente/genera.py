# -*- coding: utf-8 -*-
"""Generatore del sito francozanghi.it — pagine statiche.

Legge le notizie da sito-sorgente/notizie.json e ricostruisce
l'intero sito: prima pagina, sezioni, pagine degli articoli e
pagine fisse. Si lancia con:  python3 genera.py
"""
import os, html, json, unicodedata

SORGENTE = "sorgente/notizie.json"
USCITA   = "."
POSTA    = "francozanghi@gmail.com"

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


def menu(attiva=""):
    cl = ' class="attiva"' if attiva == "home" else ""
    voci = [f'    <a href="index.html"{cl}>Prima pagina</a>']
    for slug, nome in SEZIONI:
        cl = ' class="attiva"' if slug == attiva else ""
        voci.append(f'    <a href="{slug}.html"{cl}>{nome}</a>')
    cl = ' class="attiva"' if attiva == "chi-sono" else ""
    voci.append(f'    <a href="chi-sono.html"{cl}>Chi sono</a>')
    return "\n".join(voci)


def pagina(titolo, corpo, attiva="", iniziale=False):
    classe = "testata" if iniziale else "testata interna"
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
<link rel="stylesheet" href="stile.css">
</head>
<body>
<div class="foglio">

  <header class="{classe}">
    <h1>{nome}</h1>
    {occhiello}
  </header>

  <nav>
{menu(attiva)}
  </nav>

{corpo}

  <footer>
    <p>
      <a href="rettifiche.html">Rettifiche</a> &nbsp;·&nbsp;
      <a href="contatti.html">Contatti</a> &nbsp;·&nbsp;
      <a href="dati-personali.html">Dati personali</a>
    </p>
    <p class="gerenza">
      francozanghi.it — Domenico Franco Zanghì, Patti (Messina) — <a href="mailto:{POSTA}">{POSTA}</a>
    </p>
  </footer>

</div>
</body>
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
scrivi("index.html", pagina("Franco Zanghì", corpo, attiva="home", iniziale=True))

# ------------------------------------------------------------------
# pagine di sezione
# ------------------------------------------------------------------
for slug, nome in SEZIONI:
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
    scrivi(f"{slug}.html", pagina(f"{nome} — Franco Zanghì", corpo, attiva=slug))

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

    <p>Nessuna correzione finora.</p>
  </section>
"""
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

    <h3>Strumenti di tracciamento</h3>
    <p>Questo sito non utilizza strumenti di tracciamento della navigazione n&eacute; sistemi di misurazione del pubblico di terze parti, e non ospita pubblicit&agrave;.</p>

    <h3>I tuoi diritti</h3>
    <p>Puoi chiedere in qualsiasi momento di accedere ai dati che ti riguardano, di correggerli o di cancellarli, scrivendo all'indirizzo indicato sopra.</p>

    <p><em>Questo testo va verificato e aggiornato se in futuro il sito dovesse introdurre moduli di contatto, iscrizioni, misurazione del pubblico o contenuti incorporati da altri servizi.</em></p>
  </section>
""" % (POSTA, POSTA)
scrivi("dati-personali.html", pagina("Dati personali — Franco Zanghì", dati))

print(f"Generate {len(notizie)} notizie piu' le pagine fisse. Sito nella cartella: {USCITA}")
for n in notizie:
    print(" -", n["data"], n["sezione"], "->", n["file"])
