import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon, FileSpreadsheet, CheckCircle, XCircle, AlertCircle, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { uploadFile } from '@/lib/api';
import { formatPercent, getClassColor } from '@/lib/utils';

interface UploadResult {
  filename: string;
  summary: {
    total_analyzed: number;
    confirmed_exoplanets: number;
    candidates: number;
    false_positives: number;
    high_confidence_confirmed: number;
  };
  predictions: Array<{
    index: number;
    object_id?: string;
    predicted_class: number;
    predicted_class_name: string;
    confidence: number;
  }>;
  total_predictions: number;
}

export const Upload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadFile(file);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const downloadSampleCSV = () => {
    const headers = 'kepid,koi_period,koi_duration,koi_depth,koi_prad,koi_teq,koi_insol,koi_model_snr,koi_steff,koi_srad,koi_smass,koi_impact';
    const sample1 = '10797460,10.304,3.5,500,1.5,288,1.0,50,5778,1.0,1.0,0.3';
    const sample2 = '11442793,3.5,2.1,15000,12.0,1500,1000,200,6000,1.2,1.1,0.1';
    const sample3 = '10748390,50.2,5.8,800,2.5,350,1.5,75,5200,0.9,0.95,0.5';
    
    const csv = [headers, sample1, sample2, sample3].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_exoplanet_data.csv';
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <h2 className="text-3xl font-bold gradient-text mb-2">Upload Data</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Upload a CSV file with transit observations for batch classification
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Zone */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle>Upload CSV File</CardTitle>
              <CardDescription>Drag and drop or click to select a file</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  isDragActive
                    ? 'border-purple-500 bg-purple-500/10'
                    : 'border-white/20 hover:border-purple-500/50 hover:bg-white/5'
                }`}
              >
                <input {...getInputProps()} />
                <UploadIcon className={`w-12 h-12 mx-auto mb-4 ${isDragActive ? 'text-purple-400' : 'text-gray-500'}`} />
                {isDragActive ? (
                  <p className="text-purple-300">Drop the file here...</p>
                ) : (
                  <>
                    <p className="text-gray-300 mb-2">Drag & drop a CSV file here</p>
                    <p className="text-gray-500 text-sm">or click to browse</p>
                  </>
                )}
              </div>

              {/* Selected File */}
              {file && (
                <div className="mt-4 p-4 bg-white/5 rounded-lg flex items-center gap-3">
                  <FileSpreadsheet className="w-8 h-8 text-cyan-400" />
                  <div className="flex-1">
                    <p className="text-white font-medium">{file.name}</p>
                    <p className="text-gray-400 text-sm">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="text-gray-400 hover:text-white"
                  >
                    <XCircle className="w-5 h-5" />
                  </button>
                </div>
              )}

              {/* Upload Button */}
              <Button
                onClick={handleUpload}
                disabled={!file || isUploading}
                isLoading={isUploading}
                size="lg"
                className="w-full mt-4"
              >
                <UploadIcon className="w-5 h-5 mr-2" />
                Analyze Data
              </Button>

              {error && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  {error}
                </div>
              )}

              {/* Sample Download */}
              <div className="mt-6 pt-6 border-t border-white/10">
                <p className="text-sm text-gray-400 mb-3">Need a sample file to test?</p>
                <Button variant="outline" size="sm" onClick={downloadSampleCSV}>
                  <Download className="w-4 h-4 mr-2" />
                  Download Sample CSV
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Required Columns */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Required Columns</CardTitle>
              <CardDescription>Your CSV should include these features</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {[
                  'koi_period - Orbital period',
                  'koi_duration - Transit duration',
                  'koi_depth - Transit depth',
                  'koi_prad - Planet radius',
                  'koi_teq - Equilibrium temp',
                  'koi_insol - Insolation flux',
                  'koi_model_snr - Signal-to-noise',
                  'koi_steff - Star temperature',
                  'koi_srad - Star radius',
                  'koi_smass - Star mass',
                ].map((col) => (
                  <div key={col} className="text-gray-400">
                    <code className="text-purple-300">{col.split(' - ')[0]}</code>
                    <span className="text-gray-500"> - {col.split(' - ')[1]}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Results */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
              <CardDescription>Classification summary and predictions</CardDescription>
            </CardHeader>
            <CardContent>
              {!result ? (
                <div className="text-center py-16 text-gray-400">
                  <FileSpreadsheet className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p>Upload a file to see analysis results</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/5 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-white">{result.summary.total_analyzed}</p>
                      <p className="text-sm text-gray-400">Total Analyzed</p>
                    </div>
                    <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-green-400">{result.summary.confirmed_exoplanets}</p>
                      <p className="text-sm text-gray-400">Confirmed</p>
                    </div>
                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-yellow-400">{result.summary.candidates}</p>
                      <p className="text-sm text-gray-400">Candidates</p>
                    </div>
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-red-400">{result.summary.false_positives}</p>
                      <p className="text-sm text-gray-400">False Positives</p>
                    </div>
                  </div>

                  {/* High Confidence */}
                  {result.summary.high_confidence_confirmed > 0 && (
                    <div className="bg-gradient-to-r from-green-500/20 to-cyan-500/20 border border-green-500/30 rounded-lg p-4">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <span className="text-white font-medium">
                          {result.summary.high_confidence_confirmed} high-confidence exoplanet(s) found!
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm mt-1">
                        These have &gt;80% confidence as confirmed exoplanets
                      </p>
                    </div>
                  )}

                  {/* Predictions Table */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-3">
                      Predictions (showing first {Math.min(result.predictions.length, 20)})
                    </h4>
                    <div className="max-h-64 overflow-y-auto">
                      <table className="w-full text-sm">
                        <thead className="text-gray-400 border-b border-white/10 sticky top-0 bg-space-dark">
                          <tr>
                            <th className="text-left py-2 px-2">#</th>
                            <th className="text-left py-2 px-2">ID</th>
                            <th className="text-left py-2 px-2">Class</th>
                            <th className="text-right py-2 px-2">Confidence</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.predictions.slice(0, 20).map((pred) => (
                            <tr key={pred.index} className="border-b border-white/5">
                              <td className="py-2 px-2 text-gray-500">{pred.index + 1}</td>
                              <td className="py-2 px-2 text-gray-300">{pred.object_id || '-'}</td>
                              <td className={`py-2 px-2 ${getClassColor(pred.predicted_class_name)}`}>
                                {pred.predicted_class_name}
                              </td>
                              <td className="py-2 px-2 text-right text-white">
                                {formatPercent(pred.confidence)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {result.total_predictions > 20 && (
                      <p className="text-gray-500 text-sm mt-2 text-center">
                        ... and {result.total_predictions - 20} more predictions
                      </p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};
