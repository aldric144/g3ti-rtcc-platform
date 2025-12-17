"""
FDOT HLS/MPEG-TS Stream Proxy.

Implements a safe passthrough relay for HLS/MPEG-TS streams.
Uses aiohttp for async proxying without blocking the main thread.
Does NOT store video or perform transcoding.
"""

from typing import AsyncGenerator, Optional
import asyncio

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import httpx
except ImportError:
    httpx = None

from app.fdot_streams.fdot_catalog import get_camera_by_id, get_stream_url


PROXY_TIMEOUT = 30.0
CHUNK_SIZE = 8192


async def proxy_stream_aiohttp(stream_url: str) -> AsyncGenerator[bytes, None]:
    if aiohttp is None:
        yield b""
        return
    
    timeout = aiohttp.ClientTimeout(total=PROXY_TIMEOUT, connect=10.0)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                stream_url,
                headers={
                    "User-Agent": "G3TI-RTCC-UIP/1.0 (FDOT Stream Proxy)"
                }
            ) as response:
                if response.status != 200:
                    yield b""
                    return
                
                async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                    yield chunk
                    
    except asyncio.TimeoutError:
        yield b""
    except aiohttp.ClientError:
        yield b""
    except Exception:
        yield b""


async def proxy_stream_httpx(stream_url: str) -> AsyncGenerator[bytes, None]:
    if httpx is None:
        yield b""
        return
    
    try:
        async with httpx.AsyncClient(
            timeout=PROXY_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": "G3TI-RTCC-UIP/1.0 (FDOT Stream Proxy)"
            }
        ) as client:
            async with client.stream("GET", stream_url) as response:
                if response.status_code != 200:
                    yield b""
                    return
                
                async for chunk in response.aiter_bytes(CHUNK_SIZE):
                    yield chunk
                    
    except httpx.TimeoutException:
        yield b""
    except httpx.HTTPError:
        yield b""
    except Exception:
        yield b""


async def proxy_camera_stream(camera_id: str) -> AsyncGenerator[bytes, None]:
    stream_url = get_stream_url(camera_id)
    
    if not stream_url:
        yield b""
        return
    
    if aiohttp is not None:
        async for chunk in proxy_stream_aiohttp(stream_url):
            yield chunk
    elif httpx is not None:
        async for chunk in proxy_stream_httpx(stream_url):
            yield chunk
    else:
        yield b""


async def get_stream_content_type(camera_id: str) -> str:
    stream_url = get_stream_url(camera_id)
    
    if not stream_url:
        return "application/octet-stream"
    
    if stream_url.endswith(".m3u8"):
        return "application/vnd.apple.mpegurl"
    elif stream_url.endswith(".ts"):
        return "video/mp2t"
    elif stream_url.endswith(".mp4"):
        return "video/mp4"
    else:
        return "application/octet-stream"


async def fetch_snapshot(camera_id: str) -> Optional[bytes]:
    stream_url = get_stream_url(camera_id)
    
    if not stream_url:
        return None
    
    try:
        if httpx is not None:
            async with httpx.AsyncClient(
                timeout=10.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "G3TI-RTCC-UIP/1.0 (FDOT Stream Proxy)"
                }
            ) as client:
                response = await client.get(stream_url)
                if response.status_code == 200:
                    return response.content
        elif aiohttp is not None:
            timeout = aiohttp.ClientTimeout(total=10.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    stream_url,
                    headers={
                        "User-Agent": "G3TI-RTCC-UIP/1.0 (FDOT Stream Proxy)"
                    }
                ) as response:
                    if response.status == 200:
                        return await response.read()
    except Exception:
        pass
    
    return None
