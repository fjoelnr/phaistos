# PHAISTOS — Dossier 21: reproduzierbare Bilddigitalisierung

Stand: 2026-10-13. Implementierungsbeginn; **0/61 Gruppenzentren erfasst**.
Keine Entzifferung, keine neu berechneten Signifikanzen.

Die Originale des Checkpoints und der Dossiers liegen noch nicht vor. Diese
Implementierung ist ein neuer, ausdrücklich vorläufiger Arbeitsstand und kein
rekonstruiertes Original von Dossier 21. Siehe [Übergabe](docs/handover.md).

## Start

Python 3.11 oder neuer, Pillow aus `requirements.txt`; für die interaktive
Erfassung zusätzlich eine Python-Installation mit Tkinter.

```console
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m phaistos fetch
python -m phaistos validate
python -m phaistos annotate --side A --operator NAME --mapping-reference REFERENZ
python -m phaistos annotate --side B --operator NAME --mapping-reference REFERENZ
python -m phaistos overlay --side A
python -m phaistos overlay --side B
python -m phaistos validate --release
```

Alle Befehle im Repository-Hauptordner ausführen. `validate` akzeptiert leere
Vorlagen als unvollständigen Arbeitsstand. `--release` bricht bei fehlenden
Punkten oder unabhängiger Sichtprüfung ab. Synthetische Testkoordinaten sind
ausschließlich in `tests/` erzeugt und gelangen nie in Forschungsdaten.

Die Erfassung beginnt erst nach Abgleich der Gruppennummerierung mit den
gelieferten Dossiers. `mapping-reference` muss eine konkrete überprüfbare
Zuordnungsquelle nennen; es ist kein automatischer Beleg ihrer Richtigkeit.

## Arbeitsablauf

1. Checkpoint und D21-Originale unverändert unter `data/incoming/` ablegen;
   Prüfsummen und Herkunft dokumentieren, sicher außerhalb des Repos entpacken
   und Inhalte prüfen. Die Dateien werden nicht automatisch veröffentlicht.
2. `fetch` lädt die beiden separat dokumentierten Commons-Aufnahmen und prüft
   Pixelmaße sowie SHA-256. Die Bilddateien bleiben außerhalb der Git-Historie.
3. Für jede Gruppe das Zentrum gemäß [Protokoll](docs/protocol.md) anklicken;
   danach einen Unsicherheitsradius setzen und begründen. Entwürfe werden
   atomar gespeichert. Quellenhash, Operator und Zeitpunkt werden gebunden.
4. Overlays in Originalauflösung prüfen. Eine andere Person prüft jede Gruppe
   einschließlich Nummerierung, Unsicherheit und Quellenbindung. Erst danach:

```console
python -m phaistos review --group A01 --reviewer ANDERE_PERSON --note "Geprüft an ..."
```

5. `validate --release` prüft Vollständigkeit und formale Freigabekriterien.
   Es ersetzt keine wissenschaftliche Sichtprüfung. Änderungen an einem Punkt
   setzen seine Freigabe zurück. Git-Diffs und Commits sichern die Historie.

Die zusätzliche Freigabesperre in `data/project_state.json` darf erst nach
geprüftem Originalimport und belegtem Nummerierungsabgleich aufgehoben werden.

## Daten und Forschung

- `data/groups.csv`: 31 A- und 30 B-Platzhalter; Gruppennummerierung provisorisch.
- `data/sources.json`: URLs, Seitennachweise, Lizenz, Bildmaße und Prüfsummen.
- `docs/sources.md`: Quellenprüfung und Grenzen der Fotografien.
- `docs/protocol.md`: Koordinaten, Leserichtung, Unsicherheit und Sichtprüfung.
- `docs/handover.md`: fehlende Originale und verbindliche Korrekturen D18–20.

Die Angabe p≈0,332 ist allein aus dem Nutzerauftrag übernommen und noch nicht
an den Originalskripten verifiziert. Dossier 17 darf keine aktive Grundlage
der Markierungszuordnung sein. Endzeichen und Länge bleiben zu kontrollieren;
fragmentierte Strata begrenzen die Aussagekraft. Dieses Paket enthält bewusst
keinen aktiven Markierungsdatensatz und kein Signifikanzmodell.

Öffentliches Repository: [fjoelnr/phaistos](https://github.com/fjoelnr/phaistos).
Code und
Dokumente haben noch keine gewählte Projektlizenz; Bildrechte siehe Quellen.
