import { Component } from 'react';

// Konfigurasi Parameter — range disesuaikan dengan distribusi dataset sesungguhnya
const featureConfig = {
  ph:              { icon: '🧪', label: 'Tingkat pH',       unit: 'pH',    min: 6.5,   max: 8.5   },
  Hardness:        { icon: '🪨', label: 'Kekerasan Air',    unit: 'mg/L',  min: 150,   max: 250   },
  Solids:          { icon: '🧂', label: 'TDS (Padatan)',    unit: 'ppm',   min: 10000, max: 35000 },
  Chloramines:     { icon: '💧', label: 'Kloramin',         unit: 'ppm',   min: 5,     max: 9     },
  Sulfate:         { icon: '🌋', label: 'Sulfat',           unit: 'mg/L',  min: 280,   max: 400   },
  Conductivity:    { icon: '⚡', label: 'Konduktivitas',    unit: 'μS/cm', min: 300,   max: 600   },
  Organic_carbon:  { icon: '🍂', label: 'Karbon Organik',  unit: 'ppm',   min: 8,     max: 20    },
  Trihalomethanes: { icon: '🔬', label: 'Trihalometana',   unit: 'μg/L',  min: 30,    max: 100   },
  Turbidity:       { icon: '🌫️', label: 'Kekeruhan',        unit: 'NTU',   min: 1.5,   max: 5     }
};

// Preset sampel nyata dari dataset (nilai yang sudah diverifikasi)
const PRESET_AMAN = {
  ph: '9.02', Hardness: '128.10', Solids: '19859.68', Chloramines: '8.02',
  Sulfate: '300.15', Conductivity: '451.14', Organic_carbon: '14.77',
  Trihalomethanes: '73.78', Turbidity: '3.99'
};
const PRESET_TIDAK_AMAN = {
  ph: '2.50', Hardness: '380.00', Solids: '55000.00', Chloramines: '12.50',
  Sulfate: '475.00', Conductivity: '720.00', Organic_carbon: '26.00',
  Trihalomethanes: '118.00', Turbidity: '6.50'
};

// Deklarasi Kelas (OOP)
class App extends Component {
  // 1. Constructor untuk inisialisasi State (Atribut Kelas)
  constructor(props) {
    super(props);
    this.state = {
      formData: {
        ph: '', Hardness: '', Solids: '', Chloramines: '',
        Sulfate: '', Conductivity: '', Organic_carbon: '',
        Trihalomethanes: '', Turbidity: ''
      },
      result: null,
      loading: false,
      error: ''
    };
  }

  // 2. Metode Kelas: Menentukan status warna
  getStatusColor = (key, value) => {
    if (!value) return { text: 'Menunggu', bg: '#f8fafc', border: '#e2e8f0', color: '#94a3b8', level: 0 };
    const num = parseFloat(value);
    const { min, max } = featureConfig[key];

    if (num >= min && num <= max) return { text: 'Normal', bg: '#ecfdf5', border: '#34d399', color: '#10b981', level: 1 };
    if (num > max * 1.5 || num < min * 0.5) return { text: 'Bahaya', bg: '#fef2f2', border: '#f87171', color: '#ef4444', level: 3 };
    return { text: 'Waspada', bg: '#fffbeb', border: '#fbbf24', color: '#f59e0b', level: 2 };
  };

  // 3. Metode Kelas: Menangani perubahan input
  handleChange = (e) => {
    const { name, value } = e.target;
    this.setState((prevState) => ({
      formData: {
        ...prevState.formData,
        [name]: value
      },
      result: null
    }));
  };

  // 3b. Metode Kelas: Memuat preset nilai contoh
  loadPreset = (preset) => {
    this.setState({ formData: { ...preset }, result: null, error: '' });
  };

  // 4. Metode Kelas: Menangani pengiriman form (Fetch API ke Backend Flask)
  handleSubmit = async (e) => {
    e.preventDefault();
    this.setState({ loading: true, error: '', result: null });

    const { formData } = this.state;
    const payload = {};

    for (const key in formData) {
      payload[key] = parseFloat(formData[key]);
      if (isNaN(payload[key])) {
        this.setState({
          error: `Data "${featureConfig[key].label}" tidak valid.`,
          loading: false
        });
        return;
      }
    }

    try {
      // Kirim data ke backend Flask yang memuat model .pkl langsung
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      // data.potability: 0 = tidak aman, 1 = aman
      this.setState({ result: data.potability });
    } catch (err) {
      this.setState({ error: 'Sistem Error: ' + err.message });
    } finally {
      this.setState({ loading: false });
    }
  };

