"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/app/components/ui/tabs";
import {
  AgencyDirectory,
  DataSharingSettings,
  FederatedSearchPanel,
  MissionRoomViewer,
  FederatedNotificationsPanel,
  PartnerIntelligenceFeed,
} from "./components";

export default function FederationPage() {
  const [activeTab, setActiveTab] = useState("directory");

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Multi-Agency Intelligence Hub</h1>
        <p className="text-muted-foreground mt-1">
          Cross-jurisdiction data federation, intelligence sharing, and interagency collaboration
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-6 w-full">
          <TabsTrigger value="directory">Agency Directory</TabsTrigger>
          <TabsTrigger value="search">Federated Search</TabsTrigger>
          <TabsTrigger value="missions">Mission Rooms</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="intelligence">Intelligence Feed</TabsTrigger>
          <TabsTrigger value="settings">Data Sharing</TabsTrigger>
        </TabsList>

        <TabsContent value="directory" className="mt-4">
          <AgencyDirectory />
        </TabsContent>

        <TabsContent value="search" className="mt-4">
          <FederatedSearchPanel />
        </TabsContent>

        <TabsContent value="missions" className="mt-4">
          <MissionRoomViewer />
        </TabsContent>

        <TabsContent value="notifications" className="mt-4">
          <FederatedNotificationsPanel />
        </TabsContent>

        <TabsContent value="intelligence" className="mt-4">
          <PartnerIntelligenceFeed />
        </TabsContent>

        <TabsContent value="settings" className="mt-4">
          <DataSharingSettings />
        </TabsContent>
      </Tabs>
    </div>
  );
}
