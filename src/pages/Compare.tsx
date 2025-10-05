import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowUpDown, Download, CheckCircle, XCircle, TrendingUp, TrendingDown } from "lucide-react";
import { sampleCandidates } from "@/data/sampleCandidates";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Compare = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<"probability" | "period" | "snr">("probability");
  const [sortDesc, setSortDesc] = useState(true);

  const filteredCandidates = sampleCandidates
    .filter(c => 
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.id.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      return sortDesc ? bVal - aVal : aVal - bVal;
    });

  const handleSort = (field: typeof sortField) => {
    if (sortField === field) {
      setSortDesc(!sortDesc);
    } else {
      setSortField(field);
      setSortDesc(true);
    }
  };

  const handleExportAll = () => {
    const csv = `ID,Name,Mission,Probability,Period (days),Depth (%),Duration (hrs),SNR,Status\n${filteredCandidates.map(c => 
      `${c.id},${c.name},${c.mission},${c.probability},${c.period},${(c.depth * 100).toFixed(2)},${c.duration},${c.snr},${c.isConfirmed ? 'Confirmed' : c.isFalsePositive ? 'False Positive' : 'Candidate'}`
    ).join('\n')}`;
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `candidates_comparison_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const highConfidence = filteredCandidates.filter(c => c.probability > 0.8).length;
  const moderate = filteredCandidates.filter(c => c.probability >= 0.6 && c.probability <= 0.8).length;
  const lowConfidence = filteredCandidates.filter(c => c.probability < 0.6).length;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Compare Candidates</h1>
        <p className="text-muted-foreground">
          View and compare multiple detection results side by side
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Candidate List</CardTitle>
              <CardDescription>{filteredCandidates.length} candidates from sample dataset</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleExportAll}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input 
              placeholder="Search by name or ID..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="rounded-lg border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Mission</TableHead>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0" onClick={() => handleSort("probability")}>
                      Probability <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0" onClick={() => handleSort("period")}>
                      Period <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0" onClick={() => handleSort("snr")}>
                      SNR <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>Validations</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCandidates.map((candidate) => {
                  const passedValidations = Object.values(candidate.validations).filter(Boolean).length;
                  const totalValidations = Object.keys(candidate.validations).length;

                  return (
                    <TableRow key={candidate.id}>
                      <TableCell className="font-medium">{candidate.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{candidate.mission}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Badge variant={candidate.probability > 0.8 ? "default" : "secondary"}>
                            {(candidate.probability * 100).toFixed(0)}%
                          </Badge>
                          {candidate.probability > candidate.baselineProbability ? (
                            <TrendingUp className="h-3 w-3 text-green-500" />
                          ) : (
                            <TrendingDown className="h-3 w-3 text-red-500" />
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{candidate.period.toFixed(2)} days</TableCell>
                      <TableCell>{candidate.snr.toFixed(1)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <span className="text-sm font-semibold">{passedValidations}/{totalValidations}</span>
                          <div className="flex gap-1 ml-2">
                            {candidate.validations.oddEven ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <XCircle className="h-3 w-3 text-red-500" />
                            )}
                            {candidate.validations.secondary ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <XCircle className="h-3 w-3 text-red-500" />
                            )}
                            {candidate.validations.shape ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <XCircle className="h-3 w-3 text-red-500" />
                            )}
                            {candidate.validations.centroid ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <XCircle className="h-3 w-3 text-red-500" />
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {candidate.isConfirmed && (
                          <Badge variant="default">Confirmed</Badge>
                        )}
                        {candidate.isFalsePositive && (
                          <Badge variant="destructive">False Positive</Badge>
                        )}
                        {!candidate.isConfirmed && !candidate.isFalsePositive && (
                          <Badge variant="secondary">Candidate</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => navigate('/explainability')}
                        >
                          Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">High Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <p className="text-4xl font-bold text-primary">{highConfidence}</p>
              <p className="text-sm text-muted-foreground">Probability &gt; 0.8</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Moderate Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <p className="text-4xl font-bold">{moderate}</p>
              <p className="text-sm text-muted-foreground">0.6 &lt; Probability &lt; 0.8</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Requires Review</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <p className="text-4xl font-bold text-orange-500">{lowConfidence}</p>
              <p className="text-sm text-muted-foreground">Probability &lt; 0.6</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Compare;
