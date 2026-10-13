# Prüfung des Ausgangsstands

Am 2026-10-13 liefen 13 automatisierte Tests erfolgreich mit Python 3.11+
und Pillow 12.3.0. Die Tests verwenden ausschließlich synthetische Daten in
temporären Verzeichnissen; diese gehören nicht zum Forschungsdatensatz.

Geprüft wurden Pixelgrenzen, Normalisierung und y-Richtung, unzulässige und
nichtendliche Koordinaten, degenerierte Bildmaße, vollständiges Gruppeninventar,
Duplikate, falsche Seiten, Quellenhash und Maße, positive Unsicherheitsradien,
Pflichtbegründungen und UTC-Zeitstempel, unabhängige Prüfvermerke und deren
Rücksetzung bei Änderungen, CSV-Rundlauf mit mehrzeiligen Notizen,
EXIF-Orientierung und synthetische Overlay-Pixel.

Zusätzlich wurden beide tatsächlich heruntergeladenen Fotografien mit
Bildmaßen und SHA-256 geprüft, beide leeren Overlays erzeugt und die
Arbeitsvorlage validiert. Die Forschungsfreigabe wurde erwartungsgemäß
abgewiesen: 61 Messungen sowie Originalimport/Nummerierungsabgleich fehlen.
Ein End-to-End-Test der interaktiven Bedienung und die Sichtprüfung einzelner
Gruppen stehen noch aus.

## Wiederholung unter Windows

```powershell
python -m unittest discover -s tests -v
python -m phaistos fetch
python -m phaistos validate
python -m phaistos validate --release
```

Der letzte Befehl muss beim aktuellen Ausgangsstand mit Exitcode 1 enden.
Falls die Umgebung das systemweite temporäre Verzeichnis sperrt, `TEMP` und
`TMP` für den Testprozess auf ein beschreibbares Arbeitsverzeichnis setzen.
Das ist eine Umgebungsanpassung; keine Tests werden dadurch übersprungen.