  // 5. Metode Render (Wajib dalam Class Component)
  render() {
    // Destructuring state agar lebih mudah dipanggil
    const { formData, result, loading, error } = this.state;

    // Menghitung persentase botol
    const filledFieldsCount = Object.values(formData).filter(v => v !== '').length;
    const fillPercentage = filledFieldsCount === 0 ? 5 : (filledFieldsCount / 9) * 90;

    // Logika warna air
    let waterGradient = 'linear-gradient(180deg, #38bdf8 0%, #0369a1 100%)';
    let waterGlow = 'rgba(56, 189, 248, 0.4)';

    if (result === 1) {
      waterGradient = 'linear-gradient(180deg, #2dd4bf 0%, #047857 100%)';
      waterGlow = 'rgba(45, 212, 191, 0.6)';
    } else if (result === 0) {
      waterGradient = 'linear-gradient(180deg, #ef4444 0%, #450a0a 100%)';
      waterGlow = 'rgba(239, 68, 68, 0.6)';
    } else {
      let maxDangerLevel = 0;
      for (const key in formData) {
        if (formData[key] !== '') {
          const status = this.getStatusColor(key, formData[key]);
          if (status.level > maxDangerLevel) maxDangerLevel = status.level;
        }
      }
      if (maxDangerLevel === 3) {
        waterGradient = 'linear-gradient(180deg, #f87171 0%, #7f1d1d 100%)';
        waterGlow = 'rgba(248, 113, 113, 0.5)';
      } else if (maxDangerLevel === 2) {
        waterGradient = 'linear-gradient(180deg, #facc15 0%, #a16207 100%)';
        waterGlow = 'rgba(250, 204, 21, 0.5)';
      }
    }

    return (
      <div style={styles.dashboard}>
        <header style={styles.header}>
          <div style={styles.logo}>💧 AquaMetrics AI</div>
          <div style={styles.nav}>Monitoring Kualitas Air Real-time</div>
        </header>

        <div style={styles.mainContent}>
          <div style={styles.dataPanel}>
            <div style={styles.panelHeader}>
              <h2 style={styles.panelTitle}>Input Parameter Lab</h2>
              <p style={styles.panelSubtitle}>Pendekatan Object-Oriented Programming (Class Component)</p>
              <div style={styles.presetRow}>
                <span style={styles.presetLabel}>Contoh nilai:</span>
                <button type="button" style={styles.presetBtnAman}
                  onClick={() => this.loadPreset(PRESET_AMAN)}>✅ Isi Contoh AMAN</button>
                <button type="button" style={styles.presetBtnBahaya}
                  onClick={() => this.loadPreset(PRESET_TIDAK_AMAN)}>❌ Isi Contoh TERCEMAR</button>
              </div>
            </div>

            <form onSubmit={this.handleSubmit} id="water-form">
              <div style={styles.gridContainer}>
                {Object.keys(formData).map((key) => {
                  const status = this.getStatusColor(key, formData[key]);
                  return (
                    <div key={key} style={{ ...styles.card, borderColor: status.border }}>
                      <div style={styles.cardHeader}>
                        <span style={styles.cardIcon}>{featureConfig[key].icon}</span>
                        <span style={styles.cardLabel}>{featureConfig[key].label}</span>
                      </div>

                      <div style={styles.inputWrapper}>
                        <input
                          type="number" step="any" name={key}
                          value={formData[key]} onChange={this.handleChange}
                          placeholder="0.00" required style={styles.input}
                        />
                        <span style={styles.unit}>{featureConfig[key].unit}</span>
                      </div>

                      <div style={{ ...styles.statusBadge, backgroundColor: status.bg, color: status.color }}>
                        <span style={styles.statusDot(status.color)}></span>
                        {status.text}
                      </div>

                      <div style={styles.rangeText}>
                        Range aman: {featureConfig[key].min.toLocaleString()} – {featureConfig[key].max.toLocaleString()} {featureConfig[key].unit}
                      </div>
                    </div>
                  );
                })}
              </div>
            </form>
          </div>

          <div style={styles.resultPanel}>
            <div style={styles.resultCard}>
              <h3 style={styles.resultHeading}>Visualisasi Sampel Air</h3>

              <div style={styles.bottleContainer}>
                <div style={styles.bottleCap}></div>
                <div style={styles.bottleNeck}></div>
                <div style={styles.bottleBody}>
                  <div style={{
                    ...styles.waterFill,
                    height: `${fillPercentage}%`,
                    background: waterGradient,
                    boxShadow: `0 -5px 20px ${waterGlow}`,
                  }}>
                    <div style={styles.waterSurface}></div>
                  </div>
                </div>
              </div>

              <div style={styles.bottleStatusText}>
                {result === null
                  ? `Kapasitas Form Terisi: ${filledFieldsCount}/9`
                  : (result === 1 ? '✅ Air Bersih & Aman' : '❌ Air Tercemar!')}
              </div>

              <hr style={styles.divider} />

              <div style={styles.actionSection}>
                {error && <div style={styles.alertBox}>⚠️ {error}</div>}

                <button
                  type="submit" form="water-form" disabled={loading}
                  style={{ ...styles.runButton, ...(loading ? styles.buttonDisabled : {}) }}
                >
                  {loading ? '🧪 Model sedang memproses...' : 'Jalankan Analisis AI 🚀'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

// --- STYLING ---
const styles = {
  presetRow: { display: 'flex', alignItems: 'center', gap: '10px', marginTop: '12px', flexWrap: 'wrap' },
  presetLabel: { fontSize: '13px', color: '#64748b', fontWeight: '500' },
  presetBtnAman: { padding: '6px 14px', backgroundColor: '#ecfdf5', color: '#059669', border: '1.5px solid #34d399', borderRadius: '8px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' },
  presetBtnBahaya: { padding: '6px 14px', backgroundColor: '#fef2f2', color: '#dc2626', border: '1.5px solid #f87171', borderRadius: '8px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' },
  dashboard: { minHeight: '100vh', backgroundColor: '#f1f5f9', fontFamily: '"Inter", sans-serif' },
  header: { backgroundColor: '#ffffff', padding: '16px 32px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0' },
  logo: { fontSize: '20px', fontWeight: '800', color: '#0f766e' },
  nav: { fontSize: '14px', color: '#64748b' },
  mainContent: { display: 'flex', flexWrap: 'wrap', padding: '32px', gap: '32px', maxWidth: '1400px', margin: '0 auto' },
  dataPanel: { flex: '1 1 60%', minWidth: '320px' },
  panelHeader: { marginBottom: '24px' },
  panelTitle: { margin: '0 0 8px 0', fontSize: '24px', color: '#1e293b' },
  panelSubtitle: { margin: 0, color: '#64748b', fontSize: '15px' },
  gridContainer: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' },
  card: { backgroundColor: '#ffffff', padding: '16px', borderRadius: '12px', borderLeft: '4px solid', display: 'flex', flexDirection: 'column', transition: 'border-color 0.3s ease' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' },
  cardIcon: { fontSize: '18px' },
  cardLabel: { fontSize: '14px', fontWeight: '600', color: '#475569' },
  inputWrapper: { display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '12px' },
  input: { width: '100%', padding: '4px', border: 'none', borderBottom: '2px solid #cbd5e1', fontSize: '20px', fontWeight: '700', color: '#0f172a', outline: 'none', backgroundColor: 'transparent' },
  unit: { fontSize: '12px', color: '#94a3b8', fontWeight: '500' },
  statusBadge: { marginTop: 'auto', padding: '4px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px', width: 'fit-content' },
  statusDot: (color) => ({ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: color }),
  rangeText: { marginTop: '8px', fontSize: '11px', color: '#94a3b8', fontStyle: 'italic' },
  resultPanel: { flex: '1 1 30%', minWidth: '320px' },
  resultCard: { backgroundColor: '#ffffff', borderRadius: '16px', padding: '32px', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)', position: 'sticky', top: '32px' },
  resultHeading: { margin: '0 0 30px 0', fontSize: '18px', color: '#334155', textAlign: 'center', fontWeight: '700' },
  bottleContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '0 auto 20px auto', height: '240px' },
  bottleCap: { width: '40px', height: '15px', backgroundColor: '#cbd5e1', borderRadius: '4px 4px 0 0', zIndex: 2 },
  bottleNeck: { width: '30px', height: '30px', backgroundColor: 'rgba(255, 255, 255, 0.4)', borderLeft: '3px solid #e2e8f0', borderRight: '3px solid #e2e8f0', zIndex: 1 },
  bottleBody: { width: '120px', height: '180px', backgroundColor: 'rgba(255, 255, 255, 0.4)', border: '3px solid #e2e8f0', borderRadius: '20px 20px 10px 10px', position: 'relative', overflow: 'hidden', boxShadow: 'inset 0 0 10px rgba(255,255,255,0.5), 0 10px 15px -3px rgba(0,0,0,0.1)' },
  waterFill: { position: 'absolute', bottom: 0, left: 0, width: '100%', transition: 'height 0.8s cubic-bezier(0.4, 0, 0.2, 1), background 0.5s ease' },
  waterSurface: { width: '100%', height: '6px', backgroundColor: 'rgba(255, 255, 255, 0.3)', position: 'absolute', top: 0 },
  bottleStatusText: { textAlign: 'center', fontSize: '15px', fontWeight: 'bold', color: '#475569' },
  divider: { border: 'none', borderTop: '1px solid #e2e8f0', margin: '24px 0' },
  actionSection: { textAlign: 'center' },
  runButton: { width: '100%', padding: '16px', backgroundColor: '#0f766e', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: 'pointer', transition: 'all 0.2s' },
  buttonDisabled: { backgroundColor: '#cbd5e1', cursor: 'not-allowed' },
  alertBox: { padding: '12px', backgroundColor: '#fef2f2', color: '#b91c1c', borderRadius: '8px', marginBottom: '16px', fontSize: '14px', textAlign: 'left' }
};

export default App;