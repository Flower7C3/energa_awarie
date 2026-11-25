# Propozycja PR do chauek/energa_awarie

## Podsumowanie

- Dwa byty na wpis: `binary_sensor` (bieżąca awaria typ 1) + `sensor` (dni do planu).
- `DataUpdateCoordinator`, wspólny fetch planowanych i mapy bieżących (`outages.py`).
- Poprawki config flow: reconfigure, lista powiatów, gminy/miasta z API, `unique_id` przy rekonfiguracji.
- Blueprinty powiadomień w katalogu integracji.

## Breaking change

Stary pojedynczy sensor znika na rzecz dwóch encji (`translation_key`: `active_outage`, `planned_outage`). Po aktualizacji: przeładuj integrację, usuń sieroty w rejestrze encji, zaktualizuj automaty/dashboardy.

## Test plan (dla reviewera)

1. Dodaj wpis: powiat grodzki (np. Gdynia 2262) + gmina z listy.
2. Sprawdź encje w jednym urządzeniu.
3. Rekonfiguracja z dodaniem miasta — **jeden** wpis integracji (nie duplikat).
4. Import blueprintu awarii i test `persistent_notification` (symulacja stanu lub realny feed).
5. Opcjonalnie kalendarz — wydarzenie dla planu.

## Wersja

`manifest.json` → `1.2.0`