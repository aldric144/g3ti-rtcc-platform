"use client";

import { useState } from "react";

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  federalAccess: boolean;
  permissions: {
    canExportNdex: boolean;
    canQueryNcic: boolean;
    canExportEtrace: boolean;
    canSubmitSar: boolean;
    canViewAuditLogs: boolean;
  };
  lastActive: string;
}

export function AccessControlManager() {
  const [users, setUsers] = useState<User[]>([
    {
      id: "user-001",
      name: "John Smith",
      email: "john.smith@agency.gov",
      role: "supervisor",
      federalAccess: true,
      permissions: {
        canExportNdex: true,
        canQueryNcic: true,
        canExportEtrace: true,
        canSubmitSar: true,
        canViewAuditLogs: true,
      },
      lastActive: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: "user-002",
      name: "Jane Doe",
      email: "jane.doe@agency.gov",
      role: "detective",
      federalAccess: true,
      permissions: {
        canExportNdex: true,
        canQueryNcic: true,
        canExportEtrace: true,
        canSubmitSar: true,
        canViewAuditLogs: false,
      },
      lastActive: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      id: "user-003",
      name: "Bob Wilson",
      email: "bob.wilson@agency.gov",
      role: "officer",
      federalAccess: false,
      permissions: {
        canExportNdex: false,
        canQueryNcic: false,
        canExportEtrace: false,
        canSubmitSar: false,
        canViewAuditLogs: false,
      },
      lastActive: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: "user-004",
      name: "Alice Johnson",
      email: "alice.johnson@agency.gov",
      role: "rtcc_analyst",
      federalAccess: true,
      permissions: {
        canExportNdex: true,
        canQueryNcic: false,
        canExportEtrace: false,
        canSubmitSar: true,
        canViewAuditLogs: false,
      },
      lastActive: new Date(Date.now() - 1800000).toISOString(),
    },
  ]);

  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const roles = [
    { value: "admin", label: "Administrator", color: "bg-purple-500" },
    { value: "supervisor", label: "Supervisor", color: "bg-blue-500" },
    { value: "detective", label: "Detective", color: "bg-green-500" },
    { value: "rtcc_analyst", label: "RTCC Analyst", color: "bg-yellow-500" },
    { value: "officer", label: "Officer", color: "bg-gray-500" },
  ];

  const permissions = [
    { key: "canExportNdex", label: "Export to N-DEx", description: "Create N-DEx data exports" },
    { key: "canQueryNcic", label: "Query NCIC", description: "Submit NCIC queries (stub)" },
    { key: "canExportEtrace", label: "Export to eTrace", description: "Create ATF eTrace requests" },
    { key: "canSubmitSar", label: "Submit SAR", description: "Create and submit SAR reports" },
    { key: "canViewAuditLogs", label: "View Audit Logs", description: "Access CJIS audit logs" },
  ];

  const getRoleColor = (role: string) => {
    const found = roles.find((r) => r.value === role);
    return found?.color || "bg-gray-500";
  };

  const getRoleLabel = (role: string) => {
    const found = roles.find((r) => r.value === role);
    return found?.label || role;
  };

  const handleTogglePermission = (userId: string, permKey: string) => {
    setUsers(
      users.map((user) => {
        if (user.id === userId) {
          return {
            ...user,
            permissions: {
              ...user.permissions,
              [permKey]: !user.permissions[permKey as keyof typeof user.permissions],
            },
          };
        }
        return user;
      })
    );
  };

  const handleToggleFederalAccess = (userId: string) => {
    setUsers(
      users.map((user) => {
        if (user.id === userId) {
          const newFederalAccess = !user.federalAccess;
          return {
            ...user,
            federalAccess: newFederalAccess,
            permissions: newFederalAccess
              ? user.permissions
              : {
                  canExportNdex: false,
                  canQueryNcic: false,
                  canExportEtrace: false,
                  canSubmitSar: false,
                  canViewAuditLogs: false,
                },
          };
        }
        return user;
      })
    );
  };

  const handleRoleChange = (userId: string, newRole: string) => {
    const rolePermissions: Record<string, User["permissions"]> = {
      admin: {
        canExportNdex: true,
        canQueryNcic: true,
        canExportEtrace: true,
        canSubmitSar: true,
        canViewAuditLogs: true,
      },
      supervisor: {
        canExportNdex: true,
        canQueryNcic: true,
        canExportEtrace: true,
        canSubmitSar: true,
        canViewAuditLogs: true,
      },
      detective: {
        canExportNdex: true,
        canQueryNcic: true,
        canExportEtrace: true,
        canSubmitSar: true,
        canViewAuditLogs: false,
      },
      rtcc_analyst: {
        canExportNdex: true,
        canQueryNcic: false,
        canExportEtrace: false,
        canSubmitSar: true,
        canViewAuditLogs: false,
      },
      officer: {
        canExportNdex: false,
        canQueryNcic: false,
        canExportEtrace: false,
        canSubmitSar: false,
        canViewAuditLogs: false,
      },
    };

    setUsers(
      users.map((user) => {
        if (user.id === userId) {
          const newPerms = rolePermissions[newRole] || rolePermissions.officer;
          return {
            ...user,
            role: newRole,
            federalAccess: newRole !== "officer",
            permissions: newPerms,
          };
        }
        return user;
      })
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-2">Federal Access Control Manager</h2>
        <p className="text-gray-400">
          Manage user roles and permissions for federal data access. Only users with the
          &quot;federal_access&quot; permission can generate exports, submit SARs, or query federal systems.
          All access changes are logged per CJIS Policy Area 5.
        </p>
      </div>

      {/* Role Overview */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Role-Based Permissions</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
                <th className="pb-3">Role</th>
                <th className="pb-3 text-center">Federal Access</th>
                <th className="pb-3 text-center">N-DEx Export</th>
                <th className="pb-3 text-center">NCIC Query</th>
                <th className="pb-3 text-center">eTrace Export</th>
                <th className="pb-3 text-center">SAR Submit</th>
                <th className="pb-3 text-center">Audit Logs</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => {
                const perms =
                  role.value === "admin" || role.value === "supervisor"
                    ? { ndex: true, ncic: true, etrace: true, sar: true, audit: true }
                    : role.value === "detective"
                    ? { ndex: true, ncic: true, etrace: true, sar: true, audit: false }
                    : role.value === "rtcc_analyst"
                    ? { ndex: true, ncic: false, etrace: false, sar: true, audit: false }
                    : { ndex: false, ncic: false, etrace: false, sar: false, audit: false };

                return (
                  <tr key={role.value} className="border-b border-gray-700/50">
                    <td className="py-3">
                      <span
                        className={`px-3 py-1 rounded text-sm font-medium text-white ${role.color}`}
                      >
                        {role.label}
                      </span>
                    </td>
                    <td className="py-3 text-center">
                      {role.value !== "officer" ? (
                        <span className="text-green-400">Yes</span>
                      ) : (
                        <span className="text-red-400">No</span>
                      )}
                    </td>
                    <td className="py-3 text-center">
                      {perms.ndex ? (
                        <span className="text-green-400">Yes</span>
                      ) : (
                        <span className="text-red-400">No</span>
                      )}
                    </td>
                    <td className="py-3 text-center">
                      {perms.ncic ? (
                        <span className="text-green-400">Yes</span>
                      ) : (
                        <span className="text-red-400">No</span>
                      )}
                    </td>
                    <td className="py-3 text-center">
                      {perms.etrace ? (
                        <span className="text-green-400">Yes</span>
                      ) : (
                        <span className="text-red-400">No</span>
                      )}
                    </td>
                    <td className="py-3 text-center">
                      {perms.sar ? (
                        <span className="text-green-400">Yes</span>
                      ) : (
                        <span className="text-red-400">No</span>
                      )}
                    </td>
                    <td className="py-3 text-center">
                      {perms.audit ? (
                        <span className="text-green-400">Yes</span>
                      ) : (
                        <span className="text-red-400">No</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Management */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">User Management</h3>
        <div className="space-y-4">
          {users.map((user) => (
            <div
              key={user.id}
              className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gray-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {user.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <div>
                    <div className="font-medium text-white">{user.name}</div>
                    <div className="text-sm text-gray-400">{user.email}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Last active: {new Date(user.lastActive).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Role</label>
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {roles.map((role) => (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="text-center">
                    <label className="block text-xs text-gray-400 mb-1">Federal Access</label>
                    <button
                      onClick={() => handleToggleFederalAccess(user.id)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        user.federalAccess
                          ? "bg-green-600 text-white hover:bg-green-700"
                          : "bg-red-600 text-white hover:bg-red-700"
                      }`}
                    >
                      {user.federalAccess ? "Enabled" : "Disabled"}
                    </button>
                  </div>
                </div>
              </div>

              {/* Permissions */}
              {user.federalAccess && (
                <div className="mt-4 pt-4 border-t border-gray-600">
                  <div className="text-sm text-gray-400 mb-2">Permissions</div>
                  <div className="flex flex-wrap gap-2">
                    {permissions.map((perm) => (
                      <button
                        key={perm.key}
                        onClick={() => handleTogglePermission(user.id, perm.key)}
                        className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                          user.permissions[perm.key as keyof typeof user.permissions]
                            ? "bg-blue-600 text-white"
                            : "bg-gray-600 text-gray-300 hover:bg-gray-500"
                        }`}
                        title={perm.description}
                      >
                        {perm.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-white">{users.length}</div>
          <div className="text-sm text-gray-400">Total Users</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-green-400">
            {users.filter((u) => u.federalAccess).length}
          </div>
          <div className="text-sm text-gray-400">Federal Access</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-blue-400">
            {users.filter((u) => u.role === "supervisor" || u.role === "admin").length}
          </div>
          <div className="text-sm text-gray-400">Supervisors+</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-yellow-400">
            {users.filter((u) => u.permissions.canViewAuditLogs).length}
          </div>
          <div className="text-sm text-gray-400">Audit Access</div>
        </div>
      </div>
    </div>
  );
}
