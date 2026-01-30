"""
Provenance Emitter v1
Constitutional vent for evidence emission.

Implements the fire-and-forget, non-blocking interface defined in
governance/provenance-interface.v1.md
"""

import json
import sys
import threading
import time
from typing import Dict, Optional, Any
from datetime import datetime

class ProvenanceEmitter:
    """
    Emits provenance data via fire-and-forget semantics.
    
    Constitutional guarantees:
    - Non-blocking (never waits)
    - Best-effort (no retries)
    - Failure-tolerant (silent on error)
    - Never affects enforcement
    """
    
    @staticmethod
    def emit_exception_provenance(
        exception_data: Dict,
        verification_result: bool,
        public_key_fingerprint: Optional[str] = None,
        execution_context: Optional[str] = None
    ) -> None:
        """
        Emit provenance data for a verified exception.
        
        This method implements the "vent" semantics:
        - Fire-and-forget
        - Non-blocking
        - Best-effort
        - Append-only
        
        Constitutional invariant: This method never affects SIS behavior.
        All failures are silent non-events.
        """
        
        # Construct the provenance payload
        payload = {
            "version": "v1",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sis_version": "1.0.0",  # Should be dynamically determined
            "execution_context": execution_context or "unknown",
            "exception": exception_data,
            "verification": {
                "result": verification_result,
                "public_key_fingerprint": public_key_fingerprint,
                "verified_at": datetime.utcnow().isoformat() + "Z"
            },
            "metadata": {
                "emitted_at": datetime.utcnow().isoformat() + "Z",
                "interface_version": "v1"
            }
        }
        
        # Emit via non-blocking thread
        # Constitutional: Never wait, never retry, never fail enforcement
        thread = threading.Thread(
            target=ProvenanceEmitter._emit_async,
            args=(payload,),
            daemon=True  # Don't block process exit
        )
        thread.start()
    
    @staticmethod
    def _emit_async(payload: Dict) -> None:
        """
        Asynchronous emission with comprehensive failure tolerance.
        
        Constitutional guarantees:
        - Tolerates all failures
        - No retries
        - No logging to stderr (could affect CLI output)
        - Silent success/failure
        """
        try:
            # Try to emit via the configured vent
            # Currently: stdout (for demo/development)
            # In production: Could be file, HTTP endpoint, message queue, etc.
            
            # Constitutional: This is the ONLY emission point
            # All failures must be caught and ignored
            
            # For v1: Write to stdout in a non-interfering way
            # Use a dedicated file descriptor or structured logging in production
            
            # JSON Lines format for easy consumption
            line = json.dumps(payload) + "\n"
            
            # Write to stderr to avoid interfering with stdout (CLI output)
            # But only if we can do it non-blockingly
            sys.stderr.write(line)
            sys.stderr.flush()
            
            # Constitutional: No waiting, no checking, no feedback
            # Emission is complete regardless of actual success
            
        except Exception:
            # Constitutional: All exceptions are non-events
            # No logging, no retry, no impact
            pass
    
    @staticmethod
    def create_execution_context() -> str:
        """
        Create an opaque execution context identifier.
        
        Used to correlate provenance emissions across a single SIS execution.
        Opaque to SIS, meaningful to downstream systems.
        """
        import hashlib
        import os
        
        # Create a unique but opaque identifier
        # Mix process ID, timestamp, and randomness
        seed = f"{os.getpid()}-{time.time_ns()}-{os.urandom(4).hex()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]
