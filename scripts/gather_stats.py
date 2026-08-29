import pandas as pd
import numpy as np

df = pd.read_csv('EDA/01_fireline_hotspot_kalimantan/04_feature_engineering/fireline_hotspot_featured.csv', parse_dates=['acq_date'])

print('total_rows', len(df))
print('date_min', df['acq_date'].min().strftime('%d %b %Y'))
print('date_max', df['acq_date'].max().strftime('%d %b %Y'))
print('unique_dates', df['acq_date'].nunique())
print('avg_per_day', round(len(df)/df['acq_date'].nunique(), 1))
print('mean_frp', round(df['frp'].mean(), 3))
print('median_frp', round(df['frp'].median(), 3))
print('max_frp', round(df['frp'].max(), 2))
print('frp_gt100', int((df['frp'] > 100).sum()))
print('frp_gt500', int((df['frp'] > 500).sum()))
print('total_frp_GW', round(df['frp'].sum()/1000, 1))

prov = df.groupby('kalimantan_region').agg(count=('frp','count'), total_frp=('frp','sum')).sort_values('count', ascending=False)
print('\nPROVINCE TABLE')
print(prov.to_string())

print('\nCONFIDENCE')
print(df['confidence'].value_counts().to_string())

print('\nSEASON')
print(df.groupby('season').agg(count=('frp','count'), mean_frp=('frp','mean')).to_string())

print('\nINTENSITY CLASS')
print(df['fire_intensity_class'].value_counts().to_string())

monthly = df.groupby('year_month').size()
print('\npeak_month', monthly.idxmax(), int(monthly.max()))
print('low_month', monthly.idxmin(), int(monthly.min()))

print('\nhigh_recurrence_grids', int((df.groupby('coord_grid_05deg').size() >= 5).sum()))
print('high_recurrence_hotspots', int(df['is_high_recurrence'].sum()))

print('\nDAYNIGHT')
print(df['daynight'].value_counts().to_string())

wd = df.groupby('is_weekend').agg(count=('frp','count'), mean_frp=('frp','mean'))
print('\nWEEKDAY_vs_WEEKEND')
print(wd.to_string())

print('\nmean_hazard_score', round(df['hazard_score'].mean(), 2))
print('hazard_gt50', int((df['hazard_score'] > 50).sum()))
print('hazard_gt75', int((df['hazard_score'] > 75).sum()))

print('\nTOP 5 EXTREME EVENTS')
top5 = df.nlargest(5, 'frp')[['acq_date','latitude','longitude','frp','kalimantan_region','confidence']]
for _, r in top5.iterrows():
    d = r['acq_date'].date()
    la = round(r['latitude'], 3)
    lo = round(r['longitude'], 3)
    f = round(r['frp'], 1)
    p = r['kalimantan_region']
    c = r['confidence']
    print(f'  {d} | {la}, {lo} | {f} MW | {p} | conf={c}')
