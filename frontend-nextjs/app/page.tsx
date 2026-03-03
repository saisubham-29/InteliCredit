"use client";

import React, { useState, useEffect, useMemo } from "react";
import Image from "next/image";
import { 
  Upload, 
  Search, 
  FileText, 
  Brain, 
  ShieldCheck, 
  BarChart3, 
  AlertTriangle, 
  CheckCircle2, 
  Download, 
  ExternalLink,
  ChevronRight,
  Loader2,
  Building2,
  Factory,
  MessageSquareText,
  User,
  Lock,
  LogOut,
  TrendingUp,
  PieChart,
  ArrowRight,
  Network
} from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  LineChart, Line, AreaChart, Area, Cell
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

// --- Firebase ---
import { auth, googleProvider } from "../lib/firebase";
import { 
  signInWithPopup,
  onAuthStateChanged, 
  signOut,
  getIdToken,
  User as FirebaseUser
} from "firebase/auth";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const API_BASE = "http://localhost:8000";

// --- Types ---

interface UserProfile {
  email: string;
  name: string;
}

// --- Components ---

const RiskGauge = ({ score }: { score: number }) => {
  const rotation = (score / 100) * 180 - 90;
  return (
    <div className="relative w-full aspect-[2/1] overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 rounded-t-full opacity-20"></div>
      <div className="absolute inset-x-0 bottom-0 h-[20%] bg-white dark:bg-slate-900 z-10"></div>
      <div 
        className="absolute bottom-0 left-1/2 w-1 h-[90%] bg-primary origin-bottom transition-transform duration-1000 ease-out z-20"
        style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
      >
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-primary rounded-full border-4 border-white dark:border-slate-900 shadow-xl"></div>
      </div>
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-center z-30">
        <div className="text-4xl font-black text-primary">{score}</div>
        <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Risk Score</div>
      </div>
    </div>
  );
};

