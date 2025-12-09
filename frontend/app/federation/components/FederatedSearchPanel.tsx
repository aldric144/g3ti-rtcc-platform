"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";

interface SearchResult {
  id: string;
  entityType: string;
  source: string;
  agencyId: string;
  agencyName: string;
  data: Record<string, unknown>;
  confidenceScore: number;
  isMasked: boolean;
}

export function FederatedSearchPanel() {
  const [query, setQuery] = useState("");
  const [selectedEntityTypes, setSelectedEntityTypes] = useState<string[]>([]);
  const [selectedAgencies, setSelectedAgencies] = useState<string[]>([]);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);

  const entityTypes = [
    { value: "person", label: "Person" },
    { value: "vehicle", label: "Vehicle" },
    { value: "address", label: "Address" },
    { value: "incident", label: "Incident" },
    { value: "bolo", label: "BOLO" },
    { value: "firearm", label: "Firearm" },
  ];

  const agencies = [
    { id: "agency-1", name: "County Sheriff's Office" },
    { id: "agency-2", name: "State Fusion Center" },
    { id: "agency-3", name: "Regional Task Force" },
    { id: "agency-4", name: "Transit Police" },
    { id: "agency-5", name: "University Police" },
  ];

  const handleSearch = async () => {
    if (!query.trim()) return;

    setSearching(true);
    setSearchPerformed(true);

    try {
      // Simulated search results
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const mockResults: SearchResult[] = [
        {
          id: "result-1",
          entityType: "person",
          source: "rms",
          agencyId: "agency-1",
          agencyName: "County Sheriff's Office",
          data: {
            name: "John Doe",
            dob: "[MASKED]",
            lastKnownAddress: "123 Main St",
          },
          confidenceScore: 0.95,
          isMasked: true,
        },
        {
          id: "result-2",
          entityType: "vehicle",
          source: "lpr",
          agencyId: "agency-2",
          agencyName: "State Fusion Center",
          data: {
            plate: "ABC1234",
            make: "Toyota",
            model: "Camry",
            color: "Blue",
          },
          confidenceScore: 0.88,
          isMasked: false,
        },
        {
          id: "result-3",
          entityType: "incident",
          source: "cad",
          agencyId: "agency-3",
          agencyName: "Regional Task Force",
          data: {
            incidentNumber: "2024-12345",
            type: "Burglary",
            date: "2024-12-01",
            location: "456 Oak Ave",
          },
          confidenceScore: 0.72,
          isMasked: false,
        },
      ];

      setResults(mockResults);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setSearching(false);
    }
  };

  const toggleEntityType = (type: string) => {
    setSelectedEntityTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const toggleAgency = (agencyId: string) => {
    setSelectedAgencies((prev) =>
      prev.includes(agencyId)
        ? prev.filter((a) => a !== agencyId)
        : [...prev, agencyId]
    );
  };

  const getEntityTypeColor = (type: string) => {
    switch (type) {
      case "person":
        return "bg-blue-500";
      case "vehicle":
        return "bg-green-500";
      case "address":
        return "bg-purple-500";
      case "incident":
        return "bg-orange-500";
      case "bolo":
        return "bg-red-500";
      case "firearm":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return "text-green-500";
    if (score >= 0.7) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Federated Search</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Search across all agencies..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={searching || !query.trim()}>
              {searching ? "Searching..." : "Search"}
            </Button>
          </div>

          <div>
            <p className="text-sm font-medium mb-2">Entity Types:</p>
            <div className="flex flex-wrap gap-2">
              {entityTypes.map((type) => (
                <Badge
                  key={type.value}
                  variant={selectedEntityTypes.includes(type.value) ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => toggleEntityType(type.value)}
                >
                  {type.label}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-medium mb-2">Target Agencies:</p>
            <div className="flex flex-wrap gap-2">
              {agencies.map((agency) => (
                <Badge
                  key={agency.id}
                  variant={selectedAgencies.includes(agency.id) ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => toggleAgency(agency.id)}
                >
                  {agency.name}
                </Badge>
              ))}
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-lg font-semibold mb-3">
              Results {results.length > 0 && `(${results.length})`}
            </h3>

            {searching ? (
              <div className="text-center py-8 text-muted-foreground">
                Searching across partner agencies...
              </div>
            ) : results.length > 0 ? (
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {results.map((result) => (
                  <div
                    key={result.id}
                    className="p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge className={getEntityTypeColor(result.entityType)}>
                          {result.entityType}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          from {result.agencyName}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {result.isMasked && (
                          <Badge variant="outline" className="text-xs">
                            Masked
                          </Badge>
                        )}
                        <span className={`text-sm font-medium ${getConfidenceColor(result.confidenceScore)}`}>
                          {Math.round(result.confidenceScore * 100)}% match
                        </span>
                      </div>
                    </div>
                    <div className="bg-muted/50 p-2 rounded text-sm">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </div>
                    <div className="mt-2 flex gap-2">
                      <Button size="sm" variant="outline">
                        View Full Record
                      </Button>
                      <Button size="sm" variant="outline">
                        Add to Case
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : searchPerformed ? (
              <div className="text-center py-8 text-muted-foreground">
                No results found for your search
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                Enter a search query to search across partner agencies
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
