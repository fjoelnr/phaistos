# Vorläufiges Digitalisierungsprotokoll, Version 0.1

Dieses neu erstellte Protokoll wird mit dem noch fehlenden D21-Original
abgeglichen. Vor diesem Abgleich keine Forschungsfreigabe.

## Definition und Leserichtung

Eine Gruppe ist das Feld zwischen eingeritzten Trennern innerhalb der Spirale.
Als operationales Zentrum wird der visuell geschätzte Mittelpunkt der von den
Zeichen dieser Gruppe belegten Fläche erfasst. Es ist weder der Schwerpunkt
der gesamten Tontafel noch automatisch der Mittelpunkt eines Trennfelds.
Alternativdefinitionen müssen als eigene Messreihe behandelt werden.

Die Reihenfolge A01–A31/B01–B30 ist derzeit nur ein Platzhalter. Die Zuordnung
muss anhand der D18–21-Quellen überprüft werden; die konkrete Referenz kommt
in `mapping_reference`. Außen→innen ist die dokumentierte Museumskonvention.
Die CSV-Reihenfolge impliziert keine sprachliche Lesart oder Übersetzung.

## Koordinaten

Unveränderte heruntergeladene JPEG-Datei, keine Rotation, Spiegelung,
Perspektivkorrektur oder automatische EXIF-Transposition. Ursprung links oben;
x nach rechts, y nach unten. Pixelzentren: 0≤x≤Breite−1, 0≤y≤Höhe−1.
Dezimalwerte sind zulässig. Normalisierung x/(Breite−1), y/(Höhe−1).
EXIF-Orientierung ungleich 1 wird abgewiesen, bis eine explizite Transformation
dokumentiert ist. Keine implizite Annahme eines Diskuszentrums oder Radius.

## Erfassung

Der Operator wählt jede Gruppe ausdrücklich in der Liste. Ein Linksklick setzt
das Zentrum. Ein Rechtsklick setzt den Abstand zum Zentrum als heuristischen
Unsicherheitsradius in Originalpixeln. Zoom wahlweise auf 100 %, Scrollbalken
erlauben Inspektion. Pflichtnotiz: Ursache und Begründung der Unsicherheit,
z. B. undeutlicher Rand, Reflexion, konkurrierende Zentrumslagen.
Ohne begründbaren Mittelpunkt bleibt die Zeile `missing` und x/y leer.
Keine Zwischenwerte interpolieren und keine ideale Spirale einpassen.

Speichern bindet die Annotation an Bildhash, Maße, Operator, UTC-Zeit,
Zuordnungsreferenz und Status `draft`. Überarbeitungen löschen alte Prüfvermerke.
Git-Commit nach jeder abgeschlossenen Sitzung; Änderungen nachvollziehen.

## Sichtprüfung

Eine zweite Person prüft das Original und den erzeugten Overlay bei 100 %:
Seite/Gruppe korrekt, Mittelpunkt plausibel, Radius ausreichend begründet,
Quelle und Nummerierung belegt. Reine formale Validierung prüft keine dieser
inhaltlichen Aussagen. `review` verlangt einen anderen Namen und eine Notiz;
dies ist eine dokumentierte Erklärung, keine technische Identitätsprüfung.
Unklare Zuordnungen bleiben Entwurf und verhindern die Freigabe.

## Qualitätsstatus und Auswertung

`missing`: keine Messung; `draft`: erfasst, nicht unabhängig bestätigt;
`reviewed`: unabhängige Sichtprüfung erklärt. Vollständige Freigabe erfordert
genau 61 eindeutige Gruppen und 61 geprüfte Messungen an den gebundenen Bildern.
Der Hash jeder CSV und jedes Bilds wird in den Validierungsbericht geschrieben.
Nach Erhalt der Dossiers zusätzlich ihre Hashes in einem Importinventar sichern.

Der Overlay zeigt fehlende Anzahl, Gruppen-IDs, Mittelpunkt und Radius;
orange = Entwurf, grün = geprüft. Leere Zeilen erscheinen nicht als Punkte.
Keine automatische Bedeutung aus geometrischen Mustern ableiten. Für spätere
Tests vorab Hypothesen, Nullmodell, Seed, Zahl der Permutationen, Kontrollen und
Korrektur multipler Tests festlegen. Aktuell wird keine Signifikanz berechnet.
