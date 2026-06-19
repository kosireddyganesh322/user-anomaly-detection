import { useState, useEffect, useRef } from "react";
import { 
  Database, 
  Upload, 
  Trash2, 
  Play, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  Info,
  Loader2,
  RefreshCw,
  FileSpreadsheet
} from "lucide-react";
import { datasetsApi } from "../services/api";

interface Dataset {
  name: string;
  upload_date: string;
  total_users: number;
  total_records: number;
  status: string;
  departments?: number;
  date_range?: string;
  missing_values_count?: number;
  data_quality_score?: number;
  progress?: number;
  current_step?: string;
  error?: string;
}

export default function DatasetManager() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [activeDataset, setActiveDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [datasetName, setDatasetName] = useState("");
  
  // File states
  const [usersFile, setUsersFile] = useState<File | null>(null);
  const [logonFile, setLogonFile] = useState<File | null>(null);
  const [deviceFile, setDeviceFile] = useState<File | null>(null);
  const [ldapFile, setLdapFile] = useState<File | null>(null);

  // Validation state
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [validating, setValidating] = useState(false);

  // Guidance Modal state
  const [showGuidance, setShowGuidance] = useState(false);

  // Active processing state for polling
  const [processingDataset, setProcessingDataset] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<any>(null);

  const pollInterval = useRef<any>(null);

  const fetchDatasets = async () => {
    try {
      const res = await datasetsApi.list();
      setDatasets(res.data || []);
      
      const activeRes = await datasetsApi.getActive();
      setActiveDataset(activeRes.data || null);

      // Check if any dataset is currently processing
      const processing = (res.data || []).find((d: Dataset) => d.status === "Processing");
      if (processing) {
        setProcessingDataset(processing.name);
      }
    } catch (err) {
      console.error("Failed to load datasets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
    return () => {
      if (pollInterval.current) clearInterval(pollInterval.current);
    };
  }, []);

  // Poll for status if a dataset is processing
  useEffect(() => {
    if (processingDataset) {
      if (pollInterval.current) clearInterval(pollInterval.current);
      
      const checkStatus = async () => {
        try {
          const res = await datasetsApi.getStatus(processingDataset);
          setProcessingStatus(res.data);
          if (res.data.status !== "Processing") {
            setProcessingDataset(null);
            setProcessingStatus(null);
            fetchDatasets();
            // Trigger global refresh so that other pages (navbar etc.) update
            window.dispatchEvent(new Event("refresh-data"));
          }
        } catch (err) {
          console.error("Error checking job status:", err);
        }
      };

      checkStatus();
      pollInterval.current = setInterval(checkStatus, 2000);
    } else {
      if (pollInterval.current) {
        clearInterval(pollInterval.current);
        pollInterval.current = null;
      }
    }
  }, [processingDataset]);

  const handleSwitchDataset = async (name: string) => {
    try {
      setLoading(true);
      await datasetsApi.switch(name);
      await fetchDatasets();
      // Notify navigation & page contexts
      window.dispatchEvent(new Event("refresh-data"));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to switch dataset");
    } finally {
      setLoading(false);
    }
  };

  const handleReprocess = async (name: string) => {
    try {
      await datasetsApi.reprocess(name);
      setProcessingDataset(name);
      fetchDatasets();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to trigger reprocessing");
    }
  };

  const handleDelete = async (name: string) => {
    if (!window.confirm(`Are you sure you want to delete dataset '${name}'? This cannot be undone.`)) {
      return;
    }
    try {
      await datasetsApi.delete(name);
      fetchDatasets();
      // In case we deleted the active one and got switched back to CERT
      window.dispatchEvent(new Event("refresh-data"));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to delete dataset");
    }
  };

  const handleValidate = async () => {
    if (!usersFile || !logonFile || !deviceFile || !ldapFile) {
      setValidationError("Please select all 4 required CSV files before validating.");
      return;
    }
    setValidationError(null);
    setValidationResult(null);
    setValidating(true);

    const formData = new FormData();
    formData.append("users", usersFile);
    formData.append("logon", logonFile);
    formData.append("device", deviceFile);
    formData.append("ldap", ldapFile);

    try {
      const res = await datasetsApi.validate(formData);
      setValidationResult(res.data);
    } catch (err: any) {
      setValidationError(err.response?.data?.detail || "Failed to perform validation.");
    } finally {
      setValidating(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!datasetName.trim()) {
      alert("Please enter a valid dataset name.");
      return;
    }
    if (!usersFile || !logonFile || !deviceFile || !ldapFile) {
      alert("All four CSV files are required.");
      return;
    }

    setUploading(true);
    setValidationError(null);
    setValidationResult(null);

    const formData = new FormData();
    formData.append("name", datasetName.trim());
    formData.append("users", usersFile);
    formData.append("logon", logonFile);
    formData.append("device", deviceFile);
    formData.append("ldap", ldapFile);

    try {
      const res = await datasetsApi.upload(formData);
      if (res.data.success) {
        setProcessingDataset(datasetName.trim());
        setDatasetName("");
        setUsersFile(null);
        setLogonFile(null);
        setDeviceFile(null);
        setLdapFile(null);
        fetchDatasets();
      } else {
        setValidationResult(res.data.details);
        setValidationError("Upload rejected due to schema validation failures.");
      }
    } catch (err: any) {
      setValidationError(err.response?.data?.detail || "Ingestion request failed.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-3">
            <Database className="text-brand-500" size={26} />
            Data Sources & Ingestion
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Manage organizational telemetry sources, upload custom audits, and reprocess ML ingestion pipes.
          </p>
        </div>
        <button
          onClick={() => setShowGuidance(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm rounded-lg transition-colors border border-gray-700"
        >
          <Info size={16} />
          Requirements Guide
        </button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Columns (Active Stats & Switcher) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Current Active Dataset */}
          {activeDataset && (
            <div className="bg-gray-900 border border-gray-850 rounded-xl p-5 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-brand-500/10 text-brand-400 text-[10px] font-extrabold px-3 py-1.5 rounded-bl-lg border-l border-b border-gray-800/40 uppercase tracking-widest">
                Active Source
              </div>
              <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Current Dataset</h2>
              <div className="text-2xl font-extrabold text-white mt-1 flex items-center gap-2">
                {activeDataset.name}
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-safe/10 text-safe border border-safe/25">
                  Ready
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-5 pt-5 border-t border-gray-800/50">
                <div>
                  <span className="text-xs text-gray-500 block">Total Users</span>
                  <span className="text-lg font-bold text-gray-200 mt-0.5 block">{activeDataset.total_users?.toLocaleString() || "0"}</span>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Total Records</span>
                  <span className="text-lg font-bold text-gray-200 mt-0.5 block">{activeDataset.total_records?.toLocaleString() || "0"}</span>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Date Range</span>
                  <span className="text-xs font-semibold text-gray-300 mt-1 block truncate" title={activeDataset.date_range}>
                    {activeDataset.date_range || "N/A"}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Data Quality</span>
                  <span className={`text-lg font-bold mt-0.5 block ${
                    (activeDataset.data_quality_score || 0) >= 90 ? "text-safe" : 
                    (activeDataset.data_quality_score || 0) >= 70 ? "text-warning" : "text-danger"
                  }`}>
                    {activeDataset.data_quality_score !== undefined ? `${activeDataset.data_quality_score}%` : "100%"}
                  </span>
                </div>
              </div>

              {/* Selector */}
              <div className="mt-5 pt-4 border-t border-gray-800/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <label className="text-xs text-gray-400 font-medium">Switch Active Dataset:</label>
                <select
                  value={activeDataset.name}
                  onChange={(e) => handleSwitchDataset(e.target.value)}
                  className="bg-gray-950 border border-gray-800 text-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-brand-500 transition-colors w-full sm:w-64"
                >
                  {datasets.filter(d => d.status === "Success").map((d) => (
                    <option key={d.name} value={d.name}>
                      {d.name === "CERT" ? "CERT Dataset" : d.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Processing Progress Status */}
          {processingDataset && (
            <div className="bg-gray-900 border border-brand-500/20 rounded-xl p-5 shadow-lg relative overflow-hidden animate-pulse">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-gray-100 flex items-center gap-2">
                    <Loader2 size={16} className="animate-spin text-brand-400" />
                    Processing Telemetry Dataset: <span className="text-brand-400 font-extrabold">{processingDataset}</span>
                  </h3>
                  <p className="text-xs text-gray-400 mt-1">
                    Running ingestion pipelines (Data cleaning, Feature Engineering, Risk Rules, isolation Forest, Security Profiling).
                  </p>
                </div>
                <span className="text-xs font-extrabold text-brand-400">
                  {processingStatus?.progress || 0}%
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-950 rounded-full h-2 mt-4 overflow-hidden border border-gray-800">
                <div 
                  className="bg-brand-500 h-full rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${processingStatus?.progress || 0}%` }}
                ></div>
              </div>

              <div className="flex justify-between items-center mt-3">
                <span className="text-[10px] uppercase font-bold text-gray-500">Pipeline Stage:</span>
                <span className="text-[10px] uppercase font-extrabold text-brand-400 tracking-wider">
                  {processingStatus?.current_step || "Initializing..."}
                </span>
              </div>
            </div>
          )}

          {/* Dataset List / Queue Table */}
          <div className="bg-gray-900 border border-gray-850 rounded-xl p-5 shadow-lg">
            <h3 className="text-sm font-bold text-gray-200 mb-4 flex items-center gap-2">
              <FileSpreadsheet size={16} className="text-brand-400" />
              Repository Datasets
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-gray-800 text-gray-400 uppercase font-semibold">
                    <th className="py-2.5">Dataset Name</th>
                    <th className="py-2.5">Upload Date</th>
                    <th className="py-2.5 text-right">Users</th>
                    <th className="py-2.5 text-right">Total Records</th>
                    <th className="py-2.5 text-center">Status</th>
                    <th className="py-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/40 text-gray-300">
                  {datasets.map((d) => (
                    <tr key={d.name} className="hover:bg-gray-850/30 transition-colors">
                      <td className="py-3 font-semibold text-gray-100 flex items-center gap-1.5">
                        {d.name === "CERT" ? "CERT Dataset" : d.name}
                        {activeDataset?.name === d.name && (
                          <span className="w-1.5 h-1.5 bg-safe rounded-full" title="Currently Active" />
                        )}
                      </td>
                      <td className="py-3 text-gray-400">{d.upload_date}</td>
                      <td className="py-3 text-right font-medium">{d.total_users?.toLocaleString() || "0"}</td>
                      <td className="py-3 text-right font-medium">{d.total_records?.toLocaleString() || "0"}</td>
                      <td className="py-3 text-center">
                        <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          d.status === "Success" ? "bg-safe/10 text-safe border border-safe/20" :
                          d.status === "Failed" ? "bg-danger/10 text-danger border border-danger/20" :
                          "bg-warning/10 text-warning border border-warning/20"
                        }`}>
                          {d.status}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleReprocess(d.name)}
                            disabled={d.status === "Processing" || d.name === "CERT"}
                            className="p-1 text-gray-400 hover:text-white transition-colors disabled:opacity-40"
                            title="Reprocess Dataset"
                          >
                            <Play size={13} />
                          </button>
                          <button
                            onClick={() => handleDelete(d.name)}
                            disabled={d.status === "Processing" || d.name === "CERT"}
                            className="p-1 text-gray-500 hover:text-danger transition-colors disabled:opacity-40"
                            title="Delete Dataset"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {datasets.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-gray-500 italic">
                        No datasets uploaded yet. Use the sidebar module to import a dataset.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column (Upload Form) */}
        <div className="space-y-6">
          
          {/* Upload Card */}
          <div className="bg-gray-900 border border-gray-850 rounded-xl p-5 shadow-lg">
            <h3 className="text-sm font-bold text-gray-100 mb-4 flex items-center gap-2">
              <Upload size={16} className="text-brand-400" />
              Upload New Dataset
            </h3>

            <form onSubmit={handleUpload} className="space-y-4">
              {/* Dataset Name */}
              <div>
                <label className="text-xs text-gray-400 font-medium block mb-1">Dataset Identifier Name:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. NFC_Dataset, Custom_1"
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                  className="bg-gray-950 border border-gray-800 text-gray-200 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-brand-500 transition-colors w-full"
                />
              </div>

              {/* File selectors */}
              <div className="space-y-3">
                {/* Users file */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-xs text-gray-400 font-medium block">users.csv File:</label>
                    {usersFile && <span className="text-[10px] text-brand-400 font-semibold truncate max-w-[150px]">{usersFile.name}</span>}
                  </div>
                  <input
                    type="file"
                    required
                    accept=".csv"
                    onChange={(e) => setUsersFile(e.target.files?.[0] || null)}
                    className="block w-full text-xs text-gray-400 file:mr-3 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-[11px] file:font-semibold file:bg-gray-800 file:text-gray-200 hover:file:bg-gray-700 cursor-pointer"
                  />
                </div>

                {/* Logon file */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-xs text-gray-400 font-medium block">logon.csv File:</label>
                    {logonFile && <span className="text-[10px] text-brand-400 font-semibold truncate max-w-[150px]">{logonFile.name}</span>}
                  </div>
                  <input
                    type="file"
                    required
                    accept=".csv"
                    onChange={(e) => setLogonFile(e.target.files?.[0] || null)}
                    className="block w-full text-xs text-gray-400 file:mr-3 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-[11px] file:font-semibold file:bg-gray-800 file:text-gray-200 hover:file:bg-gray-700 cursor-pointer"
                  />
                </div>

                {/* Device file */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-xs text-gray-400 font-medium block">device.csv File:</label>
                    {deviceFile && <span className="text-[10px] text-brand-400 font-semibold truncate max-w-[150px]">{deviceFile.name}</span>}
                  </div>
                  <input
                    type="file"
                    required
                    accept=".csv"
                    onChange={(e) => setDeviceFile(e.target.files?.[0] || null)}
                    className="block w-full text-xs text-gray-400 file:mr-3 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-[11px] file:font-semibold file:bg-gray-800 file:text-gray-200 hover:file:bg-gray-700 cursor-pointer"
                  />
                </div>

                {/* LDAP file */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-xs text-gray-400 font-medium block">LDAP (ldap.csv) File:</label>
                    {ldapFile && <span className="text-[10px] text-brand-400 font-semibold truncate max-w-[150px]">{ldapFile.name}</span>}
                  </div>
                  <input
                    type="file"
                    required
                    accept=".csv"
                    onChange={(e) => setLdapFile(e.target.files?.[0] || null)}
                    className="block w-full text-xs text-gray-400 file:mr-3 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-[11px] file:font-semibold file:bg-gray-800 file:text-gray-200 hover:file:bg-gray-700 cursor-pointer"
                  />
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex gap-2 pt-3">
                <button
                  type="button"
                  onClick={handleValidate}
                  disabled={validating || uploading}
                  className="flex-1 px-3 py-2 bg-gray-800 hover:bg-gray-750 text-gray-200 text-xs font-semibold rounded-lg transition-colors border border-gray-750 disabled:opacity-50"
                >
                  {validating ? (
                    <span className="flex items-center justify-center gap-1">
                      <Loader2 className="animate-spin" size={13} />
                      Checking...
                    </span>
                  ) : "Validate Schema"}
                </button>
                <button
                  type="submit"
                  disabled={uploading || validating || !datasetName.trim()}
                  className="flex-1 px-3 py-2 bg-brand-500 hover:bg-brand-700 disabled:bg-brand-900 text-white text-xs font-semibold rounded-lg transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
                >
                  {uploading ? (
                    <>
                      <Loader2 className="animate-spin" size={13} />
                      Ingesting...
                    </>
                  ) : (
                    <>
                      <Upload size={13} />
                      Ingest Source
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Validation Result Box */}
          {validationResult && (
            <div className={`p-4 border rounded-xl shadow-md ${
              validationResult.valid ? "bg-safe/5 border-safe/20" : "bg-danger/5 border-danger/20"
            }`}>
              <div className="flex items-center gap-2">
                {validationResult.valid ? (
                  <>
                    <CheckCircle2 className="text-safe" size={18} />
                    <span className="text-sm font-bold text-safe">Dataset Schema Validated!</span>
                  </>
                ) : (
                  <>
                    <XCircle className="text-danger" size={18} />
                    <span className="text-sm font-bold text-danger">Validation Failures Found</span>
                  </>
                )}
              </div>

              {validationResult.valid ? (
                <p className="text-xs text-gray-400 mt-2">
                  All expected attributes (`user_id`, `department`, `activity`, `pc`/`device`, etc.) were detected. The ingestion pipeline can proceed safely.
                </p>
              ) : (
                <div className="mt-3 space-y-2 text-xs">
                  {Object.keys(validationResult.errors.missing_columns).map((file) => (
                    <div key={file} className="bg-gray-950 p-2.5 rounded-lg border border-gray-850">
                      <span className="text-danger font-semibold block mb-1">{file} missing columns:</span>
                      <div className="flex flex-wrap gap-1">
                        {validationResult.errors.missing_columns[file].map((col: string) => (
                          <span key={col} className="bg-danger/10 text-danger text-[10px] font-semibold px-2 py-0.5 rounded border border-danger/10">
                            {col}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {validationError && (
            <div className="bg-danger/5 border border-danger/20 p-4 rounded-xl flex items-start gap-2.5 shadow-md">
              <AlertTriangle className="text-danger mt-0.5" size={16} />
              <div>
                <span className="text-xs font-bold text-danger">Telemetry Engine Alert</span>
                <p className="text-[11px] text-gray-400 mt-0.5">{validationError}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Requirements Dialog Modal */}
      {showGuidance && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl overflow-y-auto max-h-[85vh]">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4">
              <h3 className="text-lg font-bold text-gray-100 flex items-center gap-2.5">
                <Database size={20} className="text-brand-500" />
                Custom Ingestion Format Requirements
              </h3>
              <button 
                onClick={() => setShowGuidance(false)}
                className="text-gray-500 hover:text-white text-sm"
              >
                ✕ Close
              </button>
            </div>

            <div className="space-y-4 text-xs text-gray-300 leading-relaxed">
              <div className="bg-brand-500/10 text-brand-400 p-3 rounded-lg border border-brand-500/10 font-medium">
                "To use custom organizational datasets, uploaded files must contain the required attributes used by the anomaly detection engine."
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-gray-200">1. users.csv Requirements</h4>
                <p className="text-gray-400">Maps employee rosters. Expected schema:</p>
                <pre className="bg-gray-950 p-2.5 rounded-lg border border-gray-850 font-mono text-[10px] text-brand-300">
                  user_id,name,department,role
                </pre>
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-gray-200">2. logon.csv Requirements</h4>
                <p className="text-gray-400">Captures network logons and logoffs. Expected schema:</p>
                <pre className="bg-gray-950 p-2.5 rounded-lg border border-gray-850 font-mono text-[10px] text-brand-300">
                  user_id,date,activity,pc
                  (date format example: 01/02/2010 07:30:00)
                </pre>
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-gray-200">3. device.csv Requirements</h4>
                <p className="text-gray-400">Traces external media connect/disconnect activity. Expected schema:</p>
                <pre className="bg-gray-950 p-2.5 rounded-lg border border-gray-850 font-mono text-[10px] text-brand-300">
                  user_id,date,activity,device
                  (date format example: 01/02/2010 15:45:00)
                </pre>
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-gray-200">4. LDAP (ldap.csv) Requirements</h4>
                <p className="text-gray-400">Defines supervision chains and groups. Expected schema:</p>
                <pre className="bg-gray-950 p-2.5 rounded-lg border border-gray-850 font-mono text-[10px] text-brand-300">
                  user_id,manager,team
                </pre>
              </div>

              <div className="bg-gray-950 p-3 rounded-lg border border-gray-850">
                <h4 className="font-bold text-gray-400 mb-1">Formatting & Type Standards:</h4>
                <ul className="list-disc pl-4 space-y-1 text-gray-400">
                  <li>Columns can be uploaded with either <code className="text-gray-300 font-mono">user_id</code> or <code className="text-gray-300 font-mono">user</code>.</li>
                  <li>In device logs, either <code className="text-gray-300 font-mono">device</code> or <code className="text-gray-300 font-mono">pc</code> will be mapped and normalized automatically.</li>
                  <li>Dates must be parseable timestamps (standard MM/DD/YYYY HH:MM:SS or ISO-8601 strings).</li>
                </ul>
              </div>
            </div>

            <div className="flex justify-end pt-4 mt-5 border-t border-gray-800">
              <button
                onClick={() => setShowGuidance(false)}
                className="px-4 py-2 bg-brand-500 hover:bg-brand-700 text-white font-bold rounded-lg transition-colors"
              >
                Acknowledge
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
