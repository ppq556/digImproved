# Skrypt do wygodniejszego przeglądania Wykopu by ppq556

## Motywacja
- usunięcie reklam, znalezisk sponsorowanych oraz toksycznych stron pseudoinformacyjnych (np. rmf.fm)

## Instrukcja

### Wersja z dockerem

#### Wymagania
- [Docker](https://docs.docker.com/install/)

#### Użycie
```shell script
docker build . -t digImproved           # tylko za pierwszym razem
docker run digImproved > wykop.html
```

### Wersja standalone

#### Wymagania
- python3 (apt install python3)
- python3-httplib2 (apt install python3-httplib2)

#### Użycie
```shell script
python3 digImproved.py > wykop.html
firefox wykop.html
```
