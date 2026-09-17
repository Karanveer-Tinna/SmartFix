<script setup>
import { ref } from "vue";

const activeDataTab = ref("overview");

const sqliteTables = [
  { name: "documents", count: 7, description: "Tracks PDF manual filenames, status, length, chunk counts, timestamps" },
  { name: "chunks", count: 48, description: "Stores document chunks, character offsets, embedding model info, vector IDs" },
];

const vectorBackends = [
  { name: "ChromaDB (Local Persistent)", status: "Active", dim: 384, metric: "Cosine (HNSW)", latency: "12.4 ms", cost: "$0.00" },
  { name: "Pinecone (Cloud Adapter)", status: "Connected / Fallback Ready", dim: 384, metric: "Cosine", latency: "48.2 ms", cost: "Serverless Tier" },
];

const multimodalAssets = [
  { type: "Wiring Schematic", equipment: "HA-MICRO-01 Microwave", source: "microwave_schematic.png", features: "OCR wire pinouts, 2.4kV transformer cathode circuit" },
  { type: "Exploded View Diagram", equipment: "HA-AIRFRY-03 Air Fryer", source: "airfryer_exploded.png", features: "Part callouts #01-#03 mapped to spare parts catalog" },
  { type: "Thermal PCB Image", equipment: "HA-WASH-04 Washer", source: "washer_motor_thermal.jpg", features: "Hot spot temperature detection (92.4°C threshold flag)" },
];

const microserviceStores = [
  { service: "Equipment Service", port: "8002", entity: "Equipment Specs & Operating Ratings", records: "HA-MICRO-01, HA-WASH-04, HA-OVEN-05, EQ-1023, EQ-2045, EQ-3081" },
  { service: "Spare Parts Service", port: "8005", entity: "Compatible Parts & Inventory", records: "MAG-2450-900W, NTC-100K-SENSOR, PMP-WASH-45W, ELEM-OVEN-2400W" },
  { service: "History Service", port: "8004", entity: "Historical Maintenance Logs", records: "Service repair records, past technician resolutions" },
  { service: "Ticket Service", port: "8006", entity: "Safety LOTO Dispatch Tickets", records: "Automated critical hazard tickets (TKT-1001)" },
];
</script>

