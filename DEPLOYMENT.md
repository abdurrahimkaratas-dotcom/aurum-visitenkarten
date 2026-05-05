# Online stellen + QR-Codes

Drei einfache Wege, das Verzeichnis ins Netz zu bringen. Empfehlung: **Netlify Drop** — ohne Account, drag&drop, eine Minute fertig.

## Option 1 · Netlify Drop (empfohlen, schnellster Weg)

1. https://app.netlify.com/drop öffnen
2. Den Ordner `Digitale Visitenkarte` (komplett, mit `index.html`, `images/`, `*.html`, `*.css`, `*.vcf`) per Drag&Drop in das Browserfenster ziehen
3. Du bekommst sofort eine URL wie `https://aurum-visitenkarten-xyz.netlify.app`
4. Im Netlify-Dashboard kannst du die URL umbenennen (z.B. `aurum-cards.netlify.app`) oder eine eigene Domain (`visitenkarten.aurum-fassadenreinigung.de`) hinzufügen
5. **Wichtig:** kein Account-Zwang für Drop, aber für Umbenennen/Domain Account erstellen (kostenlos)

## Option 2 · GitHub Pages

1. Auf github.com einen Repo `aurum-visitenkarten` anlegen (public)
2. Den ganzen Ordnerinhalt hochladen (Web-UI: "Add file" → "Upload files")
3. Settings → Pages → Source: `main` Branch, Folder `/ (root)` → Save
4. Nach ~1 Minute ist die Seite unter `https://<benutzer>.github.io/aurum-visitenkarten/` erreichbar

## Option 3 · Cloudflare Pages

1. https://dash.cloudflare.com/?to=/:account/pages → "Create application" → "Direct Upload"
2. Ordner hochladen → Projekt benennen → Deploy
3. URL: `https://aurum-visitenkarten.pages.dev`

---

## QR-Codes erzeugen

Sobald du eine URL hast (egal welcher Anbieter), QR-Codes generieren:

```bash
pip install qrcode[pil]
python generate_qr.py https://aurum-visitenkarten.netlify.app
```

Die fertigen PNGs landen im Ordner `qr/`:

- `qr-uebersicht.png` → Übersichtsseite (alle Visitenkarten)
- `qr-khafi.png` → Visitenkarte Mustafa Khafi
- `qr-julia.png` → Visitenkarte Julia Schneider
- `qr-cornelia.png` → Visitenkarte Cornelia Jöge

Jeder QR-Code hat das Aurum-Logo in der Mitte und einen kleinen Beschriftungs-Footer.
Druckbar in jeder Größe — die Auflösung ist groß genug für A4.

## Test mit dem Handy

1. Handy-Kamera öffnen
2. Auf den QR-Code halten
3. Auf den Banner tippen → die Visitenkarte öffnet sich direkt im Browser
4. Auf "Kontakt speichern" tippen → Kontakt landet im Adressbuch (vCard)

## Eigene Domain

Wenn ihr eine Subdomain wollt (z.B. `karten.aurum-fassadenreinigung.de`):

- Bei Netlify/Cloudflare: Custom Domain hinzufügen, dann beim Domain-Anbieter einen CNAME setzen, der auf die Plattform zeigt.
- Nach DNS-Propagation (5–30 Min) ist die Subdomain aktiv. SSL läuft automatisch.

Dann nochmal `python generate_qr.py https://karten.aurum-fassadenreinigung.de` ausführen, damit die QRs auf die schöne Domain zeigen.
