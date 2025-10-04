import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Search, Upload, Play, Loader2, CheckCircle, AlertCircle, Telescope, Zap } from "lucide-react";
import { toast } from "sonner";
import { BaselineComparison } from "@/components/BaselineComparison";
import { sampleCandidates, Candidate } from "@/data/sampleCandidates";

const Detect = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [showComparison, setShowComparison] = useState(false);

  const handleRunDemo = (candidateIndex?: number) => {
    setIsProcessing(true);
    setShowComparison(false);
    toast.info("Starting analysis on pre-loaded sample data...");
    
    // Simulate processing
    setTimeout(() => {
      setIsProcessing(false);
      
      // Load all sample candidates
      setResults(sampleCandidates);
      
      // If specific candidate requested, highlight it
      if (candidateIndex !== undefined) {
        setSelectedCandidate(sampleCandidates[candidateIndex]);
      }
      
      toast.success(`Analysis complete! Found ${sampleCandidates.length} candidates (${sampleCandidates.filter(c => !c.isFalsePositive).length} genuine, ${sampleCandidates.filter(c => c.isFalsePositive).length} false positive).`);
    }, 2000);
  };

  const handleViewComparison = (candidate: Candidate) => {
    setSelectedCandidate(candidate);
    setShowComparison(true);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Transit Detection</h1>
        <p className="text-muted-foreground mb-4">
          Run analysis on pre-loaded sample data or upload your own light curves
        </p>
        
        {/* Quick Demo Buttons */}
        <div className="flex flex-wrap gap-3 mb-6">
          <Button variant="hero" onClick={() => handleRunDemo()} disabled={isProcessing}>
            <Zap className="h-4 w-4" />
            Run All Samples
          </Button>
          <Button variant="secondary" onClick={() => handleRunDemo(0)} disabled={isProcessing}>
            Demo: Kepler-90i
          </Button>
          <Button variant="secondary" onClick={() => handleRunDemo(2)} disabled={isProcessing}>
            Demo: Kepler-452b
          </Button>
          <Button variant="outline" onClick={() => handleRunDemo(3)} disabled={isProcessing}>
            Demo: False Positive
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Panel - Input */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Data Source</CardTitle>
              <CardDescription>Choose where to load light curve data</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="dataset" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="dataset">Dataset</TabsTrigger>
                  <TabsTrigger value="upload">Upload</TabsTrigger>
                </TabsList>
                
                <TabsContent value="dataset" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="mission">Mission</Label>
                    <Select>
                      <SelectTrigger id="mission">
                        <SelectValue placeholder="Select mission" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="kepler">Kepler</SelectItem>
                        <SelectItem value="k2">K2</SelectItem>
                        <SelectItem value="tess">TESS</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="target">Target ID</Label>
                    <div className="flex gap-2">
                      <Input id="target" placeholder="e.g., KIC 8462852" />
                      <Button size="icon" variant="secondary">
                        <Search className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="upload" className="space-y-4">
                  <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                    <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground mb-2">
                      Drop files here or click to browse
                    </p>
                    <Input type="file" className="hidden" id="file-upload" />
                    <Label htmlFor="file-upload">
                      <Button variant="secondary" size="sm" asChild>
                        <span>Choose File</span>
                      </Button>
                    </Label>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Processing Options</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="preset">Preprocessing Preset</Label>
                <Select defaultValue="standard">
                  <SelectTrigger id="preset">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="standard">Standard</SelectItem>
                    <SelectItem value="sensitive">High Sensitivity</SelectItem>
                    <SelectItem value="fast">Fast Scan</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <Button 
                className="w-full" 
                size="lg" 
                onClick={() => handleRunDemo()}
                disabled={isProcessing}
                variant="hero"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    Run Detection
                  </>
                )}
              </Button>

              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => handleRunDemo()}
              >
                <Zap className="h-5 w-5" />
                Try All Samples
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Panel - Results or Comparison */}
        <div className="lg:col-span-2">
          {showComparison && selectedCandidate ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Baseline vs. Resonant Comparison</CardTitle>
                      <CardDescription>{selectedCandidate.name}</CardDescription>
                    </div>
                    <Button variant="outline" onClick={() => setShowComparison(false)}>
                      Back to Results
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <BaselineComparison candidate={selectedCandidate} />
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Detection Results</CardTitle>
                <CardDescription>
                  {results.length > 0 
                    ? `Found ${results.length} candidate${results.length > 1 ? 's' : ''} in sample data`
                    : "Run detection to see results"
                  }
                </CardDescription>
              </CardHeader>
              <CardContent>
                {results.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Telescope className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="mb-2">No results yet. Try one of our pre-loaded samples to begin.</p>
                    <p className="text-sm mb-4">Samples include known planets and a false positive for comparison.</p>
                    <Button variant="hero" onClick={() => handleRunDemo()}>
                      <Zap className="h-4 w-4" />
                      Run All Samples
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {results.map((result, idx) => {
                      const validationCount = Object.values(result.validations).filter(Boolean).length;
                      const totalValidations = Object.keys(result.validations).length;
                      
                      return (
                        <Card key={result.id} className={`${result.isFalsePositive ? 'bg-accent/5' : 'bg-muted/50'}`}>
                          <CardContent className="pt-6">
                            <div className="flex items-start justify-between mb-4">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2 flex-wrap">
                                  <h3 className="font-semibold">{result.name}</h3>
                                  {result.isConfirmed && (
                                    <Badge variant="outline" className="text-xs">
                                      Confirmed Planet
                                    </Badge>
                                  )}
                                  {result.isFalsePositive && (
                                    <Badge variant="destructive" className="text-xs">
                                      False Positive
                                    </Badge>
                                  )}
                                </div>
                                <div className="flex items-center gap-2 mb-3 flex-wrap">
                                  <Badge variant={result.probability > 0.8 ? "default" : result.probability > 0.5 ? "secondary" : "outline"}>
                                    Resonant: {result.probability.toFixed(2)}
                                  </Badge>
                                  <Badge variant="outline" className="text-muted-foreground">
                                    Baseline: {result.baselineProbability.toFixed(2)}
                                  </Badge>
                                  <Badge variant="outline">
                                    Period: {result.period.toFixed(2)}d
                                  </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground mb-3">
                                  {result.description}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  Depth: {result.depth.toFixed(3)} | Duration: {result.duration.toFixed(1)}h | SNR: {result.snr.toFixed(1)}
                                </p>
                              </div>
                              <Button 
                                variant="secondary" 
                                size="sm"
                                onClick={() => handleViewComparison(result)}
                                className="ml-4"
                              >
                                Compare
                              </Button>
                            </div>
                            
                            <div className="flex gap-3 text-xs">
                              <span className="text-muted-foreground">
                                Validation: {validationCount}/{totalValidations}
                              </span>
                              <div className="flex gap-2">
                                {Object.entries(result.validations).map(([key, passed]) => (
                                  <div key={key} className="flex items-center gap-1">
                                    {passed ? (
                                      <CheckCircle className="h-3 w-3 text-primary" />
                                    ) : (
                                      <AlertCircle className="h-3 w-3 text-muted-foreground" />
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Detect;