<template>
  <div class="datalayer-container">
    <div class="page-header">
      <div class="badge-row">
        <span class="sub-badge">Architecture View</span>
        <span class="tag-badge">Hybrid Data Layer</span>
      </div>
      <h2>Enterprise Data Layer & Persistence Architecture</h2>
      <p>Multi-modal persistence: Relational SQLite metadata, Dual Vector Store (ChromaDB + Pinecone), and Visual Schematic Image Ingestion.</p>
    </div>

    <!-- Data Layer Sub-Tabs -->
    <div class="tab-nav">
      <button :class="{ active: activeDataTab === 'overview' }" @click="activeDataTab = 'overview'">1. Data Layer Overview</button>
      <button :class="{ active: activeDataTab === 'vector' }" @click="activeDataTab === 'vector'">2. ChromaDB & Pinecone</button>
      <button :class="{ active: activeDataTab === 'multimodal' }" @click="activeDataTab === 'multimodal'">3. Multimodal & Schematics</button>
      <button :class="{ active: activeDataTab === 'sqlite' }" @click="activeDataTab === 'sqlite'">4. SQLite & Microservices</button>
    </div>

    <!-- 1. Overview Section -->
    <div v-if="activeDataTab === 'overview'" class="tab-content">
      <div class="arch-card">
        <h3>SmartFix Data Layer Flow</h3>
        <div class="pipeline-diagram">
          <div class="node">
            <div class="node-title">Raw Documents & Schematics</div>
            <div class="node-body">PDF Manuals, Exploded Views, Thermal Images (data/documents)</div>
          </div>
          <div class="arrow">➔</div>
          <div class="node">
            <div class="node-title">Extraction & Splitters</div>
            <div class="node-body">Recursive Text Splitter + Multimodal Schematic OCR</div>
          </div>
          <div class="arrow">➔</div>
          <div class="node">
            <div class="node-title">Dual Vector Store</div>
            <div class="node-body">Local ChromaDB (384-d) + Cloud Pinecone Adapter</div>
          </div>
          <div class="arrow">➔</div>
          <div class="node">
            <div class="node-title">Relational Store</div>
            <div class="node-body">SQLite metadata (data/knowledge-base.db)</div>
          </div>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-label">Vector Store Backends</span>
          <span class="stat-value">2 (ChromaDB + Pinecone)</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Embedding Dimensions</span>
          <span class="stat-value">384 Dense Float</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Indexed Documents</span>
          <span class="stat-value">7 Real PDF Manuals</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Microservice Repositories</span>
          <span class="stat-value">4 Dedicated Data Stores</span>
        </div>
      </div>
    </div>

    <!-- 2. ChromaDB & Pinecone Section -->
    <div v-else-if="activeDataTab === 'vector'" class="tab-content">
      <div class="table-card">
        <h3>Dual Vector Store Adapter Comparison</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Backend</th>
              <th>Status</th>
              <th>Dimensions</th>
              <th>Distance Metric</th>
              <th>Mean Query Latency</th>
              <th>Storage Cost</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vb in vectorBackends" :key="vb.name">
              <td><strong>{{ vb.name }}</strong></td>
              <td><span class="status-chip active">{{ vb.status }}</span></td>
              <td><code>{{ vb.dim }}</code></td>
              <td>{{ vb.metric }}</td>
              <td><strong>{{ vb.latency }}</strong></td>
              <td>{{ vb.cost }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 3. Multimodal & Schematics Section -->
    <div v-else-if="activeDataTab === 'multimodal'" class="tab-content">
      <div class="table-card">
        <h3>Multimodal Image & Visual Schematic Ingestion</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Asset Type</th>
              <th>Target Equipment</th>
              <th>File Name</th>
              <th>Extracted Vision & OCR Features</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="asset in multimodalAssets" :key="asset.source">
              <td><span class="type-badge">{{ asset.type }}</span></td>
              <td><strong>{{ asset.equipment }}</strong></td>
              <td><code>{{ asset.source }}</code></td>
              <td>{{ asset.features }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 4. SQLite & Microservices Section -->
    <div v-else-if="activeDataTab === 'sqlite'" class="tab-content">
      <div class="table-card">
        <h3>SQLite Database Tables (data/knowledge-base.db)</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Table Name</th>
              <th>Record Count</th>
              <th>Description & Schema</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tbl in sqliteTables" :key="tbl.name">
              <td><code>{{ tbl.name }}</code></td>
              <td><strong>{{ tbl.count }}</strong></td>
              <td>{{ tbl.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-card" style="margin-top: 1.5rem;">
        <h3>Microservice Data Repositories</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Port</th>
              <th>Managed Entity</th>
              <th>Sample Records</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="svc in microserviceStores" :key="svc.service">
              <td><strong>{{ svc.service }}</strong></td>
              <td><code>:{{ svc.port }}</code></td>
              <td>{{ svc.entity }}</td>
              <td>{{ svc.records }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.datalayer-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.badge-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.sub-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent);
  background: var(--accent-light);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.tag-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #10b981;
  background: rgba(16, 185, 129, 0.12);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.tab-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.tab-nav button {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  padding: 0.5rem 0.85rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-nav button.active {
  background: var(--card-bg);
  border-color: var(--border-color);
  color: var(--accent);
}

.arch-card, .table-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.25rem;
}

.pipeline-diagram {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.node {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0.75rem;
  min-width: 170px;
}

.node-title {
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-main);
}

.node-body {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.arrow {
  color: var(--accent);
  font-weight: bold;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.stat-box {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--accent);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.75rem;
  font-size: 0.85rem;
}

.data-table th, .data-table td {
  padding: 0.65rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.data-table th {
  color: var(--text-dim);
  font-weight: 600;
}

.status-chip {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.type-badge {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.75rem;
}
</style>
