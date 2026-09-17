<script setup>
import { ref, reactive, onMounted } from 'vue'

// Global State
const evidenceList = ref([])
const isLoading = ref(true)
const expandedHash = ref(null)
const evidenceFindings = ref([])
const custodyEvents = ref([])
const isLoadingFindings = ref(false)
const isVerifying = ref(false)
const pageRankGraphData = ref(null)

// Modal State Management
const activeModal = ref(null) // 'ingest' | 'checkout' | 'checkin' | 'purge' | 'verify' | null
const selectedHash = ref('')

const modalForm = reactive({
  officerId: '',
  location: '',
  reason: '',
  encryptionKey: 'SIFT_Default_Secure_Key_2026',
  file: null,
  fieldHash: ''
})

const notification = ref({ show: false, title: '', message: '', type: 'info' })

// Helpers
const triggerNotification = (title, message, type = 'info') => {
  notification.value = { show: true, title, message, type }
}
const closeNotification = () => { notification.value.show = false }
const formatDate = (timestamp) => new Date(timestamp).toLocaleString()

const handleFileChange = (event) => {
  modalForm.file = event.target.files[0]
}

const openModal = (type, hash = '') => {
  selectedHash.value = hash
  activeModal.value = type
  
  // Set defaults based on action type
  if (type === 'ingest') {
    modalForm.officerId = ''
    modalForm.location = ''
    modalForm.file = null
    modalForm.fieldHash = ''
  } else if (type === 'checkout') {
    modalForm.officerId = 'Officer_HQ'
    modalForm.location = 'HQ Central Vault'
    modalForm.reason = 'External forensic analysis'
    modalForm.encryptionKey = 'SIFT_Default_Secure_Key_2026'
  } else if (type === 'checkin') {
    modalForm.officerId = 'Officer_HQ'
    modalForm.location = 'HQ Central Vault'
    modalForm.reason = 'Returning working copy after analysis'
    modalForm.encryptionKey = 'SIFT_Default_Secure_Key_2026'
    modalForm.file = null
  } else if (type === 'purge') {
    modalForm.officerId = 'Superior_Officer_01'
    modalForm.location = 'HQ Central Vault'
    modalForm.reason = 'Warrant Expired - Court Order #2026-881'
  } else if (type === 'verify') {
    modalForm.officerId = 'Officer_HQ'
    modalForm.location = 'HQ Central Vault'
  }
}

const closeModal = () => {
  activeModal.value = null
  selectedHash.value = ''
  modalForm.file = null
}

// API Calls
const fetchEvidence = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/evidence')
    const data = await response.json()
    evidenceList.value = data.evidence
  } catch (error) {
    triggerNotification("Connection Error", "Could not connect to SIFT backend.", "error")
  } finally {
    isLoading.value = false
  }
}

const toggleRow = async (hash) => {
  pageRankGraphData.value = null
  evidenceFindings.value = []
  custodyEvents.value = []
  
  if (expandedHash.value === hash) {
    expandedHash.value = null
    return
  }
  
  expandedHash.value = hash
  isLoadingFindings.value = true
  
  try {
    const [findingsRes, custodyRes] = await Promise.all([
      fetch(`http://localhost:8000/api/v1/evidence/${hash}/findings`),
      fetch(`http://localhost:8000/api/v1/evidence/${hash}/custody`)
    ])
    const findingsData = await findingsRes.json()
    const custodyData = await custodyRes.json()
    
    evidenceFindings.value = findingsData.findings
    custodyEvents.value = custodyData.events
    
    const pageRankfinding = findingsData.findings.find(f => f.type === 'PAGERANK')
    if (pageRankfinding && pageRankfinding.statement) {
      try { pageRankGraphData.value = JSON.parse(pageRankfinding.statement) } catch (e) { pageRankGraphData.value = null }
    }
  } catch (error) {
    console.error(error)
  } finally {
    isLoadingFindings.value = false
  }
}

