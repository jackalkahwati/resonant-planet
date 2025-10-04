import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Activity, Zap, Target, Info } from "lucide-react";

const Explainability = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Explainability Dashboard</h1>
        <p className="text-muted-foreground">
          Understand model decisions through physics-based validation and transparent visualizations
        </p>
      </div>

      <div className="mb-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Candidate Overview</CardTitle>
                <CardDescription>KIC 8462852 - Period 3.52 days</CardDescription>
              </div>
              <Badge className="text-lg px-4 py-2">Probability: 0.94</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">Transit Depth</p>
                <p className="text-2xl font-bold text-primary">1.2%</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">Duration</p>
                <p className="text-2xl font-bold">2.8h</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">SNR</p>
                <p className="text-2xl font-bold">12.4</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">Validation Score</p>
                <p className="text-2xl font-bold text-primary">8.7/10</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="phase-fold" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-7">
          <TabsTrigger value="phase-fold">Phase Fold</TabsTrigger>
          <TabsTrigger value="bls">BLS Spectrum</TabsTrigger>
          <TabsTrigger value="saliency">Saliency</TabsTrigger>
          <TabsTrigger value="odd-even">Odd/Even</TabsTrigger>
          <TabsTrigger value="secondary">Secondary</TabsTrigger>
          <TabsTrigger value="shape">Shape Test</TabsTrigger>
          <TabsTrigger value="centroid">Centroid</TabsTrigger>
        </TabsList>

        <TabsContent value="phase-fold" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                <CardTitle>Phase-Folded Light Curve</CardTitle>
              </div>
              <CardDescription>
                Transit signal folded at detected period with model fit overlay
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Interactive Plotly chart will render here</p>
              </div>
              <Alert className="mt-4">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Rationale:</strong> Phase-folded curve shows consistent transit shape across multiple
                  epochs, confirming periodicity. Model fit residuals within 3-sigma support genuine transit signal.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bls" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                <CardTitle>Box-Fitting Least Squares Periodogram</CardTitle>
              </div>
              <CardDescription>
                Power spectrum showing detected period and potential aliases
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">BLS periodogram visualization</p>
              </div>
              <Alert className="mt-4">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Rationale:</strong> Clear peak at 3.52 days with no strong aliases. Secondary peaks
                  ruled out through visual inspection and statistical tests.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="saliency" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                <CardTitle>Attention Saliency Map</CardTitle>
              </div>
              <CardDescription>
                Model attention weights over time showing important features
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Saliency heatmap visualization</p>
              </div>
              <Alert className="mt-4">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Rationale:</strong> Model attention concentrates on transit ingress and egress,
                  matching expected physics. No spurious attention on instrumental artifacts.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="odd-even" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                <CardTitle>Odd vs Even Transit Comparison</CardTitle>
              </div>
              <CardDescription>
                Depth consistency check to rule out eclipsing binary systems
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center mb-4">
                <p className="text-muted-foreground">Odd/Even transit overlay plot</p>
              </div>
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Odd Transit Depth</p>
                  <p className="text-2xl font-bold">1.21%</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Even Transit Depth</p>
                  <p className="text-2xl font-bold">1.18%</p>
                </div>
              </div>
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Rationale:</strong> Odd and even depths are consistent within 3%, well below the
                  threshold for eclipsing binary detection. This strongly reduces the likelihood of a
                  false positive from binary stars.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="secondary" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Secondary Eclipse Search</CardTitle>
              <CardDescription>
                Check for secondary eclipse that would indicate a stellar companion
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Secondary eclipse window visualization</p>
              </div>
              <Alert className="mt-4">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Rationale:</strong> No significant signal detected at phase 0.5, consistent with
                  planetary transit rather than eclipsing binary. Upper limit on secondary depth: 0.02%.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="shape" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Transit Shape Analysis</CardTitle>
              <CardDescription>
                Compare observed shape to V-shape characteristic of grazing eclipsing binaries
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Shape comparison plot</p>
              </div>
              <Alert className="mt-4">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Rationale:</strong> Transit exhibits flat-bottomed U-shape consistent with planetary
                  transit, not V-shape of grazing binary. Shape parameter χ² = 0.87 (threshold = 2.0).
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="centroid" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Centroid Motion Proxy</CardTitle>
              <CardDescription>
                Check for centroid shifts indicating background eclipsing binary
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Centroid shift analysis</p>
              </div>
              <Alert className="mt-4">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Rationale:</strong> No significant centroid shift detected during transit (Δx = 0.03px,
                  Δy = 0.02px). Signal originates from target star, not blended background source.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Explainability;
