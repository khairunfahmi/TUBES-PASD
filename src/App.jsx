import React, { Component } from 'react';

// ============================================================
// Konfigurasi API URL
// Prioritas: 1. VITE_API_URL dari .env  2. Fallback ke localhost
// ============================================================
const DEFAULT_API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// Konfigurasi Parameter (Tetap di luar kelas karena bersifat statis/konstan)
const featureConfig = {
  ph: { icon: '🧪', label: 'Tingkat pH', unit: 'pH', min: 6.5, max: 8.5 },
  Hardness: { icon: '🪨', label: 'Kekerasan Air', unit: 'mg/L', min: 0, max: 200 },
  Solids: { icon: '🧂', label: 'TDS (Padatan)', unit: 'ppm', min: 0, max: 500 },
  Chloramines: { icon: '💧', label: 'Kloramin', unit: 'ppm', min: 0, max: 4 },
  Sulfate: { icon: '🌋', label: 'Sulfat', unit: 'mg/L', min: 0, max: 250 },
  Conductivity: { icon: '⚡', label: 'Konduktivitas', unit: 'μS/cm', min: 0, max: 400 },
  Organic_carbon: { icon: '🍂', label: 'Karbon Organik', unit: 'ppm', min: 0, max: 10 },
  Trihalomethanes: { icon: '🔬', label: 'Trihalometana', unit: 'μg/L', min: 0, max: 80 },
  Turbidity: { icon: '🌫️', label: 'Kekeruhan', unit: 'NTU', min: 0, max: 5 }
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
      error: '',
      apiUrl: DEFAULT_API_URL,
      apiStatus: 'checking' // 'checking' | 'online' | 'offline'
    };
  }

  // Metode: Cek koneksi API saat komponen mount
  componentDidMount() {
    this.checkApiConnection();
  }

  // Metode: Cek apakah API tersedia
  checkApiConnection = async () => {
    this.setState({ apiStatus: 'checking' });
    try {
      const response = await fetch(this.state.apiUrl + '/', { 
        method: 'GET',
        headers: { 'ngrok-skip-browser-warning': 'true' },
        signal: AbortSignal.timeout(5000) 
      });
      if (response.ok) {
        this.setState({ apiStatus: 'online' });
      } else {
        this.setState({ apiStatus: 'offline' });
      }
    } catch {
      this.setState({ apiStatus: 'offline' });
    }
  };


  // 2. Metode Kelas: Menentukan status warna (Validasi Visual)
  getStatusColor = (key, value) => {
    const { min, max } = featureConfig[key];
    const tooltipText = `Batas aman: ${min} - ${max} ${featureConfig[key].unit}`;
    
    if (!value) return { text: 'Menunggu', bg: '#f8fafc', border: '#e2e8f0', color: '#94a3b8', level: 0, tooltip: tooltipText };
    
    const num = parseFloat(value);
    if (num >= min && num <= max) return { text: 'Aman', bg: '#ecfdf5', border: '#10b981', color: '#059669', level: 1, tooltip: tooltipText };
    
    return { text: 'Tidak Aman', bg: '#fef2f2', border: '#ef4444', color: '#dc2626', level: 2, tooltip: tooltipText };
  };

  // 3. Metode Kelas: Menangani perubahan input
  handleChange = (e) => {
    const { name, value } = e.target;
    this.setState((prevState) => ({
      formData: {
        ...prevState.formData,
        [name]: value
      },
      result: null // Reset hasil setiap ada input baru
    }));
  };

  // 4. Metode Kelas: Menangani pengiriman form (Fetch API)
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
      const response = await fetch(this.state.apiUrl + '/predict', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Koneksi API terputus.');
      const data = await response.json();
      
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
    const { formData, result, loading, error, apiStatus } = this.state;

    // Menghitung persentase botol
    const filledFieldsCount = Object.values(formData).filter(v => v !== '').length;
    const fillPercentage = filledFieldsCount === 0 ? 5 : (filledFieldsCount / 9) * 90;

    // Logika warna air berdasarkan agregat validasi visual
    let waterGradient = 'linear-gradient(180deg, #2dd4bf 0%, #0f766e 100%)'; // teal aman
    let waterGlow = 'rgba(45, 212, 191, 0.5)';
    
    let dangerCount = 0;
    for (const key in formData) {
      if (formData[key] !== '') {
        const status = this.getStatusColor(key, formData[key]);
        if (status.level > 1) dangerCount++;
      }
    }

    if (dangerCount > 3) {
      waterGradient = 'linear-gradient(180deg, #fca5a5 0%, #be123c 100%)'; // merah muda
      waterGlow = 'rgba(252, 165, 165, 0.5)';
    } else if (dangerCount > 0) {
      waterGradient = 'linear-gradient(180deg, #fbbf24 0%, #b45309 100%)'; // amber
      waterGlow = 'rgba(251, 191, 36, 0.5)';
    } else if (filledFieldsCount === 0) {
      waterGradient = 'linear-gradient(180deg, #38bdf8 0%, #0369a1 100%)'; // biru default
      waterGlow = 'rgba(56, 189, 248, 0.4)';
    }

    // Status koneksi API
    const statusConfig = {
      checking: { color: '#f59e0b', text: '⏳ Memeriksa...', bg: '#fffbeb' },
      online: { color: '#10b981', text: '🟢 API Terhubung', bg: '#ecfdf5' },
      offline: { color: '#ef4444', text: '🔴 API Offline', bg: '#fef2f2' }
    };
    const currentStatus = statusConfig[apiStatus];

    return (
      <div style={styles.dashboard}>
        <header style={styles.header}>
          <div style={styles.logo}>💧 AquaMetrics AI</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Status Koneksi API */}
            <div 
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '6px 14px', borderRadius: '20px', fontSize: '13px',
                fontWeight: '600', transition: 'all 0.2s',
                backgroundColor: currentStatus.bg, color: currentStatus.color,
                border: `1px solid ${currentStatus.color}20`,
                boxShadow: apiStatus === 'online' ? '0 0 10px rgba(16, 185, 129, 0.2)' : 'none'
              }}
            >
              {currentStatus.text}
            </div>
            <div style={styles.nav}>Monitoring Kualitas Air Real-time</div>
          </div>
        </header>

        <div style={styles.mainContent}>
          <div style={styles.dataPanel}>
            <div style={styles.panelHeader}>
              <h2 style={styles.panelTitle}>Input Parameter Lab</h2>
              <p style={styles.panelSubtitle}>Pendekatan Object-Oriented Programming (Class Component)</p>
            </div>

            <form onSubmit={this.handleSubmit} id="water-form">
              <div style={styles.gridContainer}>
                {Object.keys(formData).map((key) => {
                  const status = this.getStatusColor(key, formData[key]);
                  return (
                    <div key={key} className="card-hover" style={{ ...styles.card, borderColor: status.border }}>
                      <div style={styles.cardHeader}>
                        <span style={styles.cardIcon}>{featureConfig[key].icon}</span>
                        <span style={styles.cardLabel}>
                          {featureConfig[key].label}
                          <span 
                            title={status.tooltip} 
                            style={{ marginLeft: '6px', cursor: 'help', color: '#94a3b8', fontSize: '12px' }}
                          >
                            ⓘ
                          </span>
                        </span>
                      </div>

                      <div className="input-focus-ring" style={styles.inputWrapper}>
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
                    {/* Animasi Gelembung Air */}
                    {fillPercentage > 5 && Array.from({ length: 4 }).map((_, i) => (
                      <div key={i} className="bubble" style={{
                        width: `${Math.random() * 6 + 4}px`,
                        height: `${Math.random() * 6 + 4}px`,
                        left: `${Math.random() * 80 + 10}%`,
                        animationDuration: `${Math.random() * 1.5 + 1.5}s`,
                        animationDelay: `${Math.random() * 1.5}s`
                      }}></div>
                    ))}
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
                  className={loading ? "pulse-anim" : ""}
                  style={{ ...styles.runButton, ...(loading ? styles.buttonDisabled : {}) }}
                >
                  {loading ? '⏳ Menganalisis...' : 'Jalankan Analisis AI 🚀'}
                </button>
                
                {filledFieldsCount < 9 && !result && !loading && (
                  <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '12px', transition: 'all 0.3s' }}>
                    💡 Lengkapi semua parameter dulu untuk analisis akurat
                  </p>
                )}
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