import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowUpDown, Download, Filter, CheckCircle, AlertCircle } from "lucide-react";

const mockCandidates = [
  { id: "KIC-001", probability: 0.94, period: 3.52, depth: 0.012, snr: 12.4, validations: { oddEven: true, secondary: true, shape: true } },
  { id: "KIC-002", probability: 0.89, period: 7.23, depth: 0.008, snr: 10.1, validations: { oddEven: true, secondary: false, shape: true } },
  { id: "KIC-003", probability: 0.76, period: 15.6, depth: 0.005, snr: 8.3, validations: { oddEven: true, secondary: true, shape: false } },
  { id: "KIC-004", probability: 0.68, period: 2.14, depth: 0.015, snr: 9.7, validations: { oddEven: false, secondary: true, shape: true } },
  { id: "KIC-005", probability: 0.54, period: 42.1, depth: 0.003, snr: 6.2, validations: { oddEven: true, secondary: false, shape: false } },
];

const Compare = () => {
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
              <CardDescription>5 candidates from current analysis batch</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4" />
                Filter
              </Button>
              <Button variant="secondary" size="sm">
                <Download className="h-4 w-4" />
                Export All
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input placeholder="Search by ID or filter by metrics..." />
          </div>

          <div className="rounded-lg border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0">
                      ID <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0">
                      Probability <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0">
                      Period <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0">
                      Depth <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button variant="ghost" size="sm" className="h-8 p-0">
                      SNR <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </TableHead>
                  <TableHead>Validations</TableHead>
                  <TableHead>Trend</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockCandidates.map((candidate) => {
                  const passedValidations = Object.values(candidate.validations).filter(Boolean).length;
                  const totalValidations = Object.keys(candidate.validations).length;

                  return (
                    <TableRow key={candidate.id}>
                      <TableCell className="font-mono text-sm">{candidate.id}</TableCell>
                      <TableCell>
                        <Badge variant={candidate.probability > 0.8 ? "default" : "secondary"}>
                          {candidate.probability.toFixed(2)}
                        </Badge>
                      </TableCell>
                      <TableCell>{candidate.period.toFixed(2)}d</TableCell>
                      <TableCell>{candidate.depth.toFixed(3)}</TableCell>
                      <TableCell>{candidate.snr.toFixed(1)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <span className="text-sm">{passedValidations}/{totalValidations}</span>
                          <div className="flex gap-1 ml-2">
                            {candidate.validations.oddEven ? (
                              <CheckCircle className="h-3 w-3 text-primary" />
                            ) : (
                              <AlertCircle className="h-3 w-3 text-muted-foreground" />
                            )}
                            {candidate.validations.secondary ? (
                              <CheckCircle className="h-3 w-3 text-primary" />
                            ) : (
                              <AlertCircle className="h-3 w-3 text-muted-foreground" />
                            )}
                            {candidate.validations.shape ? (
                              <CheckCircle className="h-3 w-3 text-primary" />
                            ) : (
                              <AlertCircle className="h-3 w-3 text-muted-foreground" />
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="w-16 h-8 bg-muted rounded flex items-end gap-[2px] p-1">
                          {[3, 5, 4, 6, 7, 5, 8].map((height, i) => (
                            <div
                              key={i}
                              className="flex-1 bg-primary/50"
                              style={{ height: `${height * 10}%` }}
                            />
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button variant="secondary" size="sm">
                          View
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
              <p className="text-4xl font-bold text-primary">2</p>
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
              <p className="text-4xl font-bold">2</p>
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
              <p className="text-4xl font-bold text-accent">1</p>
              <p className="text-sm text-muted-foreground">Probability &lt; 0.6</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Compare;
