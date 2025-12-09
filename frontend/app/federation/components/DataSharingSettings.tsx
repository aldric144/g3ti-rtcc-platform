"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";

interface DataSharingAgreement {
  id: string;
  partnerAgency: string;
  dataCategories: string[];
  sharingLevel: string;
  status: string;
  effectiveDate: string;
  expirationDate: string | null;
}

interface AccessPolicy {
  id: string;
  name: string;
  description: string;
  appliesTo: string[];
  permissions: string[];
  isActive: boolean;
}

export function DataSharingSettings() {
  const [agreements] = useState<DataSharingAgreement[]>([
    {
      id: "dsa-1",
      partnerAgency: "County Sheriff's Office",
      dataCategories: ["incidents", "persons", "vehicles", "bolos"],
      sharingLevel: "full",
      status: "active",
      effectiveDate: "2024-01-01",
      expirationDate: "2025-12-31",
    },
    {
      id: "dsa-2",
      partnerAgency: "State Fusion Center",
      dataCategories: ["intelligence", "threats", "patterns"],
      sharingLevel: "standard",
      status: "active",
      effectiveDate: "2024-03-15",
      expirationDate: null,
    },
    {
      id: "dsa-3",
      partnerAgency: "Regional Task Force",
      dataCategories: ["incidents", "suspects"],
      sharingLevel: "basic",
      status: "pending",
      effectiveDate: "2024-06-01",
      expirationDate: "2025-06-01",
    },
  ]);

  const [policies] = useState<AccessPolicy[]>([
    {
      id: "policy-1",
      name: "Full Data Access",
      description: "Complete access to all shared data categories",
      appliesTo: ["County Sheriff's Office"],
      permissions: ["read", "query", "export"],
      isActive: true,
    },
    {
      id: "policy-2",
      name: "Intelligence Only",
      description: "Access limited to intelligence and threat data",
      appliesTo: ["State Fusion Center"],
      permissions: ["read", "query"],
      isActive: true,
    },
    {
      id: "policy-3",
      name: "Incident Sharing",
      description: "Basic incident data sharing",
      appliesTo: ["Regional Task Force", "Transit Police"],
      permissions: ["read"],
      isActive: true,
    },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500";
      case "pending":
        return "bg-yellow-500";
      case "expired":
        return "bg-red-500";
      case "suspended":
        return "bg-orange-500";
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
      default:
        return "bg-gray-500";
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Data Sharing Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-3">Data Sharing Agreements</h3>
            <div className="space-y-3">
              {agreements.map((agreement) => (
                <div
                  key={agreement.id}
                  className="p-4 border rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold">{agreement.partnerAgency}</h4>
                      <p className="text-sm text-muted-foreground">
                        Effective: {agreement.effectiveDate}
                        {agreement.expirationDate && ` - ${agreement.expirationDate}`}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Badge className={getStatusColor(agreement.status)}>
                        {agreement.status}
                      </Badge>
                      <Badge className={getSharingLevelColor(agreement.sharingLevel)}>
                        {agreement.sharingLevel}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {agreement.dataCategories.map((category) => (
                      <Badge key={category} variant="outline" className="text-xs">
                        {category}
                      </Badge>
                    ))}
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Button size="sm" variant="outline">
                      Edit
                    </Button>
                    <Button size="sm" variant="outline">
                      View Details
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <Button className="mt-3" variant="outline">
              Create New Agreement
            </Button>
          </div>

          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-3">Access Policies</h3>
            <div className="space-y-3">
              {policies.map((policy) => (
                <div
                  key={policy.id}
                  className="p-4 border rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold">{policy.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {policy.description}
                      </p>
                    </div>
                    <Badge className={policy.isActive ? "bg-green-500" : "bg-gray-500"}>
                      {policy.isActive ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  <div className="mt-2">
                    <p className="text-xs text-muted-foreground mb-1">Applies to:</p>
                    <div className="flex flex-wrap gap-1">
                      {policy.appliesTo.map((agency) => (
                        <Badge key={agency} variant="outline" className="text-xs">
                          {agency}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="mt-2">
                    <p className="text-xs text-muted-foreground mb-1">Permissions:</p>
                    <div className="flex flex-wrap gap-1">
                      {policy.permissions.map((perm) => (
                        <Badge key={perm} variant="secondary" className="text-xs">
                          {perm}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Button size="sm" variant="outline">
                      Edit Policy
                    </Button>
                    <Button size="sm" variant="outline">
                      {policy.isActive ? "Deactivate" : "Activate"}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <Button className="mt-3" variant="outline">
              Create New Policy
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
