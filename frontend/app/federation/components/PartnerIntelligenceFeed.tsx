"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";

interface IntelItem {
  id: string;
  type: string;
  classification: string;
  title: string;
  summary: string;
  sourceAgency: string;
  relatedEntities: string[];
  createdAt: string;
  expiresAt: string | null;
  isActionable: boolean;
}

interface ThreatIndicator {
  id: string;
  type: string;
  severity: string;
  description: string;
  sourceAgency: string;
  affectedAreas: string[];
  createdAt: string;
}

export function PartnerIntelligenceFeed() {
  const [intelItems, setIntelItems] = useState<IntelItem[]>([]);
  const [threatIndicators, setThreatIndicators] = useState<ThreatIndicator[]>([]);
  const [activeView, setActiveView] = useState<"feed" | "threats">("feed");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIntelFeed();
    fetchThreatIndicators();
  }, []);

  const fetchIntelFeed = async () => {
    try {
      setLoading(true);
      // Simulated data
      const mockIntel: IntelItem[] = [
        {
          id: "intel-1",
          type: "criminal_activity",
          classification: "law_enforcement_sensitive",
          title: "Organized Retail Theft Ring",
          summary: "Intelligence indicates organized retail theft ring operating across multiple jurisdictions. Suspects using rental vehicles and targeting electronics stores.",
          sourceAgency: "State Fusion Center",
          relatedEntities: ["Suspect Group Alpha", "Vehicle ABC-1234"],
          createdAt: "2024-12-09T16:00:00Z",
          expiresAt: "2024-12-16T16:00:00Z",
          isActionable: true,
        },
        {
          id: "intel-2",
          type: "gang_activity",
          classification: "confidential",
          title: "Gang Territory Expansion",
          summary: "Local gang expanding operations into neighboring jurisdiction. Increased recruitment activity observed near high schools.",
          sourceAgency: "Regional Task Force",
          relatedEntities: ["Gang XYZ", "Location: Downtown District"],
          createdAt: "2024-12-09T14:30:00Z",
          expiresAt: null,
          isActionable: true,
        },
        {
          id: "intel-3",
          type: "drug_trafficking",
          classification: "law_enforcement_sensitive",
          title: "Fentanyl Distribution Network",
          summary: "DEA intelligence indicates new fentanyl distribution network operating in the region. Multiple overdoses linked to this supply.",
          sourceAgency: "DEA",
          relatedEntities: ["Suspect John Doe", "Location: Industrial Area"],
          createdAt: "2024-12-09T12:00:00Z",
          expiresAt: "2024-12-23T12:00:00Z",
          isActionable: true,
        },
        {
          id: "intel-4",
          type: "vehicle_theft",
          classification: "unclassified",
          title: "Vehicle Theft Pattern",
          summary: "Pattern of vehicle thefts targeting late-model SUVs in parking garages. Suspects using electronic bypass devices.",
          sourceAgency: "County Sheriff",
          relatedEntities: ["Vehicle Pattern: SUVs 2020+"],
          createdAt: "2024-12-09T10:00:00Z",
          expiresAt: null,
          isActionable: false,
        },
      ];
      setIntelItems(mockIntel);
    } catch (error) {
      console.error("Failed to fetch intel feed:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchThreatIndicators = async () => {
    // Simulated threat indicators
    const mockThreats: ThreatIndicator[] = [
      {
        id: "threat-1",
        type: "violent_crime",
        severity: "high",
        description: "Elevated risk of violent crime in downtown area during weekend nights",
        sourceAgency: "Crime Analysis Unit",
        affectedAreas: ["Downtown", "Entertainment District"],
        createdAt: "2024-12-09T08:00:00Z",
      },
      {
        id: "threat-2",
        type: "civil_unrest",
        severity: "medium",
        description: "Planned protest at City Hall on Saturday. Potential for counter-protesters.",
        sourceAgency: "Intelligence Unit",
        affectedAreas: ["City Hall", "Government Center"],
        createdAt: "2024-12-09T09:00:00Z",
      },
      {
        id: "threat-3",
        type: "cyber_threat",
        severity: "low",
        description: "Phishing campaign targeting government employees detected",
        sourceAgency: "State Fusion Center",
        affectedAreas: ["All Government Networks"],
        createdAt: "2024-12-09T07:00:00Z",
      },
    ];
    setThreatIndicators(mockThreats);
  };

  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case "top_secret":
        return "bg-red-600";
      case "secret":
        return "bg-orange-600";
      case "confidential":
        return "bg-yellow-600";
      case "law_enforcement_sensitive":
        return "bg-blue-600";
      case "unclassified":
        return "bg-green-600";
      default:
        return "bg-gray-500";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "criminal_activity":
        return "bg-purple-500";
      case "gang_activity":
        return "bg-red-500";
      case "drug_trafficking":
        return "bg-orange-500";
      case "vehicle_theft":
        return "bg-blue-500";
      case "terrorism":
        return "bg-red-700";
      default:
        return "bg-gray-500";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-600";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  const actionableCount = intelItems.filter((i) => i.isActionable).length;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Partner Intelligence Feed</span>
          {actionableCount > 0 && (
            <Badge className="bg-orange-500">{actionableCount} actionable</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* View Toggle */}
          <div className="flex gap-2 border-b pb-2">
            <Button
              variant={activeView === "feed" ? "default" : "ghost"}
              size="sm"
              onClick={() => setActiveView("feed")}
            >
              Intelligence Feed ({intelItems.length})
            </Button>
            <Button
              variant={activeView === "threats" ? "default" : "ghost"}
              size="sm"
              onClick={() => setActiveView("threats")}
            >
              Threat Indicators ({threatIndicators.length})
            </Button>
          </div>

          {/* Content */}
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading intelligence feed...
            </div>
          ) : activeView === "feed" ? (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {intelItems.map((item) => (
                <div
                  key={item.id}
                  className={`p-4 border rounded-lg ${
                    item.isActionable ? "border-l-4 border-l-orange-500" : ""
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={getClassificationColor(item.classification)}>
                        {item.classification.replace("_", " ")}
                      </Badge>
                      <Badge className={getTypeColor(item.type)}>
                        {item.type.replace("_", " ")}
                      </Badge>
                      {item.isActionable && (
                        <Badge variant="outline" className="text-orange-500 border-orange-500">
                          Actionable
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(item.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <h4 className="font-semibold mb-1">{item.title}</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    {item.summary}
                  </p>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {item.relatedEntities.map((entity) => (
                      <Badge key={entity} variant="outline" className="text-xs">
                        {entity}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      Source: {item.sourceAgency}
                    </span>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                      <Button size="sm" variant="outline">
                        Add to Case
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {threatIndicators.map((threat) => (
                <div
                  key={threat.id}
                  className="p-4 border rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(threat.severity)}>
                        {threat.severity}
                      </Badge>
                      <Badge variant="outline">
                        {threat.type.replace("_", " ")}
                      </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(threat.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm mb-2">{threat.description}</p>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {threat.affectedAreas.map((area) => (
                      <Badge key={area} variant="outline" className="text-xs">
                        {area}
                      </Badge>
                    ))}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    Source: {threat.sourceAgency}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="pt-4 border-t flex gap-2">
            <Button variant="outline" className="flex-1">
              Submit Intelligence
            </Button>
            <Button variant="outline" className="flex-1">
              Request Intel
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
