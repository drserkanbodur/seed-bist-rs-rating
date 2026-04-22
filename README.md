# BIST RS Rating & Market Condition — TradingView Seed

BIST hisseleri için IBD tarzı RS Rating ve Market Condition Detector verisi.
TradingView `request.seed()` ile Pine Script'lerden okunur.

## Nasıl Çalışır

1. GitHub Actions her iş günü saat 19:00'da (borsa kapanışı sonrası) çalışır
2. ~500 BIST hissesinin fiyat verilerini Yahoo Finance'den çeker
3. RS Rating percentile eşiklerini ve HIGQ/LOWQ breadth verilerini hesaplar
4. `data/` klasörüne seed formatında yazar
5. TradingView Pine Script'leri `request.seed()` ile bu veriyi okur

## Seed Dosyaları

| Dosya | İçerik |
|-------|--------|
| `data/RSRATING.csv` | 7 RS percentile eşik değeri (p98, p89, p69, p49, p29, p9, p1) |
| `data/MCD.csv` | 9 breadth değeri (HIGQ/LOWQ/Net × 3 katman) |
| `data/rs_full.csv` | Tüm hisseler detaylı (Google Sheets için) |

## Pine Script Kullanımı

```pine
// RS Rating
rsData = request.seed('seed_drserkanbodur_bist', 'RSRATING', close)

// Market Condition
mcdData = request.seed('seed_drserkanbodur_bist', 'MCD', close)
```

## Referans

- Fred6724 / Skyte: https://github.com/Fred6725/relative-strength
- William O'Neil — IBD RS Rating
- Chilly Charts & Plots — BIST uyarlama + 3 katmanlı MCD breadth
