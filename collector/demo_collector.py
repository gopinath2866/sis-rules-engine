#!/usr/bin/env python3
"""
Demo Provenance Collector v1

A simple collector that demonstrates the SKU concept.
Listens to stderr (where SIS emits provenance), stores JSON lines,
and provides basic query capabilities.

Constitutional: This never affects SIS behavior.
"""

import sys
import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

class ProvenanceCollector:
    def __init__(self, db_path="provenance.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for provenance storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS provenance_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sis_version TEXT,
                execution_context TEXT,
                exception_id TEXT,
                rule_id TEXT,
                target TEXT,
                signer_identity TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                verification_result BOOLEAN,
                raw_data TEXT
            )
        ''')
        
        # Create indexes for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_exception_id ON provenance_events(exception_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rule_id ON provenance_events(rule_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_target ON provenance_events(target)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signer ON provenance_events(signer_identity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON provenance_events(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON provenance_events(expires_at)')
        
        conn.commit()
        conn.close()
    
    def ingest_line(self, line: str):
        """Ingest a single JSON line from SIS provenance vent."""
        try:
            data = json.loads(line.strip())
            
            # Extract fields for easy querying
            exception = data.get('exception', {})
            verification = data.get('verification', {})
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO provenance_events 
                (sis_version, execution_context, exception_id, rule_id, target, 
                 signer_identity, created_at, expires_at, verification_result, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('sis_version'),
                data.get('execution_context'),
                exception.get('exception_id'),
                exception.get('rule_id'),
                exception.get('target'),
                exception.get('signature', {}).get('signer_identity'),
                exception.get('created_at'),
                exception.get('expires_at'),
                verification.get('result'),
                line.strip()  # Store raw JSON for completeness
            ))
            
            conn.commit()
            conn.close()
            
            print(f"[Collector] Ingested event: {exception.get('exception_id')}", file=sys.stderr)
            
        except json.JSONDecodeError:
            # Constitutional: Ignore malformed lines without affecting anything
            pass
        except Exception as e:
            # Constitutional: All failures are non-events
            # In production, would log to monitoring system
            pass
    
    def query(self, rule_id=None, target=None, signer=None, start_date=None, end_date=None):
        """Query provenance events with filters."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM provenance_events WHERE 1=1"
        params = []
        
        if rule_id:
            query += " AND rule_id = ?"
            params.append(rule_id)
        
        if target:
            query += " AND target = ?"
            params.append(target)
        
        if signer:
            query += " AND signer_identity = ?"
            params.append(signer)
        
        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)
        
        query += " ORDER BY received_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def export_json(self, output_path="provenance_export.json"):
        """Export all events as JSON for audit purposes."""
        events = self.query()
        with open(output_path, 'w') as f:
            json.dump({
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "total_events": len(events),
                "events": events
            }, f, indent=2)
        return output_path

def main():
    """Run the collector, reading from stdin (piped from SIS stderr)."""
    collector = ProvenanceCollector()
    
    print("🔍 Provenance Collector v1 started", file=sys.stderr)
    print("Listening for SIS provenance events...", file=sys.stderr)
    print("Press Ctrl+C to exit", file=sys.stderr)
    
    try:
        # Read lines from stdin (where SIS stderr is redirected)
        for line in sys.stdin:
            collector.ingest_line(line)
    except KeyboardInterrupt:
        print("\nCollector stopped", file=sys.stderr)
    except Exception as e:
        # Constitutional: Collector failure doesn't affect anything
        print(f"Collector error (non-critical): {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
