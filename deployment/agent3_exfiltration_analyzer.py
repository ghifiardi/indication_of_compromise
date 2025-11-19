#!/usr/bin/env python3
"""
Agent 3: Data Exfiltration Analyzer
Real-time detection and quantification of data extraction (>100MB outbound transfer in <1 hour)
"""

from datetime import datetime, timedelta
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataExfiltrationAnalyzer:
    """
    Detects and quantifies data exfiltration in real-time.
    
    Record Type Estimation:
    - Database credentials: 512 bytes/record
    - PII: 256 bytes/record
    - Source code: 10KB/record
    - Configuration files: 2KB/file
    - Emails: 1KB/message
    """
    
    RECORD_SIZES = {
        'database_credentials': 512,  # bytes
        'pii': 256,  # bytes
        'source_code': 10240,  # 10KB
        'config_files': 2048,  # 2KB
        'emails': 1024,  # 1KB
    }
    
    def __init__(self, config: Dict):
        self.transfer_threshold_mb = config.get('transfer_threshold_mb', 100)  # MB
        self.time_window_hours = config.get('time_window_hours', 1)  # hours
        self.confidence_threshold = config.get('confidence_threshold', 0.98)
        
    def detect_exfiltration(self, network_logs: List[Dict], prior_phases: List[Dict] = None) -> List[Dict]:
        """
        Detect data exfiltration based on outbound transfer patterns.
        
        Args:
            network_logs: List of network flow/log entries
            prior_phases: Optional list of prior phase detections
            
        Returns:
            List of exfiltration alerts
        """
        alerts = []
        current_time = datetime.now()
        time_window = timedelta(hours=self.time_window_hours)
        
        # Group transfers by source and destination
        transfers_by_source = {}
        
        for log in network_logs:
            source = log.get('source_ip')
            destination = log.get('destination_ip')
            bytes_transferred = log.get('bytes_outbound', 0)
            timestamp = datetime.fromisoformat(log.get('timestamp'))
            
            if not source or not destination or bytes_transferred == 0:
                continue
            
            # Check if within time window
            if current_time - timestamp > time_window:
                continue
            
            # Check if source is post-compromise (internal system)
            if not self._is_internal_system(source):
                continue
            
            # Check if destination is external infrastructure
            if not self._is_external_infrastructure(destination):
                continue
            
            # Aggregate transfers
            key = (source, destination)
            if key not in transfers_by_source:
                transfers_by_source[key] = {
                    'source': source,
                    'destination': destination,
                    'total_bytes': 0,
                    'transfers': [],
                    'start_time': timestamp,
                    'end_time': timestamp,
                }
            
            transfers_by_source[key]['total_bytes'] += bytes_transferred
            transfers_by_source[key]['transfers'].append(log)
            transfers_by_source[key]['end_time'] = max(
                transfers_by_source[key]['end_time'],
                timestamp
            )
        
        # Check each aggregated transfer
        for key, transfer_data in transfers_by_source.items():
            total_mb = transfer_data['total_bytes'] / (1024 * 1024)
            
            if total_mb >= self.transfer_threshold_mb:
                # Check if prior phases indicate credential harvesting + lateral movement
                has_prior_phases = self._check_prior_phases(prior_phases or [])
                
                # Calculate estimated records
                estimated_records = self._estimate_records(transfer_data['total_bytes'])
                
                alert = {
                    'source_ip': transfer_data['source'],
                    'destination_ip': transfer_data['destination'],
                    'severity': 'CRITICAL',
                    'confidence': self.confidence_threshold,
                    'total_bytes': transfer_data['total_bytes'],
                    'total_mb': total_mb,
                    'estimated_records': estimated_records,
                    'has_prior_phases': has_prior_phases,
                    'action': 'BLOCK_IMMEDIATELY',
                    'escalation': 'CISO',
                    'timestamp': datetime.now().isoformat(),
                }
                
                alerts.append(alert)
                logger.critical(
                    f"Data exfiltration detected: {total_mb:.2f} MB from {transfer_data['source']} "
                    f"to {transfer_data['destination']} (estimated {estimated_records['total']:,} records)"
                )
        
        return alerts
    
    def _is_internal_system(self, ip: str) -> bool:
        """Check if IP is an internal system (post-compromise)."""
        # Simplified: check for private IP ranges
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        first_octet = int(parts[0])
        second_octet = int(parts[1])
        
        # Private IP ranges
        if first_octet == 10:
            return True
        if first_octet == 172 and 16 <= second_octet <= 31:
            return True
        if first_octet == 192 and second_octet == 168:
            return True
        
        return False
    
    def _is_external_infrastructure(self, ip: str) -> bool:
        """Check if destination is external cloud infrastructure."""
        # Simplified: check for known cloud provider IPs or external IPs
        # In production, use IP reputation databases or cloud provider IP ranges
        
        # For now, assume non-private IPs are external
        return not self._is_internal_system(ip)
    
    def _check_prior_phases(self, prior_phases: List[Dict]) -> bool:
        """Check if prior phases indicate credential harvesting + lateral movement."""
        phase_4_detected = any(
            phase.get('current_phase') == 4 or
            'lateral movement' in str(phase).lower() or
            'credential' in str(phase).lower()
            for phase in prior_phases
        )
        return phase_4_detected
    
    def _estimate_records(self, total_bytes: int) -> Dict[str, int]:
        """Estimate number of records based on total bytes transferred."""
        estimates = {}
        
        for record_type, size_bytes in self.RECORD_SIZES.items():
            count = total_bytes // size_bytes
            estimates[record_type] = count
        
        # Total estimate (using PII as baseline)
        estimates['total'] = total_bytes // self.RECORD_SIZES['pii']
        
        return estimates


# Configuration template
DEFAULT_CONFIG = {
    'transfer_threshold_mb': 100,  # MB
    'time_window_hours': 1,  # hours
    'confidence_threshold': 0.98,  # 98%
}

if __name__ == '__main__':
    # Example usage
    analyzer = DataExfiltrationAnalyzer(DEFAULT_CONFIG)
    
    # Sample network logs (for testing)
    sample_logs = [
        {
            'source_ip': '192.168.1.100',
            'destination_ip': '52.1.2.3',  # External IP
            'bytes_outbound': 150 * 1024 * 1024,  # 150 MB
            'timestamp': datetime.now().isoformat(),
        },
    ]
    
    alerts = analyzer.detect_exfiltration(sample_logs)
    print(f"Detected {len(alerts)} exfiltration alerts")

