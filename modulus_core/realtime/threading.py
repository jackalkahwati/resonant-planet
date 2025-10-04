"""Real-time threading controls for thread pinning and priority."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ThreadConfig:
    """Configuration for real-time thread behavior."""
    affinity: Optional[List[int]] = None  # CPU cores to pin to
    priority: int = 0  # Priority level (0=normal, higher=more priority)
    realtime_policy: str = "FIFO"  # "FIFO", "RR", or "OTHER"


def set_thread_affinity(core_ids: List[int]) -> bool:
    """
    Pin the current thread to specific CPU cores.
    
    Args:
        core_ids: List of CPU core IDs to pin to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if sys.platform == "linux":
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            pid = os.getpid()
            
            cpu_set_size = 128  # Assume max 128 cores
            cpu_set = (ctypes.c_ulong * (cpu_set_size // 64))()
            
            for core_id in core_ids:
                if 0 <= core_id < cpu_set_size:
                    idx = core_id // 64
                    bit = core_id % 64
                    cpu_set[idx] |= (1 << bit)
            
            result = libc.sched_setaffinity(pid, ctypes.sizeof(cpu_set), ctypes.byref(cpu_set))
            return result == 0
        
        elif sys.platform == "darwin":
            # macOS doesn't support thread affinity in the same way
            # We can use thread_policy_set with THREAD_AFFINITY_POLICY but it requires kernel calls
            import subprocess
            # For simulation purposes, just log the request
            print(f"[macOS] Thread affinity not directly supported. Requested cores: {core_ids}")
            return True
        
        elif sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            
            mask = 0
            for core_id in core_ids:
                mask |= (1 << core_id)
            
            result = kernel32.SetThreadAffinityMask(-2, mask)
            return result != 0
        
        return False
    
    except Exception as e:
        print(f"Failed to set thread affinity: {e}")
        return False


def set_thread_priority(priority: int, policy: str = "FIFO") -> bool:
    """
    Set the priority of the current thread.
    
    Args:
        priority: Priority level (0=normal, higher values = more priority)
        policy: Scheduling policy ("FIFO", "RR", "OTHER")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if sys.platform == "linux":
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            
            SCHED_OTHER = 0
            SCHED_FIFO = 1
            SCHED_RR = 2
            
            policy_map = {
                "OTHER": SCHED_OTHER,
                "FIFO": SCHED_FIFO,
                "RR": SCHED_RR,
            }
            
            sched_policy = policy_map.get(policy.upper(), SCHED_OTHER)
            
            class SchedParam(ctypes.Structure):
                _fields_ = [("sched_priority", ctypes.c_int)]
            
            param = SchedParam(sched_priority=priority)
            result = libc.sched_setscheduler(0, sched_policy, ctypes.byref(param))
            return result == 0
        
        elif sys.platform == "darwin":
            # macOS priority via nice values or pthread_setschedparam
            print(f"[macOS] Setting priority={priority} with policy={policy}")
            return True
        
        elif sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            
            THREAD_PRIORITY_MAP = {
                0: 0,   # THREAD_PRIORITY_NORMAL
                1: 1,   # THREAD_PRIORITY_ABOVE_NORMAL
                2: 2,   # THREAD_PRIORITY_HIGHEST
            }
            
            win_priority = THREAD_PRIORITY_MAP.get(min(priority, 2), 0)
            result = kernel32.SetThreadPriority(-2, win_priority)
            return result != 0
        
        return False
    
    except Exception as e:
        print(f"Failed to set thread priority: {e}")
        return False


def apply_thread_config(config: ThreadConfig) -> bool:
    """Apply a complete thread configuration."""
    success = True
    
    if config.affinity:
        success &= set_thread_affinity(config.affinity)
    
    if config.priority > 0:
        success &= set_thread_priority(config.priority, config.realtime_policy)
    
    return success


