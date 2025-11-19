#!/usr/bin/env python3
"""
Data Source Verification Script
Verifies connectivity and configuration for all 7 telemetry sources
"""

import sys
import json
import requests
import socket
from datetime import datetime
from typing import Dict, List, Tuple
import yaml

class DataSourceVerifier:
    """Verifies all 7 telemetry sources"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'sources': {},
            'summary': {},
        }
    
    def load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found: {self.config_file}")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def verify_elasticsearch(self, endpoint: str) -> Tuple[bool, str]:
        """Verify Elasticsearch connectivity"""
        try:
            url = f"{endpoint}/_cluster/health"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                health = response.json()
                status = health.get('status', 'unknown')
                return True, f"Connected - Status: {status}"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def verify_kafka(self, brokers: List[str]) -> Tuple[bool, str]:
        """Verify Kafka connectivity"""
        results = []
        for broker in brokers:
            try:
                host, port = broker.split(':')
                port = int(port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    results.append(f"{broker}: Connected")
                else:
                    results.append(f"{broker}: Failed")
            except Exception as e:
                results.append(f"{broker}: Error - {str(e)}")
        
        all_connected = all("Connected" in r for r in results)
        return all_connected, "; ".join(results)
    
    def verify_syslog(self, endpoint: str) -> Tuple[bool, str]:
        """Verify Syslog connectivity"""
        try:
            # Parse endpoint (e.g., syslog://host:port)
            if endpoint.startswith('syslog://'):
                endpoint = endpoint.replace('syslog://', '')
            
            host, port = endpoint.split(':')
            port = int(port)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return True, f"Connected to {host}:{port}"
            else:
                return False, f"Connection failed to {host}:{port}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verify_netflow(self, endpoint: str) -> Tuple[bool, str]:
        """Verify NetFlow collector connectivity"""
        try:
            host, port = endpoint.split(':')
            port = int(port)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return True, f"Connected to {host}:{port}"
            else:
                return False, f"Connection failed to {host}:{port}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verify_database(self, endpoint: str) -> Tuple[bool, str]:
        """Verify database connectivity (placeholder)"""
        # This would require database-specific libraries
        # For now, return manual verification required
        return None, "Manual verification required - check database connection"
    
    def verify_cloud_api(self, endpoint: str) -> Tuple[bool, str]:
        """Verify cloud API connectivity (placeholder)"""
        # Cloud APIs require specific SDKs and authentication
        return None, "Manual verification required - check cloud API access"
    
    def verify_all_sources(self) -> Dict:
        """Verify all 7 telemetry sources"""
        print("=" * 60)
        print("Verifying All 7 Telemetry Sources")
        print("=" * 60)
        
        data_collection = self.config.get('data_collection', {})
        
        # Source 1: API Audit Logs
        print("\n[1/7] API Audit Logs")
        api_config = data_collection.get('api_audit_logs', {})
        source = api_config.get('source', '')
        if source.startswith('elasticsearch://'):
            endpoint = source.replace('elasticsearch://', 'http://')
            success, message = self.verify_elasticsearch(endpoint)
            self.results['sources']['api_audit_logs'] = {
                'enabled': api_config.get('enabled', False),
                'status': 'connected' if success else 'failed',
                'message': message,
            }
            print(f"  Status: {'✓' if success else '✗'} {message}")
        else:
            print(f"  Status: ⚠ Manual verification required")
            self.results['sources']['api_audit_logs'] = {
                'enabled': api_config.get('enabled', False),
                'status': 'manual',
                'message': 'Manual verification required',
            }
        
        # Source 2: Network Flow Data
        print("\n[2/7] Network Flow Data")
        netflow_config = data_collection.get('network_flow_data', {})
        source = netflow_config.get('source', '')
        if source.startswith('netflow://'):
            endpoint = source.replace('netflow://', '')
            success, message = self.verify_netflow(endpoint)
            self.results['sources']['network_flow_data'] = {
                'enabled': netflow_config.get('enabled', False),
                'status': 'connected' if success else 'failed',
                'message': message,
            }
            print(f"  Status: {'✓' if success else '✗'} {message}")
        else:
            print(f"  Status: ⚠ Manual verification required")
            self.results['sources']['network_flow_data'] = {
                'enabled': netflow_config.get('enabled', False),
                'status': 'manual',
                'message': 'Manual verification required',
            }
        
        # Source 3: Database Audit Logs
        print("\n[3/7] Database Audit Logs")
        db_config = data_collection.get('database_audit_logs', {})
        sources = db_config.get('sources', [])
        if sources:
            success, message = self.verify_database(sources[0])
            self.results['sources']['database_audit_logs'] = {
                'enabled': db_config.get('enabled', False),
                'status': 'manual',
                'message': message,
            }
            print(f"  Status: ⚠ {message}")
        else:
            print(f"  Status: ⚠ Not configured")
            self.results['sources']['database_audit_logs'] = {
                'enabled': False,
                'status': 'not_configured',
                'message': 'Not configured',
            }
        
        # Source 4: Authentication/Authorization Logs
        print("\n[4/7] Authentication/Authorization Logs")
        auth_config = data_collection.get('auth_logs', {})
        sources = auth_config.get('sources', [])
        if sources:
            source = sources[0]
            success, message = self.verify_syslog(source)
            self.results['sources']['auth_logs'] = {
                'enabled': auth_config.get('enabled', False),
                'status': 'connected' if success else 'failed',
                'message': message,
            }
            print(f"  Status: {'✓' if success else '✗'} {message}")
        else:
            print(f"  Status: ⚠ Not configured")
            self.results['sources']['auth_logs'] = {
                'enabled': False,
                'status': 'not_configured',
                'message': 'Not configured',
            }
        
        # Source 5: File System Access Logs
        print("\n[5/7] File System Access Logs")
        fs_config = data_collection.get('file_system_logs', {})
        source = fs_config.get('source', '')
        if source:
            self.results['sources']['file_system_logs'] = {
                'enabled': fs_config.get('enabled', False),
                'status': 'manual',
                'message': 'Manual verification required (filebeat)',
            }
            print(f"  Status: ⚠ Manual verification required")
        else:
            print(f"  Status: ⚠ Not configured")
            self.results['sources']['file_system_logs'] = {
                'enabled': False,
                'status': 'not_configured',
                'message': 'Not configured',
            }
        
        # Source 6: Interactive Session Logs
        print("\n[6/7] Interactive Session Logs")
        session_config = data_collection.get('session_logs', {})
        source = session_config.get('source', '')
        if source.startswith('kafka://'):
            # Extract Kafka brokers from config
            infra_config = self.config.get('infrastructure', {})
            streaming_config = infra_config.get('streaming', {})
            brokers = streaming_config.get('brokers', [])
            if brokers:
                success, message = self.verify_kafka(brokers)
                self.results['sources']['session_logs'] = {
                    'enabled': session_config.get('enabled', False),
                    'status': 'connected' if success else 'failed',
                    'message': message,
                }
                print(f"  Status: {'✓' if success else '✗'} {message}")
            else:
                print(f"  Status: ⚠ Kafka brokers not configured")
                self.results['sources']['session_logs'] = {
                    'enabled': False,
                    'status': 'not_configured',
                    'message': 'Kafka brokers not configured',
                }
        else:
            print(f"  Status: ⚠ Manual verification required")
            self.results['sources']['session_logs'] = {
                'enabled': session_config.get('enabled', False),
                'status': 'manual',
                'message': 'Manual verification required',
            }
        
        # Source 7: Cloud API Audit Logs
        print("\n[7/7] Cloud API Audit Logs")
        cloud_config = data_collection.get('cloud_api_logs', {})
        sources = cloud_config.get('sources', [])
        if sources:
            success, message = self.verify_cloud_api(sources[0])
            self.results['sources']['cloud_api_logs'] = {
                'enabled': cloud_config.get('enabled', False),
                'status': 'manual',
                'message': message,
            }
            print(f"  Status: ⚠ {message}")
        else:
            print(f"  Status: ⚠ Not configured")
            self.results['sources']['cloud_api_logs'] = {
                'enabled': False,
                'status': 'not_configured',
                'message': 'Not configured',
            }
        
        # Calculate summary
        total = len(self.results['sources'])
        connected = sum(1 for s in self.results['sources'].values() if s['status'] == 'connected')
        failed = sum(1 for s in self.results['sources'].values() if s['status'] == 'failed')
        manual = sum(1 for s in self.results['sources'].values() if s['status'] == 'manual')
        not_configured = sum(1 for s in self.results['sources'].values() if s['status'] == 'not_configured')
        
        self.results['summary'] = {
            'total': total,
            'connected': connected,
            'failed': failed,
            'manual': manual,
            'not_configured': not_configured,
        }
        
        print("\n" + "=" * 60)
        print("Verification Summary")
        print("=" * 60)
        print(f"Total Sources: {total}")
        print(f"Connected: {connected} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Manual Verification: {manual} ⚠")
        print(f"Not Configured: {not_configured} ⚠")
        print("=" * 60)
        
        return self.results
    
    def save_results(self, filename: str = "data_source_verification.json"):
        """Save verification results to file"""
        import os
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {filename}")


if __name__ == '__main__':
    verifier = DataSourceVerifier()
    results = verifier.verify_all_sources()
    verifier.save_results()
    
    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        sys.exit(1)
    elif results['summary']['connected'] == results['summary']['total']:
        sys.exit(0)
    else:
        sys.exit(2)  # Partial success (some manual verification needed)

