'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useTheme } from '@/lib/theme';
import { Camera, AlertTriangle, Activity, Eye, Zap } from 'lucide-react';

interface CameraData {
  id: string;
  name: string;
  stream_url?: string;
  snapshot_url?: string;
  camera_type?: string;
  type?: string;
  jurisdiction?: string;
  status?: string;
  sector?: string;
  description?: string;
  has_threat?: boolean;
  is_active?: boolean;
}

interface ThemedCameraTileProps {
  camera: CameraData;
  showMetadata?: boolean;
  onClick?: () => void;
  className?: string;
}

export function ThemedCameraTile({
  camera,
  showMetadata = true,
  onClick,
  className = '',
}: ThemedCameraTileProps) {
  const { theme } = useTheme();
  const [isHovered, setIsHovered] = useState(false);
  const [imageError, setImageError] = useState(false);

  const cameraType = camera.camera_type || camera.type || 'cctv';
  const hasThreat = camera.has_threat || false;
  const isActive = camera.is_active || false;

  const getCameraTypeColor = () => {
    switch (cameraType.toLowerCase()) {
      case 'lpr':
        return theme.colors.cameraLPR;
      case 'ptz':
        return theme.colors.cameraPTZ;
      default:
        if (camera.jurisdiction === 'FDOT') return theme.colors.cameraFDOT;
        return theme.colors.cameraRBPD;
    }
  };

  const typeColor = getCameraTypeColor();

  const tileStyle: React.CSSProperties = {
    background: theme.colors.backgroundSecondary,
    border: `2px solid ${hasThreat ? theme.colors.threatRed : theme.colors.authorityGold}`,
    borderRadius: '8px',
    overflow: 'hidden',
    transition: theme.enableAnimations ? 'all 0.3s ease' : 'none',
    boxShadow: hasThreat
      ? `0 0 0 1px ${theme.colors.threatRed}, 0 0 30px rgba(255, 39, 64, 0.5)`
      : isHovered
        ? `0 0 0 1px ${theme.colors.neuralBlue}, 0 0 30px rgba(30, 144, 255, 0.4)`
        : `0 0 0 1px rgba(217, 178, 82, 0.3), 0 4px 20px rgba(0, 0, 0, 0.4)`,
    transform: isHovered && theme.enableAnimations ? 'translateY(-2px)' : 'none',
  };

  const glowOverlayStyle: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    background: `radial-gradient(circle at center, ${typeColor}10 0%, transparent 70%)`,
    pointerEvents: 'none',
    opacity: isHovered ? 1 : 0.5,
    transition: theme.enableAnimations ? 'opacity 0.3s ease' : 'none',
  };

  const statusIndicatorStyle: React.CSSProperties = {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: camera.status === 'online' ? theme.colors.online : theme.colors.offline,
    boxShadow: `0 0 8px ${camera.status === 'online' ? theme.colors.online : theme.colors.offline}`,
  };

  return (
    <div
      className={`relative cursor-pointer ${className}`}
      style={tileStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {/* Particle dust background effect */}
      {theme.enableParticles && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `radial-gradient(circle at 20% 30%, ${theme.colors.neuralBlue}08 0%, transparent 50%),
                        radial-gradient(circle at 80% 70%, ${theme.colors.authorityGold}05 0%, transparent 50%)`,
          }}
        />
      )}

      {/* Video/Image container */}
      <div className="relative aspect-video">
        {!imageError && (camera.stream_url || camera.snapshot_url) ? (
          <img
            src={camera.snapshot_url || camera.stream_url}
            alt={camera.name}
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : (
          <div
            className="w-full h-full flex items-center justify-center"
            style={{ background: theme.colors.background }}
          >
            <Camera
              className="h-12 w-12"
              style={{ color: theme.colors.textMuted }}
            />
          </div>
        )}

        {/* Glow overlay */}
        <div style={glowOverlayStyle} />

        {/* Threat indicator */}
        {hasThreat && (
          <div
            className="absolute top-2 right-2 flex items-center gap-1 px-2 py-1 rounded"
            style={{
              background: `${theme.colors.threatRed}CC`,
              animation: theme.enableAnimations ? 'pulse 1.5s ease-in-out infinite' : 'none',
            }}
          >
            <AlertTriangle className="h-4 w-4 text-white" />
            <span className="text-xs font-bold text-white">THREAT</span>
          </div>
        )}

        {/* Active indicator */}
        {isActive && (
          <div
            className="absolute top-2 left-2 flex items-center gap-1 px-2 py-1 rounded"
            style={{
              background: `${theme.colors.neuralBlue}CC`,
              animation: theme.enableAnimations ? 'pulse 2s ease-in-out infinite' : 'none',
            }}
          >
            <Activity className="h-4 w-4 text-white" />
            <span className="text-xs font-bold text-white">LIVE</span>
          </div>
        )}

        {/* Camera type badge */}
        <div
          className="absolute bottom-2 left-2 px-2 py-1 rounded text-xs font-semibold"
          style={{
            background: `${typeColor}CC`,
            color: '#FFFFFF',
            boxShadow: `0 0 10px ${typeColor}`,
          }}
        >
          {cameraType.toUpperCase()}
        </div>
      </div>

      {/* Metadata panel */}
      {showMetadata && (
        <div
          className="p-3"
          style={{
            background: theme.colors.panelBackground,
            borderTop: `1px solid ${theme.colors.panelBorder}`,
          }}
        >
          <div className="flex items-center justify-between mb-1">
            <h3
              className="font-semibold text-sm truncate flex-1"
              style={{ color: theme.colors.textPrimary }}
            >
              {camera.name}
            </h3>
            <div style={statusIndicatorStyle} />
          </div>

          <div className="flex items-center gap-2 text-xs" style={{ color: theme.colors.textMuted }}>
            {camera.jurisdiction && <span>{camera.jurisdiction}</span>}
            {camera.sector && (
              <>
                <span>|</span>
                <span>{camera.sector}</span>
              </>
            )}
          </div>

          {camera.description && (
            <p
              className="text-xs mt-1 truncate"
              style={{ color: theme.colors.textSecondary }}
            >
              {camera.description}
            </p>
          )}

          {/* Action buttons */}
          <div className="flex items-center gap-2 mt-2">
            <Link
              href={`/cameras/${camera.id}`}
              className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors"
              style={{
                background: `${theme.colors.neuralBlue}20`,
                color: theme.colors.neuralBlue,
                border: `1px solid ${theme.colors.neuralBlue}40`,
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <Eye className="h-3 w-3" />
              View
            </Link>
            <button
              className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors"
              style={{
                background: `${theme.colors.authorityGold}20`,
                color: theme.colors.authorityGold,
                border: `1px solid ${theme.colors.authorityGold}40`,
              }}
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              <Zap className="h-3 w-3" />
              PTZ
            </button>
          </div>
        </div>
      )}

      {/* Cosmic pulse animation on activation */}
      {isActive && theme.enableAnimations && (
        <div
          className="absolute inset-0 pointer-events-none rounded-lg"
          style={{
            border: `2px solid ${theme.colors.neuralBlue}`,
            animation: 'cosmicPulse 2s infinite',
          }}
        />
      )}
    </div>
  );
}

export default ThemedCameraTile;
