import pulp
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

# ---------------------------------------------------------
# 1. PARAMETRELER VE VERİ SETİ (Tez Bölüm 3.2 ile Uyumlu)
# ---------------------------------------------------------
kaynaklar = ["Istanbul", "Kocaeli", "Bursa", "Izmir", "Ankara", "Eskisehir"]
tesisler = ["F1_Istanbul", "F2_Kocaeli", "F3_Eskisehir", "F4_Ankara"]
kategoriler = ["Plastik", "Metal", "Ambalaj"]

# Tez Tablo 1: Atık Dağılımı (D_i) [cite: 156]
baz_atik = {"Istanbul": 100.6, "Kocaeli": 71.9, "Bursa": 43.1, "Izmir": 28.8, "Ankara": 28.8, "Eskisehir": 14.3}
oranlar = {"Plastik": 0.40, "Metal": 0.25, "Ambalaj": 0.35}

# Tez Bölüm 3.2.4: Finansal Parametreler [cite: 171, 173, 174]
C_var = 0.12  # Değişken taşıma maliyeti ($/ton-km)
N_years = 10  # Tez maliyet yıllıklandırma süresi (Yıl) [cite: 176]
E_factor = 0.062 # Emisyon faktörü (kg CO2 / ton-km) [cite: 148]

# Toplam Sabit Maliyetler (CAPEX)
# Istanbul: 50.000$, Anadolu: 25.000$ [cite: 173, 174]
sabit_maliyet_toplam = {
    "F1_Istanbul": 50000,
    "F2_Kocaeli": 25000,
    "F3_Eskisehir": 25000,
    "F4_Ankara": 25000
}

# Kapasite ve Mesafeler (Mevcut altyapı verileri)
kapasite = {"F1_Istanbul": 200, "F2_Kocaeli": 150, "F3_Eskisehir": 100, "F4_Ankara": 120}
gelirler = {"Plastik": 200, "Metal": 450, "Ambalaj": 150} # Kategorizasyon için korundu

mesafeler = {
    "Istanbul": {"F1_Istanbul": 10, "F2_Kocaeli": 85, "F3_Eskisehir": 280, "F4_Ankara": 450},
    "Kocaeli": {"F1_Istanbul": 85, "F2_Kocaeli": 10, "F3_Eskisehir": 200, "F4_Ankara": 350},
    "Bursa": {"F1_Istanbul": 150, "F2_Kocaeli": 130, "F3_Eskisehir": 150, "F4_Ankara": 380},
    "Izmir": {"F1_Istanbul": 480, "F2_Kocaeli": 450, "F3_Eskisehir": 410, "F4_Ankara": 590},
    "Ankara": {"F1_Istanbul": 450, "F2_Kocaeli": 350, "F3_Eskisehir": 235, "F4_Ankara": 10},
    "Eskisehir": {"F1_Istanbul": 280, "F2_Kocaeli": 200, "F3_Eskisehir": 10, "F4_Ankara": 235}
}

# ---------------------------------------------------------
# 2. MATEMATİKSEL MODEL (MILP FORMÜLASYONU)
# ---------------------------------------------------------
def optimize_reverse_logistics(senaryo_adi, talep_carpani, E_tax):
    model = pulp.LpProblem(f"Reverse_Logistics_Optimization_{senaryo_adi.replace(' ', '_')}", pulp.LpMinimize)

    # Karar Değişkenleri [cite: 184, 185]
    y = pulp.LpVariable.dicts("Open_Facility", tesisler, cat='Binary')
    x = pulp.LpVariable.dicts("Flow", [(i, j, k) for i in kaynaklar for j in tesisler for k in kategoriler], lowBound=0, cat='Continuous')

    # Tez Denklemi 6: Yıllıklandırılmış Yatırım Maliyeti (f_j) [cite: 177]
    f_j = {j: sabit_maliyet_toplam[j] / N_years for j in tesisler}

    # Tez Denklemleri 7, 8, 9: Amaç Fonksiyonu Bileşenleri [cite: 190, 192]
    Z_inv = pulp.lpSum([f_j[j] * y[j] for j in tesisler])
    Z_trans = pulp.lpSum([C_var * mesafeler[i][j] * x[(i, j, k)] for i in kaynaklar for j in tesisler for k in kategoriler])
    Z_env = pulp.lpSum([(E_tax/1000) * E_factor * mesafeler[i][j] * x[(i, j, k)] for i in kaynaklar for j in tesisler for k in kategoriler])

    # Global Amaç Fonksiyonu (Denklem 10) [cite: 197]
    model += Z_inv + Z_trans + Z_env

    # Kısıt 1: Talep Memnuniyeti (Denklem 11) [cite: 201]
    for i in kaynaklar:
        for k in kategoriler:
            model += pulp.lpSum([x[(i, j, k)] for j in tesisler]) == baz_atik[i] * talep_carpani * oranlar[k]

    # Kısıt 2: Kapasite Mantığı (Denklem 12) [cite: 205]
    for j in tesisler:
        model += pulp.lpSum([x[(i, j, k)] for i in kaynaklar for k in kategoriler]) <= kapasite[j] * y[j]

    model.solve()

    if pulp.LpStatus[model.status] != 'Optimal':
        return {"Senaryo": senaryo_adi, "Durum": "Çözümsüz"}

    # Performans Metrikleri: Toplam Karbon Ayak İzi (Denklem 14) [cite: 213]
    total_emissions = sum([E_factor * mesafeler[i][j] * x[(i, j, k)].varValue for i in kaynaklar for j in tesisler for k in kategoriler])
    total_revenue = sum([x[(i, j, k)].varValue * gelirler[k] for i in kaynaklar for j in tesisler for k in kategoriler])
    total_cost = pulp.value(model.objective)

    return {
        "Senaryo": senaryo_adi,
        "Açılan Tesisler": [j for j in tesisler if y[j].varValue == 1],
        "Yıllık Yatırım Maliyeti ($)": round(pulp.value(Z_inv), 2),
        "Lojistik Maliyet ($)": round(pulp.value(Z_trans), 2),
        "Karbon Vergisi Maliyeti ($)": round(pulp.value(Z_env), 2),
        "Toplam Karbon Ayak İzi (kg CO2)": round(total_emissions, 2),
        "Tahmini Net Kâr ($)": round(total_revenue - total_cost, 2),
        "Rotalar": [(i, j, sum(x[(i, j, k)].varValue for k in kategoriler)) for i in kaynaklar for j in tesisler if sum(x[(i, j, k)].varValue for k in kategoriler) > 0]
    }

# ---------------------------------------------------------
# 3. SENARYO ANALİZİ VE SONUÇLAR
# ---------------------------------------------------------
senaryolar = [
    {"ad": "Baz Senaryo (50$ Vergi)", "talep": 1.0, "vergi": 50},
    {"ad": "Yeşil Mutabakat (150$ Vergi)", "talep": 1.0, "vergi": 150}
]

rapor_verisi = []
for s in senaryolar:
    res = optimize_reverse_logistics(s["ad"], s["talep"], s["vergi"])
    rapor_verisi.append(res)

df_rapor = pd.DataFrame([{k: v for k, v in r.items() if k != 'Rotalar'} for r in rapor_verisi])
print(df_rapor.to_string(index=False))