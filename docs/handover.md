# Übergabe und Provenienz

## Tatsächlich verfügbar, 2026-10-13

Der Nutzerauftrag nennt 61 Gruppen (A31/B30), Dossiers 13–20, den Checkpoint
`PHAISTOS_checkpoint_2026-10-13.zip` sowie `phaistos_d21_digitization_template.csv`,
`phaistos_d21_geometry.py`, `phaistos_d21_protocol.md`.
**Keine dieser Dateien wurde bisher gelesen oder importiert.**

Im aktuellen Arbeitsordner und durch Dateinamensuche unter Documents/Codex
wurden keine passenden Dateien gefunden. Eine ergänzende Prüfung der direkten
Dateien unter Downloads und Documents lieferte ebenfalls keinen Treffer.
Das ist keine vollständige Suche des Computers.

Der referenzierte Chat `6acdf121-46e4-83eb-9a36-f6faf6f84a1b` lieferte beim
Abruf nur Inhaltsverweis-Platzhalter, keine lesbaren Dossiers und keine Anhänge.
MUNIN wurde anfangs unter `PHAISTOS` geprüft und lieferte keinen Treffer.
Auf Nutzerkorrektur wird MUNIN für dieses neue Projekt nicht weiter verwendet.

## Forschungsstand laut Nutzerauftrag, nicht neu verifiziert

- Dossier 17 enthält eine fehlerhafte Markierungszuordnung.
- Die korrigierten Dossiers 18–20 sollen D17 als aktive Grundlage ersetzen.
- Der Markierungszusammenhang ist unter Kontrolle für Endzeichen und Länge
  nicht robust; strenges Modell p≈0,332, stark fragmentierte Strata.
- Keine Koordinaten, Signifikanzen oder Entzifferung ergänzen bzw. behaupten.

Diese Aussagen sind ein übernommener Forschungscheckpoint, keine hier
reproduzierten Ergebnisse. D17 ist als überholt zu archivieren, sobald die
Dateien vorliegen. Die korrigierten Daten müssen mit Herkunft und Skripten
importiert und ihre Ergebnisse reproduziert werden. Bis dahin bleibt jede
Markierungsanalyse gesperrt; es gibt keine erfundenen Ersatzdaten.

## Offene Schritte

1. Die vier genannten Dateien bzw. das vollständige Checkpoint-Paket erhalten.
2. Hash-Inventar und Dossier-zu-Datei-Zuordnung erstellen; Originale bewahren.
3. CSV-Schema und Geometriedefinition des echten D21 prüfen, dann dokumentiert
   migrieren. Die aktuelle Implementierung muss nötigenfalls angepasst werden.
4. A01–A31/B01–B30 mit Originalnummerierung und Transkription abgleichen.
5. Beide Fotos visuell auf Vollständigkeit, Reflexionen und Verzerrung prüfen.
6. 61 Zentren erfassen, Unsicherheit begründen, unabhängig sichten und freigeben.
7. Öffentliches Remote `fjoelnr/phaistos` mit dem geprüften Ausgangsstand befüllen.

Die 61 Zeilen in `groups.csv` sind leere Erfassungsplätze, kein importierter
Forschungsdatensatz. Es wird keine Kompatibilität mit dem fehlenden D21-CSV
behauptet. Alle Implementierungsentscheidungen sind im neuen Protokoll erklärt.
