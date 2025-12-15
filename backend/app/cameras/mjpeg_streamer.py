"""
MJPEG Streamer Module for FDOT Cameras

Provides simulated live video streaming by refreshing FDOT snapshots
at a configurable rate and serving them as an MJPEG stream.
"""

import asyncio
from typing import AsyncGenerator

import httpx


async def fetch_snapshot(url: str) -> bytes:
    """Fetch a snapshot image from the given URL."""
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10.0)
        return res.content


class MJPEGStreamer:
    """
    MJPEG Streamer that creates a pseudo-live video stream
    by continuously fetching and serving snapshots.
    """
    
    def __init__(self, snapshot_url: str, refresh_rate: float = 1.0):
        """
        Initialize the MJPEG streamer.
        
        Args:
            snapshot_url: URL to fetch snapshot images from
            refresh_rate: Time in seconds between frame refreshes (default: 1.0)
        """
        self.snapshot_url = snapshot_url
        self.refresh_rate = refresh_rate

    async def stream(self) -> AsyncGenerator[bytes, None]:
        """
        Generate an MJPEG stream by continuously fetching snapshots.
        
        Yields:
            bytes: MJPEG frame data with proper headers
        """
        boundary = "frameboundary"
        yield f"--{boundary}\r\n".encode("utf-8")

        while True:
            try:
                img = await fetch_snapshot(self.snapshot_url)
                yield (
                    f"Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(img)}\r\n\r\n"
                ).encode("utf-8") + img + f"\r\n--{boundary}\r\n".encode("utf-8")

                await asyncio.sleep(self.refresh_rate)
            except Exception:
                await asyncio.sleep(self.refresh_rate)
                continue
