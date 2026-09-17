<template>
  <div class="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-blue-500 selection:text-white">
    <!-- Navbar -->
    <nav class="container mx-auto px-6 py-5 flex justify-between items-center border-b border-slate-800/80">
      <div class="flex items-center gap-3">
        <svg class="w-5 h-5 text-emerald-600 group-hover:text-emerald-400 transition-colors duration-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        <span class="text-2xl tracking-tighter text-blue-700">S
  <span class="font-light text-slate-500">I</span><span class="text-emerald-500 ml-0.5 animate-pulse">FT</span><span class="text-blue-700 text-3xl leading-none">.</span>
</span>
<!-- <span class="text-2xl font-mono font-bold tracking-tight text-white flex items-center">
  _<span class="text-emerald-500 ml-0.5 animate-pulse">SIFT</span>
</span> -->
          
      </div>
      <div class="flex items-center gap-6">
        <a href="#capabilities" class="hidden md:inline-block text-sm text-slate-400 hover:text-white transition-colors">Capabilities</a>
        <a href="#architecture" class="hidden md:inline-block text-sm text-slate-400 hover:text-white transition-colors">Architecture</a>
        <a href="#compliance" class="hidden md:inline-block text-sm text-slate-400 hover:text-white transition-colors">Compliance</a>
        <router-link to="/dashboard" class="px-5 py-2.5 text-sm font-semibold text-white bg-blue-800 rounded-lg hover:bg-emerald-500 shadow-md shadow-blue-600/20 transition-all">
          Launch Workspace
        </router-link>
      </div>
    </nav>

    <!-- Navbar -->
    

    <!-- Hero Section -->
    <header class="container mx-auto px-6 pt-20 pb-24 text-center relative overflow-hidden">
      <!-- Glow effect -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-blue-600/15 blur-[120px] rounded-full pointer-events-none"></div>

      <div class="relative z-10">
        <div class="inline-flex items-center gap-2 mb-6 px-3.5 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-semibold tracking-wide uppercase">
          <span class="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
          ISO 27037-Compliant Digital Forensic Vault
        </div>

        <h1 class="text-5xl md:text-7xl font-extrabold text-white tracking-tight mb-8 leading-tight">
        Securing the Future of <br/>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
          Digital Evidence in Nigeria.
        </span>
      </h1>

        <p class="max-w-3xl mx-auto text-lg md:text-xl text-slate-400 mb-10 leading-relaxed font-normal">
          SIFT replaces vulnerable flash drives and manual spreadsheets with an immutable, cryptographically sealed chain-of-custody platform. By leveraging AES-256 encryption and Neo4j graph ledgering, SIFT eliminates evidence tampering and restores civic trust in digital investigations.
        </p>

        <div class="flex flex-col sm:flex-row justify-center items-center gap-4">
          <router-link to="/dashboard" class="w-full sm:w-auto px-8 py-4 text-base font-bold text-white bg-emerald-600 rounded-xl hover:bg-blue-500 shadow-xl shadow-blue-600/25 transition-all flex items-center justify-center gap-2">
            Enter Forensic Vault
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </router-link>
          <a href="#capabilities" class="w-full sm:w-auto px-8 py-4 text-base font-semibold text-slate-300 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 transition-all">
            Explore Features
          </a>
        </div>
      </div>
    </header>

    <!-- Metrics / Proof Bar -->
    <section class="border-y border-slate-800/80 bg-slate-900/40 py-8">
      <div class="container mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        <div>
          <div class="text-2xl font-bold text-white font-mono">SHA-256</div>
          <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Root Evidence Baseline</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-blue-400 font-mono">AES-256</div>
          <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Working Copy Confidentiality</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-emerald-400 font-mono">Graph Ledger</div>
          <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Neo4j Chain-of-Custody</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-purple-400 font-mono">ISO 27037</div>
          <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Court-Ready PDF Export</div>
        </div>
      </div>
    </section>

    <!-- Product Capabilities Grid -->
    <section id="capabilities" class="py-24 relative">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-extrabold text-white mb-4 tracking-tight">Engineered for Forensic Rigor</h2>
          <p class="text-slate-400 max-w-2xl mx-auto">Complete custody management built to satisfy strict evidentiary standards across civil, criminal, and enterprise security audits.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <!-- Capability 1 -->
          <div class="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-blue-500/50 transition-all group">
            <div class="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-6 text-blue-400 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Immutable Vaulting & Handoffs</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              Master evidence is permanently sealed upon intake. SIFT generates AES-256 encrypted working copies for examiner checkout, enforcing strict badge ID authorization and automatic spoliation detection.
            </p>
          </div>

          <!-- Capability 2 -->
          <div class="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-emerald-500/50 transition-all group">
            <div class="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6 text-emerald-400 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Algorithmic Forensic Engines</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              Equipped with a Temporal Sequence Engine to flag clock manipulation or timestomping in log events, alongside NetworkX PageRank analytics to pinpoint attack vectors and threat centers of gravity.
            </p>
          </div>

          <!-- Capability 3 -->
          <div class="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-purple-500/50 transition-all group">
            <div class="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-6 text-purple-400 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Court Dossiers & Lawful Purges</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              Compiles court-admissible PDF reports containing cryptographic proof trees. When warrants expire, SIFT executes NDPR-compliant purges, scrubbing raw binaries while retaining immutable Tombstone records.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Enterprise Target Audience -->
    <section id="architecture" class="py-20 border-t border-slate-800/80 bg-slate-900/30">
      <div class="container mx-auto px-6">
        <div class="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-3xl p-8 md:p-12 relative overflow-hidden">
          <div class="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div class="space-y-4">
              <span class="text-xs font-bold text-blue-400 uppercase tracking-widest">Built For Technical Investigations</span>
              <h3 class="text-2xl md:text-3xl font-bold text-white">Deployable for DFIR Teams, Legal Tech & Law Enforcement</h3>
              <p class="text-slate-400 text-sm leading-relaxed max-w-xl">
                Whether managing digital evidence for corporate incident response, regulatory compliance audits, or law enforcement custody logs, SIFT ensures every digital artifact remains untampered and court-admissible.
              </p>
            </div>
            <router-link to="/dashboard" class="shrink-0 px-6 py-3.5 font-bold text-slate-900 bg-white rounded-xl hover:bg-slate-200 transition-all text-sm">
              Launch Live App
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500">
      <div class="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>SIFT  Secure Immutable Forensic Tracking</div>
        <div>Built with Vue 3, FastAPI & Neo4j Graph Database</div>
      </div>
    </footer>
  </div>
</template>
