import urllib.request, json, os

# Updated list of sources to try
sources = [
    'https://raw.githubusercontent.com/denyherianto/indonesia-geojson-topojson-maps-with-38-provinces/main/provinces.geojson',
    'https://raw.githubusercontent.com/ardian28/GeoJson-Indonesia-38-Provinsi/main/indonesia-provinces.geojson',
    'https://raw.githubusercontent.com/Alf-Anas/batas-administrasi-indonesia/main/provinsi.geojson',
    'https://raw.githubusercontent.com/IndraSubagja/genz-frontend/main/public/data/indonesia.geojson',
    'https://raw.githubusercontent.com/rizki4106/daerah-indonesia/main/provinsi.geojson',
    'https://raw.githubusercontent.com/tomihardjo/geojson-indonesia/main/indonesia.geojson',
    'https://raw.githubusercontent.com/iqbal-pratama/geojson-indonesia/main/indonesia-provinces.geojson',
]

selected_fname = None
for url in sources:
    fname = url.split('/')[-1]
    try:
        print(f'Trying: {url}')
        urllib.request.urlretrieve(url, fname)
        with open(fname, encoding='utf-8') as f:
            data = json.load(f)
        features = data.get('features', [])
        print(f'  OK -> {len(features)} features')
        if features:
            props = list(features[0]['properties'].keys())
            print(f'  Props: {props}')
        kal_kw = ['alimantan', 'ALIMANTAN', 'Kalimantan']
        kal = [ft for ft in features if any(any(kw in str(v) for kw in kal_kw) for v in ft['properties'].values())]
        print(f'  Kalimantan features: {len(kal)}')
        if len(kal) >= 4:
            selected_fname = fname
            print(f'  >> USING THIS FILE')
            break
        else:
            os.remove(fname)
    except Exception as e:
        print(f'  FAILED: {e}')
        if os.path.exists(fname):
            os.remove(fname)

if selected_fname:
    target = 'indonesia_provinces.json'
    if os.path.exists(target):
        os.remove(target)
    os.rename(selected_fname, target)
    print(f'\nSaved as: {target}')
    # Print a sample name for verification
    with open(target, encoding='utf-8') as f:
        data = json.load(f)
    kal_kw = ['alimantan']
    kal_names = [str(list(ft['properties'].values())) for ft in data['features']
                 if any(any(kw in str(v) for kw in kal_kw) for v in ft['properties'].values())]
    print('Kalimantan entries:')
    for n in kal_names:
        print(' -', n[:100])
else:
    print('\nAll sources failed')
