"""
BIST RS Rating & Market Condition Detector
==========================================
TradingView request.seed() için veri üretir.
GitHub Actions ile her iş günü otomatik çalışır.

Çıktılar:
  data/RSRATING.csv  → RS percentile eşik değerleri (seed format)
  data/MCD.csv       → HIGQ/LOWQ breadth değerleri (seed format)
  data/rs_full.csv   → Tüm hisseler detaylı (Google Sheets için)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

REFERENCE_INDEX = "XU100.IS"
DATA_DIR = "data"

BIST_CODES = [
    "ACIPD","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON","AGESA","AGHOL","AGROT",
    "AGYO","AHGAZ","AHSGY","AKBNK","AKCNS","AKFGY","AKFYE","AKGRT","AKMGY","AKSA",
    "AKSGY","AKSEN","AKSUE","AKYHO","ALARK","ALBRK","ALCAR","ALCTL","ALFAS","ALGYO",
    "ALKIM","ALTIN","ALTNY","ANACM","ANELE","ANHYT","ANSEN","ANSGR","ARASE","ARCLK",
    "ARDYZ","ARENA","ARFYO","ARMDA","ARSAN","ARZUM","ASELS","ASGYO","ASUZU","ATAGY",
    "ATATP","ATAKP","ATLAS","AVGYO","AVHOL","AVOD","AVPGY","AVTUR","AYCES","AYDEM",
    "AYEN","BAGFS","BAKAB","BALAT","BANVT","BARMA","BASCM","BASGZ","BAYRK","BERA",
    "BEYAZ","BFREN","BIENY","BIGCH","BIMAS","BINHO","BIOEN","BJKAS","BKNMA","BLCYT",
    "BMELK","BMSCH","BMSTL","BNTAS","BOBET","BORLS","BOSSA","BRISA","BRKO","BRLSM",
    "BRMEN","BRSAN","BRYAT","BSOKE","BTCIM","BUCIM","BURCE","BURVA","BYDNR","CANTE",
    "CASA","CATES","CCOLA","CELHA","CEMAS","CEMTS","CEOEM","CGCAM","CIMSA","CLEBI",
    "CMBTN","CMENT","CONSE","COSMO","CRFSA","CRDFA","CUSAN","CVKMD","CWENE","DAGHL",
    "DAGI","DAPGM","DARDL","DENGE","DERHL","DERIM","DESA","DESPC","DEVA","DGATE",
    "DGGYO","DGNMO","DIRIT","DITAS","DMSAS","DNISI","DOAS","DOBUR","DOGUB","DOHOL",
    "DOKTA","DURDO","DYOBY","DZGYO","EBEBK","ECILC","ECZYT","EDATA","EDIP","EGCEY",
    "EGCYH","EGEEN","EGEPO","EGGUB","EGPRO","EGSER","EKGYO","EKIZ","EKOS","EKSUN",
    "ELITE","EMKEL","EMNIS","ENDST","ENERY","ENJSA","ENKAI","ENSRI","EPLAS","EPCGY",
    "ERBOS","EREGL","ERGLI","ERSU","ESAVE","ESCAR","ESCOM","ESEN","ETILR","EUIMG",
    "EUPWR","EUREN","EUYO","EYGYO","FADE","FENER","FLAP","FMIZP","FONET","FORMT",
    "FORTE","FRIGO","FROTO","FZLGY","GARAN","GARFA","GEDIK","GEDZA","GENIL","GENTS",
    "GEREL","GESAN","GLCVY","GLYHO","GLRYH","GMTAS","GOKNR","GOLTS","GORBN","GOZDE",
    "GRNYO","GRSEL","GRTRK","GSDDE","GSDHO","GSRAY","GUBRF","GWIND","GZNMI","HALKB",
    "HATEK","HATSN","HDFGS","HEDEF","HEKTS","HTTBT","HUBVC","HUNER","HURGZ","ICBCT",
    "ICUGS","IDEAS","IDGYO","IEYHO","IHEVA","IHGZT","IHLAS","IHLGM","IHYAY","IMASM",
    "INDES","INFO","INGRM","INTEM","INVEO","INVES","IPEKE","ISATR","ISCTR","ISDMR",
    "ISFIN","ISGYO","ISKPL","ISKUR","ISMEN","ISSEN","IZENR","IZFAS","IZINV","IZMDC",
    "JANTS","KAPLM","KAREL","KARSN","KARTN","KARYE","KATMR","KAYSE","KBORU","KCAER",
    "KCHOL","KENT","KERVN","KERVT","KFEIN","KGYO","KIMMR","KLGYO","KLMSN","KLNMA",
    "KLRHO","KLSER","KLSYN","KMPUR","KNFRT","KONTR","KONYA","KOPOL","KORDS","KOZAA",
    "KOZAL","KRDMD","KRGYO","KRONT","KRPLS","KRSTL","KRTEK","KRVGD","KTLEV","KUTPO",
    "KUYAS","KUVYT","LIDER","LIDFA","LILAK","LINK","LKMNH","LMKDC","LOGO","LRSHO",
    "LUKSK","MAALT","MACKO","MAGEN","MAKIM","MAKTK","MANAS","MARBL","MARKA","MARTI",
    "MASSY","MAVI","MEDTR","MEGAP","MEGMT","MEKAG","MEPET","MERCN","MERIT","MERKO",
    "METRO","METUR","MGROS","MIATK","MIPAZ","MMCAS","MOBTL","MOGAN","MPARK","MRSHL",
    "MSGYO","MTRKS","MTRYO","MZHLD","NATEN","NETAS","NIBAS","NRBNK","NTGAZ","NUGYO",
    "NUHCM","NUROL","OBAMS","OBASE","ODAS","OFSYM","ONCSM","ORGE","ORMA","OSMEN",
    "OSTIM","OTKAR","OTTO","OYAKC","OYLUM","OYYAT","OZBAL","OZGYO","OZKGY","OZRDN",
    "OZSUB","OZTK","PAGYO","PAMEL","PAPIL","PARSN","PCILT","PEGYO","PENGD","PENTA",
    "PETKM","PETUN","PGSUS","PINSU","PKART","PKENT","PLTUR","POLHO","POLTK","PRDGS",
    "PRKAB","PRKME","PRZMA","PSDTC","QNBFB","QNBFL","QUAGR","RALYH","RAYSG","REEDR",
    "RGYAS","RODRG","ROYAL","RUBNS","RYGYO","RYSAS","SAFKR","SAHOL","SAMAT","SANEL",
    "SANFM","SANKO","SARKY","SASA","SAYAS","SDTTR","SEGYO","SEKFK","SELEC","SELGD",
    "SELVA","SEYKM","SILVR","SISE","SKBNK","SKTAS","SMART","SMRTG","SNGYO","SNKRN",
    "SNPAM","SODSN","SOKM","SONME","SRVGY","SUNTK","SURGY","SUWEN","SYRGY","TABGD",
    "TATGD","TATEN","TAVHL","TBORG","TCELL","TDGYO","TEKTU","TERA","TETMT","TGSAS",
    "THYAO","TKFEN","TLMAN","TMSN","TMPOL","TNZTP","TOASO","TRCAS","TRGYO","TRILC",
    "TSGYO","TSKB","TTKOM","TTRAK","TUCLK","TUKAS","TUPRS","TUREX","TURGG","TURSG",
    "UFUK","ULAS","ULKER","ULUFA","ULUUN","UNLU","USAK","UZERB","VAKBN","VAKFN",
    "VAKKO","VANGD","VBTYZ","VERTU","VERUS","VESBE","VESTL","VKFYO","VKGYO","VRGYO",
    "YATAS","YAYLA","YESIL","YEOTK","YGYO","YKSLN","YUNSA","YYLGD","ZEDUR","ZOREN",
    "ZRGYO",
]


def fetch_all_data():
    """Tüm BIST verilerini çek"""
    tickers = list(set([t + ".IS" for t in BIST_CODES]))
    end = datetime.now()
    start = end - timedelta(days=400)

    print(f"📥 Referans: {REFERENCE_INDEX}")
    ref = yf.download(REFERENCE_INDEX, start=start, end=end, progress=False)
    if ref.empty:
        print("❌ XU100 verisi alınamadı!")
        return None, None

    if isinstance(ref.columns, pd.MultiIndex):
        ref_c = ref[('Close', REFERENCE_INDEX)].dropna()
    else:
        ref_c = ref['Close'].dropna()

    print(f"📥 {len(tickers)} hisse çekiliyor...")
    all_data = {}
    batch_size = 50

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            data = yf.download(" ".join(batch), start=start, end=end,
                             progress=False, group_by='ticker', threads=True)
            for t in batch:
                try:
                    td = data[t] if len(batch) > 1 else data
                    if not td.empty and len(td) > 63:
                        all_data[t] = td
                except:
                    pass
        except:
            pass
        done = min(i + batch_size, len(tickers))
        print(f"   [{done}/{len(tickers)}]", end='\r')
        if i + batch_size < len(tickers):
            time.sleep(1)

    print(f"\n   ✅ {len(all_data)} hisse")
    return all_data, ref_c


def calc_rs_and_breadth(all_data, ref_c):
    """RS skorları ve 52H breadth hesapla"""
    results = []

    for ticker, data in all_data.items():
        try:
            if isinstance(data.columns, pd.MultiIndex):
                closes = data[('Close', ticker)].dropna()
                highs = data[('High', ticker)].dropna()
                lows = data[('Low', ticker)].dropna()
            else:
                closes = data['Close'].dropna()
                highs = data['High'].dropna()
                lows = data['Low'].dropna()

            if len(closes) < 63:
                continue

            n = len(closes)
            nr = len(ref_c)

            # RS Score
            rs_stock = (0.4 * float(closes.iloc[-1]) / float(closes.iloc[-1-min(63,n-1)]) +
                       0.2 * float(closes.iloc[-1]) / float(closes.iloc[-1-min(126,n-1)]) +
                       0.2 * float(closes.iloc[-1]) / float(closes.iloc[-1-min(189,n-1)]) +
                       0.2 * float(closes.iloc[-1]) / float(closes.iloc[-1-min(252,n-1)]))

            rs_ref = (0.4 * float(ref_c.iloc[-1]) / float(ref_c.iloc[-1-min(63,nr-1)]) +
                     0.2 * float(ref_c.iloc[-1]) / float(ref_c.iloc[-1-min(126,nr-1)]) +
                     0.2 * float(ref_c.iloc[-1]) / float(ref_c.iloc[-1-min(189,nr-1)]) +
                     0.2 * float(ref_c.iloc[-1]) / float(ref_c.iloc[-1-min(252,nr-1)]))

            if rs_ref == 0:
                continue

            rs_score = (rs_stock / rs_ref) * 100
            last = float(closes.iloc[-1])

            # 52H
            h52 = float(highs.tail(252).max()) if len(highs) >= 252 else float(highs.max())
            l52 = float(lows.tail(252).min()) if len(lows) >= 252 else float(lows.min())
            pct_from_high = (h52 - last) / h52 * 100 if h52 > 0 else 999
            pct_from_low = (last - l52) / l52 * 100 if l52 > 0 else 999

            results.append({
                'Ticker': ticker.replace('.IS', ''),
                'RSScore': round(rs_score, 2),
                'Fiyat': round(last, 2),
                'ZirvedenUzaklik': round(pct_from_high, 2),
                'DiptenYukselis': round(pct_from_low, 2),
                'High52W': round(h52, 2),
                'Low52W': round(l52, 2),
            })
        except:
            continue

    return pd.DataFrame(results)


def generate_rs_seed(df):
    """
    RS Rating seed formatı — Fred6724 ile aynı mantık
    7 percentile eşik değeri: 98, 89, 69, 49, 29, 9, 1
    5 kez tekrarlanır (hafta sonu güvenliği)
    """
    percentiles = [98, 89, 69, 49, 29, 9, 1]
    thresholds = []

    for p in percentiles:
        idx = int(len(df) * (100 - p) / 100)
        idx = min(idx, len(df) - 1)
        thresholds.append(round(float(df.iloc[idx]['RSScore']), 2))

    # Seed CSV: date, close formatında — 5 kez tekrar
    today = datetime.now().strftime('%Y-%m-%d')
    rows = []
    for _ in range(5):
        for val in thresholds:
            rows.append({'date': today, 'close': val})

    return pd.DataFrame(rows), thresholds


def generate_mcd_seed(df):
    """
    MCD seed formatı — HIGQ/LOWQ/Net 3 katman
    9 değer: HIGQ1,LOWQ1,NET1, HIGQ5,LOWQ5,NET5, HIGQ25,LOWQ25,NET25
    5 kez tekrarlanır
    """
    higq1 = len(df[df['ZirvedenUzaklik'] <= 1])
    lowq1 = len(df[df['DiptenYukselis'] <= 1])
    net1 = higq1 - lowq1

    higq5 = len(df[df['ZirvedenUzaklik'] <= 5])
    lowq5 = len(df[df['DiptenYukselis'] <= 5])
    net5 = higq5 - lowq5

    higq25 = len(df[df['ZirvedenUzaklik'] <= 25])
    lowq25 = len(df[df['DiptenYukselis'] <= 25])
    net25 = higq25 - lowq25

    values = [higq1, lowq1, net1, higq5, lowq5, net5, higq25, lowq25, net25]

    today = datetime.now().strftime('%Y-%m-%d')
    rows = []
    for _ in range(5):
        for val in values:
            rows.append({'date': today, 'close': float(val)})

    return pd.DataFrame(rows), {
        'HIGQ_1': higq1, 'LOWQ_1': lowq1, 'Net_1': net1,
        'HIGQ_5': higq5, 'LOWQ_5': lowq5, 'Net_5': net5,
        'HIGQ_25': higq25, 'LOWQ_25': lowq25, 'Net_25': net25,
    }


def main():
    print("=" * 60)
    print("  BIST Seed Generator — RS Rating & MCD")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    os.makedirs(DATA_DIR, exist_ok=True)

    # Veri çek
    all_data, ref_c = fetch_all_data()
    if ref_c is None:
        return

    # RS + Breadth hesapla
    print(f"\n📊 Hesaplanıyor...")
    df = calc_rs_and_breadth(all_data, ref_c)

    if len(df) == 0:
        print("❌ Sonuç yok!")
        return

    # RS Rating percentile
    df = df.sort_values('RSScore', ascending=False).reset_index(drop=True)
    n = len(df)
    df['RSRating'] = [max(1, min(99, int(((n - i) / n) * 100))) for i in range(n)]
    df['Sira'] = range(1, n + 1)

    # ═══ SEED DOSYALARI ═══

    # 1. RS Rating Seed
    rs_seed, rs_thresholds = generate_rs_seed(df)
    rs_seed.to_csv(os.path.join(DATA_DIR, 'RSRATING.csv'), index=False)
    print(f"✅ RSRATING.csv — eşikler: {rs_thresholds}")

    # 2. MCD Seed
    mcd_seed, mcd_values = generate_mcd_seed(df)
    mcd_seed.to_csv(os.path.join(DATA_DIR, 'MCD.csv'), index=False)
    print(f"✅ MCD.csv — {mcd_values}")

    # 3. Full RS list (Google Sheets için)
    df['Tarih'] = datetime.now().strftime('%Y-%m-%d')
    full_cols = ['Sira', 'Ticker', 'RSRating', 'RSScore', 'Fiyat',
                 'High52W', 'Low52W', 'ZirvedenUzaklik', 'DiptenYukselis', 'Tarih']
    df[full_cols].to_csv(os.path.join(DATA_DIR, 'rs_full.csv'), index=False)
    print(f"✅ rs_full.csv — {len(df)} hisse")

    # Özet
    print(f"\n{'='*60}")
    print(f"  RS Rating: {len(df)} hisse")
    print(f"  RS ≥ 90: {len(df[df['RSRating'] >= 90])}")
    print(f"  RS ≥ 80: {len(df[df['RSRating'] >= 80])}")
    print(f"  MCD Net (Geniş %5): {mcd_values['Net_5']:+d}")
    print(f"{'='*60}")

    print(f"\n  TOP 10:")
    for _, r in df.head(10).iterrows():
        print(f"  {r['Sira']:<4}{r['Ticker']:<10}{r['RSRating']:<4}{r['RSScore']:<8.1f}")

    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
