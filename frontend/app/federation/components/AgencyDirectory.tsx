"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";

interface Agency {
  id: string;
  name: string;
  type: string;
  status: string;
  jurisdiction: string;
  data_sharing_level: string;
}

export function AgencyDirectory() {
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgencies();
  }, []);

  const fetchAgencies = async () => {
    try {
      setLoading(true);
      // Simulated data for now
      const mockAgencies: Agency[] = [
        {
          id: "agency-1",
          name: "County Sheriff's Office",
          type: "sheriff_office",
          status: "active",
          jurisdiction: "County",
          data_sharing_level: "full",
        },
        {
          id: "agency-2",
          name: "State Fusion Center",
          type: "state_fusion_center",
          status: "active",
          jurisdiction: "State",
          data_sharing_level: "full",
        },
        {
          id: "agency-3",
          name: "Regional Task Force",
          type: "regional_task_force",
          status: "active",
          jurisdiction: "Regional",
          data_sharing_level: "standard",
        },
        {
          id: "agency-4",
          name: "Transit Police",
          type: "transit_police",
          status: "pending",
          jurisdiction: "Metro",
          data_sharing_level: "basic",
        },
        {
          id: "agency-5",
          name: "University Police",
          type: "university_police",
          status: "active",
          jurisdiction: "Campus",
          data_sharing_level: "basic",
        },
      ];
      setAgencies(mockAgencies);
    } catch (error) {
      console.error("Failed to fetch agencies:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAgencies = agencies.filter((agency) => {
    const matchesSearch =
      agency.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agency.jurisdiction.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !filterType || agency.type === filterType;
    return matchesSearch && matchesType;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500";
      case "pending":
        return "bg-yellow-500";
      case "inactive":
        return "bg-gray-500";
      case "suspended":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getSharingLevelColor = (level: string) => {
    switch (level) {
      case "full":
        return "bg-blue-500";
      case "standard":
        return "bg-indigo-500";
      case "basic":
        return "bg-purple-500";
      case "restricted":
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  const agencyTypes = [
    { value: "sheriff_office", label: "Sheriff's Office" },
    { value: "state_fusion_center", label: "State Fusion Center" },
    { value: "regional_task_force", label: "Regional Task Force" },
    { value: "transit_police", label: "Transit Police" },
    { value: "university_police", label: "University Police" },
    { value: "county_intelligence", label: "County Intelligence" },
  ];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Partner Agency Directory</span>
          <Badge variant="outline">{agencies.length} Agencies</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Search agencies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            <select
              className="px-3 py-2 border rounded-md bg-background"
              value={filterType || ""}
              onChange={(e) => setFilterType(e.target.value || null)}
            >
              <option value="">All Types</option>
              {agencyTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading agencies...
            </div>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {filteredAgencies.map((agency) => (
                <div
                  key={agency.id}
                  className="p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold">{agency.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {agency.jurisdiction} Jurisdiction
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Badge className={getStatusColor(agency.status)}>
                        {agency.status}
                      </Badge>
                      <Badge className={getSharingLevelColor(agency.data_sharing_level)}>
                        {agency.data_sharing_level}
                      </Badge>
                    </div>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Button size="sm" variant="outline">
                      View Details
                    </Button>
                    <Button size="sm" variant="outline">
                      Configure
                    </Button>
                    <Button size="sm" variant="outline">
                      Query Data
                    </Button>
                  </div>
                </div>
              ))}
              {filteredAgencies.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No agencies found matching your criteria
                </div>
              )}
            </div>
          )}

          <div className="pt-4 border-t">
            <Button className="w-full">Register New Agency</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
