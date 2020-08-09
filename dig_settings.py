#!/usr/bin/python3
# This Python file uses the following encoding: utf-8

# ilość stron do pobrania z Wykopu (domyślnie 2)
dig_numPages = 2

# cechy/treść znalezisk natrętnych/powtarzalnych (regexp)
blacklisted_leads = "^(.*korona.*wirus.*|.*lgbt.*|.*margot.*)$"
blacklisted_text = "^(.*korona.*wirus.*|.*lgbt.*|.*homoseks.*|.*margot.*)$"
blacklisted_sites = "^(rmf24.pl|tvp.info|regiony.tvp.pl)$"
blacklisted_tags = "^(koronawirus|covid19|.*corona.*|.*korona.*wirus|lgbt|bekazlewactwa)$"
blacklisted_authors = "^(Wykop Poleca)$"