const submitIngest = async () => {
  if (!modalForm.file || !modalForm.officerId || !modalForm.location) {
    triggerNotification("Missing Fields", "File, Officer ID, and Location are required.", "error")
    return
  }
  const formData = new FormData()
  formData.append("file", modalForm.file)
  if (modalForm.fieldHash) formData.append("field_hash", modalForm.fieldHash)
  formData.append("officer_id", modalForm.officerId)
  formData.append("location", modalForm.location)

  try {
    const response = await fetch('http://localhost:8000/api/v1/ingest', { method: 'POST', body: formData })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || "Upload failed")
    }
    closeModal()
    triggerNotification("Evidence Ingested & Sealed", "Cryptographic baseline recorded in Neo4j.", "success")
    await fetchEvidence()
  } catch (error) {
    triggerNotification("Ingest Error", error.message, "error")
  }
}

const submitCheckout = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/evidence/${selectedHash.value}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        officer_id: modalForm.officerId,
        location: modalForm.location,
        reason: modalForm.reason,
        encryption_key: modalForm.encryptionKey
      })
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || "Checkout failed")
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `AES_ENC_d_DE_${selectedHash.value.substring(0, 8)}.enc`
    document.body.appendChild(a)
    a.click()
    a.remove()
    
    closeModal()
    triggerNotification("Checkout Complete", "Encrypted working copy downloaded.", "success")
    await fetchEvidence()
    await toggleRow(selectedHash.value)
  } catch (err) {
    triggerNotification("Checkout Error", err.message, "error")
  }
}

