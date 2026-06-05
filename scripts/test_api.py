import urllib.request, json

def test(label, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        'http://localhost:5000/predict', data=data,
        headers={'Content-Type': 'application/json'}
    )
    try:
        resp = urllib.request.urlopen(req)
        r = json.loads(resp.read())
        status = 'AMAN' if r['potability'] == 1 else 'TIDAK AMAN'
        print(f"{label}: {status}  (hybrid={r['hybrid_score']}, rule={r['rule_score']}, ml={r['ml_prob_aman']})")
    except Exception as e:
        print(f"{label}: ERROR - {e}")

test('Semua DALAM range aman',
     {'ph':7.5,'Hardness':200,'Solids':22000,'Chloramines':7.0,
      'Sulfate':340,'Conductivity':430,'Organic_carbon':14,
      'Trihalomethanes':65,'Turbidity':4.0})

test('Preset AMAN dari dataset',
     {'ph':9.02,'Hardness':128.10,'Solids':19859.68,'Chloramines':8.02,
      'Sulfate':300.15,'Conductivity':451.14,'Organic_carbon':14.77,
      'Trihalomethanes':73.78,'Turbidity':3.99})

test('Preset TIDAK AMAN (pH=4.37)',
     {'ph':4.37,'Hardness':188.65,'Solids':29542.34,'Chloramines':8.12,
      'Sulfate':301.02,'Conductivity':456.31,'Organic_carbon':16.35,
      'Trihalomethanes':46.70,'Turbidity':4.65})

test('pH sangat rendah + semua ekstrem',
     {'ph':2.0,'Hardness':50,'Solids':500,'Chloramines':0.5,
      'Sulfate':100,'Conductivity':100,'Organic_carbon':2,
      'Trihalomethanes':5,'Turbidity':0.5})