export default function App() {
  const [activeTab, setActiveTab] = useState("analysis");
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [authLoading, setAuthLoading] = useState(false);
  
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [research, setResearch] = useState<any>(null);
  const [explainability, setExplainability] = useState<any>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const fetchCompanies = async () => {
    try {
      const res = await fetch(`${API_BASE}/companies`);
      const data = await res.json();
      setCompanies(Array.isArray(data) ? data : (data.companies || []));
    } catch (err) {
      console.error("Fetch companies failed", err);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user);
      if (user) {
        try {
          const token = await getIdToken(user);
          const verifyRes = await fetch(`${API_BASE}/verify-token`, {
            method: "POST",
            headers: { 
              "Authorization": `Bearer ${token}`,
              "Content-Type": "application/json"
            }
          });
          if (verifyRes.ok) {
            const profileData = await verifyRes.json();
            setProfile(profileData);
            fetchCompanies();
          } else {
            console.error("Token verification failed");
            setProfile(null);
          }
        } catch (err) {
          console.error("Verification error", err);
          setProfile(null);
        }
      } else {
        setProfile(null);
      }
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleGoogleLogin = async () => {
    setAuthLoading(true);
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (err: any) {
      console.error("Google login failed", err);
      alert("Login failed: " + err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    setFirebaseUser(null);
    setProfile(null);
  };

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setActionLoading(true);
    setUploadStatus("Ingesting documents...");
    const formData = new FormData(e.currentTarget);

    try {
      const token = await getIdToken(auth.currentUser!);
      const res = await fetch(`${API_BASE}/upload-documents`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      setUploadStatus("✓ Entity ingested successfully!");
      fetchCompanies();
      setTimeout(() => {
        setUploadStatus("");
        setActiveTab("analysis");
      }, 2000);
    } catch (err: any) {
      setUploadStatus("✗ " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const runAnalysis = async () => {
    if (!selectedCompany) return;
    setActionLoading(true);

    try {
      const token = await getIdToken(auth.currentUser!);
      const res = await fetch(`${API_BASE}/analyze-company`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ company_id: selectedCompany }),
      });
      const data = await res.json();
      setAnalysis(data);

      const researchRes = await fetch(`${API_BASE}/research-details/${selectedCompany}`, {
         headers: { "Authorization": `Bearer ${token}` }
      });
      setResearch(await researchRes.json());

      const explainRes = await fetch(`${API_BASE}/explainability/${selectedCompany}`, {
         headers: { "Authorization": `Bearer ${token}` }
      });
      setExplainability(await explainRes.json());
    } catch (err: any) {
      alert("Analysis failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const radarData = useMemo(() => {
    if (!analysis?.risk_report?.scores) return [];
    return Object.entries(analysis.risk_report.scores).map(([subject, A]) => ({
      subject: subject.charAt(0).toUpperCase() + subject.slice(1),
      A,
      fullMark: 35,
    }));
  }, [analysis]);

  const xaiData = useMemo(() => {
    const explanation = analysis?.risk_report?.recommendation?.ml_explanation;
    if (!explanation?.feature_importances) return [];
    return Object.entries(explanation.feature_importances).map(([name, value]) => ({
      name,
      value: (value as number) * 100
    })).sort((a, b) => b.value - a.value);
  }, [analysis]);

  const tabs = [
    { id: "upload", label: "Ingestion", icon: Upload },
    { id: "analysis", label: "Intelligence", icon: BarChart3 },
    { id: "research", label: "Telemetry", icon: Search },
    { id: "explainability", label: "Neural Logic", icon: Brain },
    { id: "cam", label: "CAM Report", icon: FileText },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
      </div>
    );
  }

  if (!firebaseUser) {
    return (
      <div className="min-h-screen glass flex items-center justify-center p-6 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md glass-card p-10 rounded-[2.5rem] shadow-2xl space-y-8"
        >
          <div className="text-center space-y-2">
            <div className="inline-flex p-4 bg-primary/10 rounded-2xl mb-4">
              <ShieldCheck className="w-10 h-10 text-primary" />
            </div>
            <h1 className="text-3xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-slate-900 to-slate-500 dark:from-white dark:to-slate-400">
              InteliCredit
            </h1>
            <p className="text-muted-foreground font-medium">Enterprise Neural Lending Platform</p>
          </div>

          <div className="space-y-6">
            <button 
              onClick={handleGoogleLogin}
              disabled={authLoading}
              className="w-full py-4 rounded-2xl bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-black text-lg shadow-xl hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center gap-3"
            >
              {authLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  <Image src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" width={24} height={24} />
                  Sign in with Google
                </>
              )}
            </button>
            <p className="text-center text-[10px] text-muted-foreground font-black uppercase tracking-widest leading-relaxed">
              Secure biometric-grade authentication via Firebase Identity Layer.
            </p>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#020617] text-slate-900 dark:text-slate-100 selection:bg-primary selection:text-white">
      {/* Navigation Header */}
      <header className="sticky top-0 z-[60] w-full glass border-b shadow-sm">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4 group cursor-pointer" onClick={() => setActiveTab("analysis")}>
            <div className="p-2.5 bg-primary rounded-xl shadow-lg shadow-primary/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tighter leading-none">INTELICREDIT</h1>
              <span className="text-[10px] font-bold text-primary tracking-[0.2em] uppercase">Secured Intelligence</span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] font-black uppercase tracking-widest">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              Neural Pipeline Active
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-black uppercase text-primary">{profile?.name || firebaseUser.displayName}</div>
                <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">{profile?.email || firebaseUser.email}</div>
              </div>
              <button 
                onClick={handleLogout}
                className="p-2.5 rounded-xl hover:bg-rose-500/10 text-slate-400 hover:text-rose-500 transition-all border border-transparent hover:border-rose-500/20"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-[1600px] mx-auto px-6 py-8 flex flex-col lg:flex-row gap-10">
        {/* Workspace Sidebar */}
        <aside className="lg:w-72 space-y-4">
          <div className="p-1 space-y-1 bg-white dark:bg-slate-900/50 rounded-2xl border shadow-sm">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-4 py-3.5 rounded-xl text-sm font-bold transition-all",
                  activeTab === tab.id
                    ? "bg-primary text-white shadow-lg shadow-primary/20"
                    : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                )}
              >
                <tab.icon className={cn("w-5 h-5", activeTab === tab.id ? "text-white" : "text-slate-400")} />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Quick Selection Card */}
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">Active Selection</h3>
            <div className="relative">
              <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border text-sm font-bold outline-none focus:ring-2 focus:ring-primary transition-all appearance-none"
              >
                <option value="">Choose entity...</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <button 
              onClick={runAnalysis}
              disabled={!selectedCompany || actionLoading}
              className="w-full py-3.5 rounded-xl bg-slate-900 dark:bg-white dark:text-slate-950 text-white text-xs font-black uppercase tracking-widest hover:opacity-90 disabled:opacity-20 transition-all"
            >
              Execute Intel
            </button>
          </div>
        </aside>

        {/* Neural Workspace */}
        <main className="flex-1 min-w-0 space-y-10 pb-20">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === "upload" && (
                <div className="max-w-3xl mx-auto">
                  <div className="glass-card rounded-[2rem] p-10 flex flex-col md:flex-row gap-12">
                    <div className="flex-1 space-y-8">
                      <div className="space-y-2">
                        <h2 className="text-3xl font-black tracking-tight">Data Ingestion</h2>
                        <p className="text-muted-foreground text-sm font-medium leading-relaxed">Pillar 1: Deterministic financial extraction and real-time fraud pattern detection gateway.</p>
                      </div>

                      <form onSubmit={handleUpload} className="space-y-6">
                        <div className="grid grid-cols-2 gap-4">
                          <input name="company_name" placeholder="Entity Name" required className="col-span-2 w-full px-5 py-4 rounded-2xl bg-slate-50 dark:bg-slate-900 border outline-none focus:ring-2 focus:ring-primary font-bold" />
                          <input name="pan" placeholder="PAN/GSTIN" className="w-full px-5 py-4 rounded-2xl bg-slate-50 dark:bg-slate-900 border outline-none focus:ring-2 focus:ring-primary font-bold" />
                          <select name="sector" required className="w-full px-5 py-4 rounded-2xl bg-slate-50 dark:bg-slate-900 border outline-none focus:ring-2 focus:ring-primary font-bold appearance-none">
                            <option value="manufacturing">Manufacturing</option>
                            <option value="infrastructure">Infrastructure</option>
                            <option value="pharma">Pharma</option>
                            <option value="retail">Retail/Services</option>
                          </select>
                        </div>
                        
                        <div className="relative group">
                          <input type="file" name="files" multiple required className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                          <div className="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-3xl p-12 text-center group-hover:border-primary/50 group-hover:bg-primary/5 transition-all">
                            <Upload className="w-10 h-10 text-primary/30 mx-auto mb-4 group-hover:scale-110 transition-transform" />
                            <p className="text-sm font-black uppercase tracking-widest text-slate-400">Drag Digital Assets Here</p>
                            <p className="text-xs text-muted-foreground mt-2 font-medium">Bank Statements, GSTR, Annual Reports (PDF/CSV)</p>
                          </div>
                        </div>

                        <button className="w-full py-5 rounded-2xl bg-primary text-white font-black text-lg shadow-2xl shadow-primary/30 flex items-center justify-center gap-3 active:scale-95 transition-all">
                          {actionLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <ShieldCheck className="w-6 h-6" />}
                          Initialize Neural Scan
                        </button>
                        {uploadStatus && <div className="text-center text-sm font-black text-emerald-500 uppercase tracking-widest animate-pulse">{uploadStatus}</div>}
                      </form>
                    </div>

                    <div className="md:w-64 space-y-6">
                      <div className="p-6 rounded-3xl bg-primary/5 border border-primary/10">
                        <TrendingUp className="w-8 h-8 text-primary mb-4" />
                        <h4 className="text-sm font-black uppercase mb-1">Pillar 1 Strength</h4>
                        <p className="text-xs text-muted-foreground leading-relaxed">Deterministic extraction ensures zero-hallucination metrics for audit-grade accuracy.</p>
                      </div>
                      <div className="p-6 rounded-3xl bg-amber-500/5 border border-amber-500/10">
                        <AlertTriangle className="w-8 h-8 text-amber-500 mb-4" />
                        <h4 className="text-sm font-black uppercase mb-1">Fraud Guard</h4>
                        <p className="text-xs text-muted-foreground leading-relaxed">Real-time GSTR-2A vs 3B mismatch detection integrated.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "analysis" && (
                <div className="space-y-10">
                  {!analysis ? (
                    <div className="glass-card p-20 rounded-[3rem] text-center space-y-4">
                      <div className="relative w-32 h-32 mx-auto">
                        <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full"></div>
                        <Brain className="relative w-full h-full text-primary opacity-20 animate-pulse" />
                      </div>
                      <h2 className="text-2xl font-black text-slate-400 uppercase tracking-widest">Neural Cluster Idle</h2>
                      <p className="text-muted-foreground font-medium">Select an entity from target list to initiate risk mapping.</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-8 ring-offset-4 ring-slate-100">
                      
                      {/* Left: Global Risk Score */}
                      <div className="md:col-span-4 glass-card p-10 rounded-[2.5rem] flex flex-col justify-between items-center text-center">
                        <div className="w-full">
                          <div className="flex items-center justify-between mb-8">
                             <h3 className="text-sm font-black uppercase tracking-widest text-slate-400">Risk Assessment</h3>
                             <div className={cn(
                               "px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm",
                               analysis.risk_report.total_score < 40 ? "bg-emerald-500 text-white" : analysis.risk_report.total_score < 70 ? "bg-amber-500 text-white" : "bg-rose-500 text-white"
                             )}>
                               {analysis.risk_report.risk_band} RISK
                             </div>
                          </div>
                          
                          <RiskGauge score={analysis.risk_report.total_score} />
                          
                          <div className="mt-10 p-6 rounded-2xl bg-slate-50 dark:bg-slate-900 border">
                            <div className="text-[10px] font-black uppercase tracking-tighter text-slate-400 mb-4">5Cs Compositional Radar</div>
                            <div className="w-full h-[250px]">
                              <ResponsiveContainer width="100%" height="100%">
                                <RadarChart data={radarData}>
                                  <PolarGrid stroke="#94a3b8" strokeOpacity={0.2} />
                                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 800 }} />
                                  <Radar name="Scoring" dataKey="A" stroke="#2563eb" fill="#2563eb" fillOpacity={0.5} />
                                </RadarChart>
                              </ResponsiveContainer>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Right: ML Recommendation & Rationale */}
                      <div className="md:col-span-8 flex flex-col gap-8">
                        <div className="bg-slate-900 dark:bg-primary/10 text-white rounded-[2.5rem] p-10 shadow-2xl overflow-hidden relative border border-white/5">
                          <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-primary/50 to-transparent opacity-30"></div>
                          
                          <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-10">
                            <div className="space-y-6">
                               <div className="flex items-center gap-3 text-primary-foreground">
                                 <Brain className="w-8 h-8" />
                                 <h3 className="text-2xl font-black tracking-tight uppercase">Neural Recommendation</h3>
                               </div>
                               
                               <div className="space-y-2">
                                 <div className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-300/60">System Decision</div>
                                 <div className={cn(
                                   "text-6xl font-black transition-all",
                                   analysis.risk_report.recommendation.decision_tag.includes("Approve") ? "text-emerald-400" : "text-rose-400"
                                 )}>
                                   {analysis.risk_report.recommendation.decision_tag}
                                 </div>
                               </div>

                               <p className="text-blue-100/70 text-sm leading-relaxed font-medium">
                                 {analysis.risk_report.recommendation.rationale}
                                </p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                               <div className="glass-card bg-white/5 p-6 rounded-3xl border-white/10 flex flex-col justify-between">
                                  <div className="text-[10px] font-black uppercase tracking-widest text-blue-300/50">Risk Grade</div>
                                  <div className="text-5xl font-black text-white">{analysis.risk_report.recommendation.risk_grade}</div>
                               </div>
                               <div className="glass-card bg-white/5 p-6 rounded-3xl border-white/10 flex flex-col justify-between">
                                  <div className="text-[10px] font-black uppercase tracking-widest text-blue-300/50">Interest Rate</div>
                                  <div className="text-4xl font-black text-blue-400">{analysis.risk_report.recommendation.interest_rate}%</div>
                               </div>
                               <div className="glass-card bg-white/5 p-6 rounded-3xl border-white/10 col-span-2 flex items-center justify-between">
                                  <div>
                                    <div className="text-[10px] font-black uppercase tracking-widest text-blue-300/50">Rec. Limit (cr)</div>
                                    <div className="text-2xl font-black text-white">₹ {analysis.risk_report.recommendation.eligible_amount} Cr</div>
                                  </div>
                                  <div className="text-right">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-blue-300/50">PD</div>
                                    <div className="text-xl font-bold text-emerald-400">{(analysis.risk_report.recommendation.probability_of_default * 100).toFixed(2)}%</div>
                                  </div>
                               </div>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                          {/* Critical Risk Drivers */}
                          <div className="glass-card p-10 rounded-[2.5rem]">
                             <h3 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-8 flex items-center gap-2">
                               <AlertTriangle className="w-4 h-4 text-amber-500" /> Executive Risk Drivers
                             </h3>
                             <div className="grid grid-cols-1 gap-4">
                               {analysis.risk_report.drivers.slice(0, 4).map((driver: string, i: number) => (
                                 <div key={i} className="flex gap-4 p-5 rounded-2xl bg-white dark:bg-slate-900 border hover:border-primary/50 transition-all group">
                                   <div className="w-1.5 h-auto bg-primary/20 rounded-full group-hover:bg-primary transition-colors"></div>
                                   <div className="text-xs font-bold leading-relaxed">{driver}</div>
                                 </div>
                               ))}
                             </div>
                          </div>

                          {/* GNN Fraud Signals */}
                          <div className="glass-card p-10 rounded-[2.5rem] border-rose-500/20">
                             <h3 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-8 flex items-center gap-2">
                               <Network className="w-4 h-4 text-rose-500" /> Fraud Network Analysis
                             </h3>
                             <div className="space-y-6">
                                <div className="flex items-center justify-between p-6 rounded-2xl bg-rose-500/5 border border-rose-500/10">
                                   <div>
                                      <div className="text-[10px] font-black uppercase text-rose-500 mb-1">GNN Risk Score</div>
                                      <div className="text-4xl font-black">{analysis.risk_report.fraud_analysis?.fraud_risk_score || "0.0"}</div>
                                   </div>
                                   <div className={cn(
                                     "px-3 py-1 rounded text-[10px] font-black uppercase",
                                     analysis.risk_report.fraud_analysis?.fraud_level === 'High' ? "bg-rose-500 text-white" : "bg-emerald-500 text-white"
                                   )}>
                                      {analysis.risk_report.fraud_analysis?.fraud_level || "LOW"} RISK
                                   </div>
                                </div>
                                <div className="space-y-3">
                                   <div className="text-[10px] font-black uppercase text-slate-400">Detected Patterns</div>
                                   <div className="flex flex-wrap gap-2">
                                      {analysis.risk_report.fraud_analysis?.detected_patterns?.length > 0 ? (
                                        analysis.risk_report.fraud_analysis.detected_patterns.map((p: string) => (
                                          <span key={p} className="px-3 py-1 bg-rose-500/10 text-rose-500 text-[10px] font-bold rounded-lg border border-rose-500/20">{p}</span>
                                        ))
                                      ) : (
                                        <span className="text-xs font-medium text-slate-400italic">No suspicious patterns detected in network.</span>
                                      )}
                                   </div>
                                </div>
                             </div>
                          </div>
                        </div>
                      </div>

                    </div>
                  )}
                </div>
              )}

              {activeTab === "research" && (
                <div className="space-y-10">
                  {!research ? (
                    <div className="glass-card p-20 rounded-[3rem] text-center border shadow-lg">
                      <Search className="w-16 h-16 text-slate-200 mx-auto mb-4 animate-pulse" />
                      <p className="text-slate-400 font-bold uppercase tracking-widest">Awaiting Entity Telemetry</p>
                    </div>
                  ) : (
                    <div className="space-y-10 max-w-6xl mx-auto">
                      {/* Sentiment & Sector Vision */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                         <div className="glass-card p-8 rounded-[2rem] space-y-4">
                            <div className="text-xs font-black uppercase tracking-widest text-slate-400">Sentiment Engine</div>
                            <div className="flex items-center gap-6">
                               <div className="text-5xl font-black text-primary">{(research.news_hits?.filter((n:any) => n.sentiment === 'Positive').length / (research.news_hits?.length || 1) * 100).toFixed(0)}%</div>
                               <div className="text-[10px] font-bold text-emerald-500 leading-tight">POSITIVE NEWS<br/>DENSITY</div>
                            </div>
                            <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                               <div className="h-full bg-emerald-500" style={{ width: `${(research.news_hits?.filter((n:any) => n.sentiment === 'Positive').length / (research.news_hits?.length || 1) * 100)}%` }} />
                            </div>
                         </div>
                         <div className="md:col-span-2 glass-card p-8 rounded-[2rem] flex flex-col justify-center">
                            <h4 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
                              <TrendingUp className="w-4 h-4" /> Sector Outlook
                            </h4>
                            <p className="text-xl font-bold leading-relaxed italic text-slate-700 dark:text-slate-300">&ldquo;{research.sector_outlook}&rdquo;</p>
                         </div>
                      </div>

                      {/* Targeted Risk Tags */}
                      <div className="flex flex-wrap gap-3">
                        {research.risk_tags?.map((tag: string) => (
                          <div key={tag} className="px-6 py-2.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-500 text-[10px] font-black uppercase tracking-widest">
                            🚨 {tag} Risk Detected
                          </div>
                        ))}
                      </div>

                      {/* Intelligence Stream */}
                      <div className="space-y-6">
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-400 flex items-center gap-2">
                          <MessageSquareText className="w-4 h-4 text-primary" /> Telemetry Feed
                        </h3>
                        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                          {research.news_hits?.map((news: any, i: number) => (
                            <motion.div 
                              whileHover={{ y: -5 }}
                              key={i} 
                              className="glass-card p-8 rounded-[2rem] border-l-4 border-l-primary group"
                            >
                               <div className="flex justify-between items-start gap-6 mb-4">
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                       <span className={cn(
                                         "px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest",
                                         news.sentiment === 'Positive' ? "bg-emerald-500 text-white" : "bg-rose-500 text-white"
                                       )}>{news.sentiment}</span>
                                       <span className="text-[10px] font-bold text-slate-400">{new Date(news.date).toLocaleDateString()}</span>
                                    </div>
                                    <h4 className="text-lg font-bold leading-tight group-hover:text-primary transition-colors underline decoration-slate-200 underline-offset-4">{news.title}</h4>
                                  </div>
                                  <a href={news.source} target="_blank" className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border-none opacity-0 group-hover:opacity-100 transition-all">
                                    <ExternalLink className="w-4 h-4" />
                                  </a>
                               </div>
                               <p className="text-sm text-muted-foreground font-medium leading-relaxed">{news.snippet}</p>
                               <div className="mt-4 flex flex-wrap gap-2">
                                  {news.risk_keywords?.map((k: string) => (
                                    <span key={k} className="text-[9px] font-black text-rose-500 uppercase tracking-tighter">#{k}</span>
                                  ))}
                               </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "explainability" && (
                <div className="max-w-6xl mx-auto space-y-10">
                  {analysis?.risk_report?.recommendation?.ml_explanation ? (
                    <div className="space-y-10">
                       <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                          {/* Feature Importances Chart */}
                          <div className="lg:col-span-7 glass-card p-10 rounded-[2.5rem]">
                             <h3 className="text-sm font-black uppercase tracking-[0.2em] text-slate-400 mb-8 flex items-center gap-3">
                                <Brain className="w-5 h-5 text-primary" /> Model Feature Attribution
                             </h3>
                             <div className="w-full h-[400px]">
                                <ResponsiveContainer width="100%" height="100%">
                                   <BarChart data={xaiData} layout="vertical" margin={{ left: 20, right: 30 }}>
                                      <CartesianGrid strokeDasharray="3 3" horizontal={false} strokeOpacity={0.1} />
                                      <XAxis type="number" hide />
                                      <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 10, fontWeight: 800, fill: '#64748b' }} axisLine={false} tickLine={false} />
                                      <Tooltip 
                                        cursor={{ fill: 'transparent' }}
                                        contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px', color: '#fff' }}
                                        formatter={(val: number) => [`${val.toFixed(1)}%`, 'Contribution']}
                                      />
                                      <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                                        {xaiData.map((entry, index) => (
                                          <Cell key={`cell-${index}`} fill={index < 3 ? '#2563eb' : '#94a3b8'} fillOpacity={0.8 - (index * 0.1)} />
                                        ))}
                                      </Bar>
                                   </BarChart>
                                </ResponsiveContainer>
                             </div>
                             <p className="text-[10px] text-muted-foreground mt-4 italic">This chart represents the weighted influence of each financial cluster on the Probability of Default (PD) calculation using Gradient Boosting Regressor feature importance.</p>
                          </div>

                          {/* Key Risk Drivers (ML) */}
                          <div className="lg:col-span-5 space-y-6">
                             <div className="glass-card p-10 rounded-[2.5rem] bg-primary/5 border-primary/20">
                                <h3 className="text-sm font-black uppercase tracking-widest text-primary mb-6">Neural Risk Drivers</h3>
                                <div className="space-y-4">
                                   {analysis.risk_report.recommendation.ml_explanation.key_drivers.map((driver: string, i: number) => (
                                     <div key={i} className="p-5 rounded-2xl bg-white dark:bg-slate-900 border-2 border-rose-500/20 flex gap-4 items-start shadow-sm">
                                        <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0" />
                                        <div className="text-sm font-bold leading-tight">{driver}</div>
                                     </div>
                                   ))}
                                </div>
                             </div>

                             <div className="glass-card p-8 rounded-[2.5rem] flex items-center gap-6">
                                <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                                   <ShieldCheck className="w-8 h-8 text-emerald-500" />
                                </div>
                                <div>
                                   <div className="text-[10px] font-black uppercase text-emerald-500">ML Model Confidence</div>
                                   <div className="text-2xl font-black">{((analysis.risk_report.recommendation.ml_confidence || 0.85) * 100).toFixed(1)}%</div>
                                </div>
                             </div>
                          </div>
                       </div>

                       {/* Traditional 5Cs Breakdown (Still shown as detail) */}
                       <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                          {Object.entries(analysis.risk_report.component_details || {}).map(([key, data]: [string, any]) => (
                            <div key={key} className="glass-card p-6 rounded-2xl border hover:border-primary transition-all">
                               <div className="text-[10px] font-black uppercase text-slate-400 mb-2">{key}</div>
                               <div className="text-xl font-black">{data.score.toFixed(1)}</div>
                               <div className="text-[9px] font-medium text-muted-foreground mt-1 line-clamp-2">{data.reason}</div>
                            </div>
                          ))}
                       </div>
                    </div>
                  ) : (
                    <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
                       {Object.entries(analysis?.risk_report?.component_details || {}).map(([key, data]: [string, any]) => (
                         <div key={key} className="glass-card p-8 rounded-[2.5rem] border hover:border-primary transition-all relative overflow-hidden group">
                            <div className="relative z-10 space-y-6">
                               <div className="flex items-center justify-between">
                                  <h3 className="text-lg font-black uppercase tracking-widest text-primary">{key}</h3>
                                  <div className="text-3xl font-black text-slate-900 dark:text-white">{data.score.toFixed(1)}</div>
                                </div>
                               <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800 border">
                                  <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-2">Neural Reason</div>
                                  <p className="text-sm font-bold leading-relaxed">{data.reason}</p>
                               </div>
                            </div>
                         </div>
                       ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === "cam" && (
                <div className="max-w-3xl mx-auto">
                   {selectedCompany ? (
                     <motion.div 
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="glass-card p-12 rounded-[3.5rem] text-center border-2 border-slate-100 dark:border-slate-800 shadow-[0_32px_128px_-16px_rgba(0,0,0,0.1)] relative overflow-hidden"
                     >
                        <div className="absolute inset-0 bg-gradient-to-tr from-rose-500/5 via-transparent to-transparent"></div>
                        <div className="relative z-10 w-24 h-24 bg-rose-500/10 rounded-full flex items-center justify-center mx-auto mb-10 border border-rose-500/20">
                          <FileText className="w-10 h-10 text-rose-500" />
                        </div>
                        <h2 className="text-4xl font-black tracking-tighter mb-4">Credit Memorandum</h2>
                        <p className="max-w-xs mx-auto text-muted-foreground text-sm font-medium mb-10 leading-relaxed">
                          Pillar 3 output: 10-page deep-audit PDF dossier generated with Indian context sensitivity and legal-grade formatting.
                        </p>
                        
                        <a 
                          href={`${API_BASE}/download-cam/${selectedCompany}`}
                          download 
                          className="inline-flex items-center gap-4 bg-slate-900 dark:bg-white text-white dark:text-slate-950 px-12 py-5 rounded-[2rem] font-black text-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all shadow-xl"
                        >
                          <Download className="w-6 h-6" />
                          DOWNLOAD CAM
                        </a>

                        <div className="mt-12 flex items-center justify-center gap-10 border-t pt-10 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                           <div className="flex items-center gap-2"><Lock className="w-3.5 h-3.5" /> SECURED DATA</div>
                           <div className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5" /> AUDIT READY</div>
                        </div>
                     </motion.div>
                   ) : (
                     <div className="glass-card p-20 rounded-[3rem] text-center opacity-30">
                        <FileText className="w-16 h-16 mx-auto mb-4" />
                        <p className="font-bold uppercase tracking-widest">Select entity to compile dossier</p>
                     </div>
                   )}
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Synthesis Interaction */}
      <AnimatePresence>
        {actionLoading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] glass flex items-center justify-center"
          >
            <div className="glass-card p-12 rounded-[3.5rem] shadow-2xl border text-center space-y-6 max-w-sm w-full">
               <div className="relative w-20 h-20 mx-auto">
                 <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
                 <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                 <Brain className="absolute inset-0 m-auto w-8 h-8 text-primary animate-pulse" />
               </div>
               <div className="space-y-2">
                <h4 className="text-xl font-black tracking-tight uppercase">Neural Synthesis</h4>
                <p className="text-xs text-muted-foreground font-black uppercase tracking-[0.2em] animate-pulse">Running PD & 5Cs Cluster Analysis...</p>
               </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