const submitCheckin = async () => {
  if (!modalForm.file) return triggerNotification("Error", "Encrypted file required.", "error")
  
  const formData = new FormData()
  formData.append("file", modalForm.file)
  formData.append("officer_id", modalForm.officerId)
  formData.append("location", modalForm.location)
  formData.append("reason", modalForm.reason)
  formData.append("encryption_key", modalForm.encryptionKey)

  try {
    const response = await fetch(`http://localhost:8000/api/v1/evidence/${selectedHash.value}/checkin`, {
      method: 'POST',
      body: formData,
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || data.message || "Check-in failed")
    
    closeModal()
    if (data.is_intact) {
      triggerNotification("Handoff Verified", data.message, "success")
    } else {
      triggerNotification("Spoliation Detected", data.message, "error")
    }
    await fetchEvidence()
    await toggleRow(selectedHash.value)
  } catch (error) {
    triggerNotification("Check-in Error", error.message, "error")
  }
}

const submitPurge = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/evidence/${selectedHash.value}/purge`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        officer_id: modalForm.officerId,
        location: modalForm.location,
        reason: modalForm.reason
      })
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || "Purge execution failed.")
    
    closeModal()
    triggerNotification("Evidence Purged", data.message, "warning")
    await fetchEvidence()
    await toggleRow(selectedHash.value)
  } catch (error) {
    triggerNotification("Purge Error", error.message, "error")
  }
}

const submitVerify = async () => {
  isVerifying.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/v1/evidence/${selectedHash.value}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ officer_id: modalForm.officerId, location: modalForm.location })
    })
    const data = await response.json()
    closeModal()
    if (data.is_intact) {
      triggerNotification("SEAL INTACT", "Disk SHA-256 matches Neo4j baseline.", "success")
    } else {
      triggerNotification("SPOLIATION DETECTED!", "File contents on disk have been altered!", "error")
    }
    await fetchEvidence()
  } catch (error) {
    triggerNotification("Verification Error", "Failed to complete disk re-hash check.", "error")
  } finally {
    isVerifying.value = false
  }
}

onMounted(() => fetchEvidence())
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 p-4 sm:p-6 lg:p-8">
    <!-- Header -->
    <header class="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">SIFT Chain of Custody System</h1>
        <p class="text-xs sm:text-sm text-slate-400 mt-1">Cryptographic Evidence Vault & Automated Provenance Ledger</p>
      </div>
      <button @click="openModal('ingest')" class="w-full sm:w-auto px-5 py-2.5 bg-blue-600 hover:bg-blue-500 font-bold rounded-lg shadow-lg text-sm transition-all flex items-center justify-center gap-2">
        <span>+</span> Ingest Evidence
      </button>
    </header>

    <div v-if="isLoading" class="max-w-7xl mx-auto text-slate-500 animate-pulse">Verifying database records...</div>

    <!-- Main Content Container -->
    <main v-else class="max-w-7xl mx-auto">
      <div class="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl shadow-2xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/80 uppercase text-xs tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="py-4 px-4 sm:px-6 font-semibold">Filename</th>
                <th class="py-4 px-4 sm:px-6 font-semibold">Status</th>
                <th class="py-4 px-4 sm:px-6 hidden md:table-cell font-semibold">Ingested At</th>
                <th class="py-4 px-4 sm:px-6 hidden sm:table-cell font-semibold">SHA-256 Hash</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/50">
              <template v-for="item in evidenceList" :key="item.sha256_hash">
                <tr @click="toggleRow(item.sha256_hash)" class="hover:bg-slate-700/40 cursor-pointer transition-colors bg-slate-800">
                  <td class="py-4 px-4 sm:px-6 font-semibold text-white flex items-center gap-2">
                    <span class="text-xs text-slate-500">{{ expandedHash === item.sha256_hash ? '▼' : '▶' }}</span>
                    {{ item.filename }}
                  </td>
                  <td class="py-4 px-4 sm:px-6">
                    <span :class="{
                      'bg-emerald-500/10 text-emerald-400 border-emerald-500/30': item.status === 'Sealed' || item.status === 'Cryptographically Sealed',
                      'bg-red-500/10 text-red-400 border-red-500/30': item.status.includes('TAMPERED'),
                      'bg-amber-500/10 text-amber-400 border-amber-500/30': item.status.includes('PURGED')
                    }" class="px-2.5 py-1 text-xs font-semibold rounded-full border">
                      {{ item.status }}
                    </span>
                  </td>
                  <td class="py-4 px-4 sm:px-6 text-slate-400 hidden md:table-cell">{{ formatDate(item.ingested_at) }}</td>
                  <td class="py-4 px-4 sm:px-6 font-mono text-xs text-slate-400 hidden sm:table-cell truncate max-w-[200px]" :title="item.sha256_hash">
                    {{ item.sha256_hash.substring(0, 16) }}...
                  </td>
                </tr>

                <!-- Expanded Panel -->
                <tr v-if="expandedHash === item.sha256_hash">
                  <td colspan="4" class="bg-slate-900/50 p-4 sm:p-6 border-y border-slate-700/80">
                    <div class="flex flex-col xl:flex-row justify-between gap-4 mb-6">
                      <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">Forensic Investigation Panel</h3>
                      <div class="flex flex-wrap gap-2">
                        <button @click="openModal('verify', item.sha256_hash)" class="px-3 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 text-xs font-bold rounded shadow-sm transition">
                          {{ isVerifying ? 'Hashing...' : 'Re-Verify Seal' }}
                        </button>
                        <a :href="`http://localhost:8000/api/v1/evidence/${item.sha256_hash}/report`" download class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded shadow-sm transition">
                          Export Court PDF
                        </a>
                        <button @click="openModal('checkout', item.sha256_hash)" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold rounded shadow-sm transition">
                          Checkout (d_DE)
                        </button>
                        <button @click="openModal('checkin', item.sha256_hash)" class="px-3 py-1.5 bg-teal-600/20 hover:bg-teal-600/40 text-teal-400 border border-teal-500/30 text-xs font-bold rounded shadow-sm transition">
                          Return / Check-In
                        </button>
                        <button @click="openModal('purge', item.sha256_hash)" class="px-3 py-1.5 bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-500/30 text-xs font-bold rounded shadow-sm transition">
                          Purge / Warrant Expiry
                        </button>
                      </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <!-- DCoC Timeline -->
                      <div class="bg-slate-800 rounded-lg p-5 border border-slate-700">
                        <h4 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">Digital Chain of Custody</h4>
                        <ol class="relative border-l border-slate-600 ml-2 space-y-4">
                          <li v-for="(event, idx) in custodyEvents" :key="idx" class="ml-4">
                            <div class="absolute w-3 h-3 bg-blue-500 rounded-full mt-1.5 -left-1.5 border border-slate-800"></div>
                            <div class="text-[11px] text-slate-400 font-mono">{{ formatDate(event.timestamp) }} — Location: {{ event.location }}</div>
                            <p class="text-sm font-bold text-slate-200 mt-0.5">Officer ID: {{ event.officer_id }} <span class="text-blue-400 uppercase font-mono ml-1">{{ event.action }}</span></p>
                            <p class="text-xs text-slate-400 bg-slate-900/50 p-2 rounded mt-2 border border-slate-700/50">{{ event.reason }}</p>
                          </li>
                        </ol>
                      </div>

                      <!-- Findings & Topology -->
                      <div class="space-y-4">
                        <h4 class="text-xs font-bold uppercase tracking-widest text-slate-400">Mathematical & Graph Findings</h4>
                        <div v-for="(finding, index) in evidenceFindings" :key="index">
                          <div v-if="finding.type === 'PAGERANK'" class="border border-slate-700 rounded-lg p-6 bg-slate-800 text-center">
                            <h4 class="text-xs font-bold uppercase tracking-widest text-slate-500 mb-6">PageRank Attack Topology</h4>
                            <div class="flex flex-col items-center">
                              <template v-for="(node, nodeIndex) in pageRankGraphData?.nodes" :key="node.id">
                                <div v-if="nodeIndex !== 0" class="w-0.5 h-6 bg-slate-600 my-1"></div>
                                <div class="px-4 py-2 rounded-lg border shadow-sm font-mono text-sm font-bold z-10" :class="node.is_center ? 'border-red-500/50 bg-red-900/20 text-red-400 scale-105' : 'border-slate-600 bg-slate-900 text-slate-300'">
                                  [{{ node.type }}] {{ node.id }}
                                  <span v-if="node.is_center" class="block text-[10px] text-red-500 uppercase mt-1">Center of Gravity</span>
                                </div>
                              </template>
                            </div>
                          </div>
                          <div v-else class="p-4 border-l-4 rounded bg-slate-800 shadow-sm text-sm border-y border-r border-slate-700" :class="finding.status === 'CONFIRMED' ? 'border-l-emerald-500' : 'border-l-red-500'">
                            <div class="flex justify-between items-start gap-4">
                              <span class="font-bold text-slate-200">[{{ finding.type }}] {{ finding.statement }}</span>
                              <span class="text-[10px] font-bold px-2 py-1 rounded whitespace-nowrap" :class="finding.status === 'CONFIRMED' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'">{{ finding.status }}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- UI MODALS (Replacing window.prompt/confirm) -->
    
    <!-- Ingest Modal -->
    <!-- Ingest Modal -->
    <div v-if="activeModal === 'ingest'" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6 shadow-2xl">
        <h2 class="text-xl font-bold mb-4 text-white">Ingest New Evidence</h2>
        <div class="space-y-4 text-sm">
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Select File</label>
            <input type="file" @change="handleFileChange" class="w-full text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-xs file:font-bold file:bg-blue-600 file:text-white hover:file:bg-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Officer Badge ID</label>
            <input type="text" v-model="modalForm.officerId" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Station / Location</label>
            <input type="text" v-model="modalForm.location" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Field Capture Hash (Optional - Offline Sync)</label>
            <input type="text" v-model="modalForm.fieldHash" placeholder="Paste SHA-256 generated at crime scene..." class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white font-mono text-xs focus:outline-none focus:border-blue-500" />
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <button @click="closeModal" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded">Cancel</button>
          <button @click="submitIngest" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded">Seal Evidence</button>
        </div>
      </div>
    </div>

    <!-- Checkout Modal -->
    <div v-if="activeModal === 'checkout'" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6 shadow-2xl">
        <h3 class="text-lg font-bold text-white mb-1">AES-256 Checkout (d_DE)</h3>
        <p class="text-xs text-slate-400 mb-4">Generate an encrypted working copy for safe analysis.</p>
        <div class="space-y-4 text-sm">
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Officer Badge ID</label>
            <input v-model="modalForm.officerId" type="text" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-slate-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Vault / Location</label>
            <input v-model="modalForm.location" type="text" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-slate-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Reason for Checkout</label>
            <input v-model="modalForm.reason" type="text" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-slate-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Encryption Passphrase</label>
            <input v-model="modalForm.encryptionKey" type="password" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-slate-500" />
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <button @click="closeModal" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded">Cancel</button>
          <button @click="submitCheckout" class="px-4 py-2 bg-slate-200 hover:bg-white text-slate-900 text-xs font-bold rounded">Confirm Checkout</button>
        </div>
      </div>
    </div>

    <!-- Check-In Modal -->
    <div v-if="activeModal === 'checkin'" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6 shadow-2xl">
        <h3 class="text-lg font-bold text-white mb-1">Return / Check-In</h3>
        <p class="text-xs text-slate-400 mb-4">Submit encrypted .enc file to trigger the Hash Handshake.</p>
        <div class="space-y-4 text-sm">
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Analyzed File (.enc)</label>
            <input type="file" @change="handleFileChange" class="w-full text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-xs file:font-bold file:bg-teal-600/20 file:text-teal-400 hover:file:bg-teal-600/30" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Officer Badge ID</label>
            <input v-model="modalForm.officerId" type="text" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-teal-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Decryption Passphrase</label>
            <input v-model="modalForm.encryptionKey" type="password" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-teal-500" />
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <button @click="closeModal" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded">Cancel</button>
          <button @click="submitCheckin" class="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold rounded">Verify Handshake</button>
        </div>
      </div>
    </div>

    <!-- Purge Modal -->
    <div v-if="activeModal === 'purge'" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-slate-800 border border-red-500/30 rounded-xl w-full max-w-md p-6 shadow-2xl">
        <h3 class="text-lg font-bold text-red-400 mb-1">Lawful Warrant Purge</h3>
        <p class="text-xs text-slate-400 mb-4">Permanently scrub files and write Neo4j Tombstone.</p>
        <div class="space-y-4 text-sm">
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Authorizing Officer ID</label>
            <input v-model="modalForm.officerId" type="text" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-red-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Court Order / Reason</label>
            <input v-model="modalForm.reason" type="text" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-red-500" />
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <button @click="closeModal" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded">Cancel</button>
          <button @click="submitPurge" class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded">Execute Purge</button>
        </div>
      </div>
    </div>

    <!-- Verify Modal -->
    <div v-if="activeModal === 'verify'" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-slate-800 border border-indigo-500/30 rounded-xl w-full max-w-md p-6 shadow-2xl">
        <h3 class="text-lg font-bold text-indigo-400 mb-1">Verify Cryptographic Seal</h3>
        <div class="space-y-4 text-sm mt-4">
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Officer Badge ID</label>
            <input v-model="modalForm.officerId" type="text" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-indigo-500" />
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <button @click="closeModal" class="px-4 py-2 bg-slate-700 text-white text-xs rounded">Cancel</button>
          <button @click="submitVerify" class="px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded">Re-Hash File</button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="notification.show" class="fixed bottom-4 right-4 z-50 animate-fade-in-up">
      <div class="bg-slate-800 rounded-lg shadow-2xl p-4 w-72 border-l-4" :class="{'border-emerald-500': notification.type === 'success', 'border-red-500': notification.type === 'error', 'border-blue-500': notification.type === 'info', 'border-amber-500': notification.type === 'warning'}">
        <div class="flex justify-between items-start mb-1">
          <h3 class="text-sm font-bold text-white">{{ notification.title }}</h3>
          <button @click="closeNotification" class="text-slate-400 hover:text-white">&times;</button>
        </div>
        <p class="text-xs text-slate-400 leading-relaxed">{{ notification.message }}</p>
      </div>
    </div>
  </div>
</template>

<style>
@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up { animation: fade-in-up 0.3s ease-out; }
</style>
