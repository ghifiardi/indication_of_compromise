#!/usr/bin/env python3
"""
Agent 1: Autonomous Tempo Detector
Detects impossible human operational cadence (2+ operations/second sustained >15 minutes)
"""

import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutonomousTempoDetector:
    """
    Detects autonomous activity by analyzing operational tempo patterns.
    
    Confidence Building:
    - Tempo >2 ops/sec for >15 min: +35%
    - Zero interactive sessions: +25%
    - Input/output ratio >100:1: +20%
    - 5+ simultaneous targets: +15%
    - Context persistence >12 hours: +10%
    - Coordinated tool execution: +5%
    """
    
    def __init__(self, config: Dict):
        self.tempo_threshold = config.get('tempo_threshold', 2.0)  # ops/sec
        self.duration_threshold = config.get('duration_threshold', 900)  # 15 minutes in seconds
        self.investigate_threshold = config.get('investigate_threshold', 0.70)
        self.isolate_threshold = config.get('isolate_threshold', 0.85)
        
        # Activity tracking by source IP
        self.activity_timeline = defaultdict(list)
        self.session_data = defaultdict(dict)
        
    def group_by_source_time(self, api_logs: List[Dict], window_seconds: int = 60) -> Dict:
        """
        Group API logs by source IP and time windows (60-second rolling).
        
        Args:
            api_logs: List of API log entries
            window_seconds: Time window for grouping (default 60 seconds)
            
        Returns:
            Dictionary mapping source_ip -> list of activity timelines
        """
        grouped = defaultdict(list)
        
        for log in api_logs:
            source_ip = log.get('source_ip')
            timestamp = datetime.fromisoformat(log.get('timestamp'))
            
            if source_ip:
                grouped[source_ip].append({
                    'timestamp': timestamp,
                    'endpoint': log.get('endpoint'),
                    'method': log.get('method'),
                    'input_size': log.get('input_size', 0),
                    'output_size': log.get('output_size', 0),
                })
        
        # Sort by timestamp for each source
        for source_ip in grouped:
            grouped[source_ip].sort(key=lambda x: x['timestamp'])
        
        return grouped
    
    def calculate_metrics(self, activity_timeline: List[Dict], session_logs: List[Dict] = None) -> Dict:
        """
        Calculate metrics for autonomous activity detection.
        
        Args:
            activity_timeline: List of activity entries for a source IP
            session_logs: Optional session log data
            
        Returns:
            Dictionary with calculated metrics
        """
        if not activity_timeline:
            return {'confidence': 0.0, 'is_autonomous': False}
        
        # Calculate operational tempo
        timestamps = [entry['timestamp'] for entry in activity_timeline]
        if len(timestamps) < 2:
            return {'confidence': 0.0, 'is_autonomous': False}
        
        time_span = (timestamps[-1] - timestamps[0]).total_seconds()
        if time_span == 0:
            time_span = 1  # Avoid division by zero
        
        ops_per_second = len(activity_timeline) / time_span
        
        # Check if tempo is sustained
        sustained_duration = self._check_sustained_tempo(activity_timeline)
        
        # Calculate input/output ratio
        total_input = sum(entry.get('input_size', 0) for entry in activity_timeline)
        total_output = sum(entry.get('output_size', 0) for entry in activity_timeline)
        io_ratio = total_input / total_output if total_output > 0 else 0
        
        # Count unique targets/endpoints
        unique_targets = len(set(entry.get('endpoint', '') for entry in activity_timeline))
        
        # Check for interactive sessions
        has_interactive_sessions = self._check_interactive_sessions(session_logs or [])
        
        # Check context persistence (if session data available)
        context_persistence_hours = self._check_context_persistence(activity_timeline)
        
        # Build confidence score
        confidence = 0.0
        
        # Tempo >2 ops/sec for >15 min: +35%
        if ops_per_second >= self.tempo_threshold and sustained_duration >= self.duration_threshold:
            confidence += 0.35
            logger.info(f"High tempo detected: {ops_per_second:.2f} ops/sec for {sustained_duration}s")
        
        # Zero interactive sessions: +25%
        if not has_interactive_sessions:
            confidence += 0.25
        
        # Input/output ratio >100:1: +20%
        if io_ratio > 100:
            confidence += 0.20
            logger.info(f"High I/O ratio detected: {io_ratio:.2f}:1")
        
        # 5+ simultaneous targets: +15%
        if unique_targets >= 5:
            confidence += 0.15
        
        # Context persistence >12 hours: +10%
        if context_persistence_hours >= 12:
            confidence += 0.10
        
        # Coordinated tool execution: +5% (simplified check)
        if self._check_coordinated_execution(activity_timeline):
            confidence += 0.05
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        return {
            'confidence': confidence,
            'is_autonomous': confidence >= self.investigate_threshold,
            'ops_per_second': ops_per_second,
            'sustained_duration': sustained_duration,
            'io_ratio': io_ratio,
            'unique_targets': unique_targets,
            'has_interactive_sessions': has_interactive_sessions,
            'context_persistence_hours': context_persistence_hours,
        }
    
    def _check_sustained_tempo(self, activity_timeline: List[Dict]) -> float:
        """Check if high tempo is sustained over threshold duration."""
        if len(activity_timeline) < 2:
            return 0.0
        
        timestamps = [entry['timestamp'] for entry in activity_timeline]
        time_span = (timestamps[-1] - timestamps[0]).total_seconds()
        
        # Check if we have enough activity to sustain tempo
        if time_span >= self.duration_threshold:
            ops_per_second = len(activity_timeline) / time_span
            if ops_per_second >= self.tempo_threshold:
                return time_span
        
        return 0.0
    
    def _check_interactive_sessions(self, session_logs: List[Dict]) -> bool:
        """Check if there are interactive user sessions."""
        # Look for interactive session indicators
        for log in session_logs:
            if log.get('session_type') == 'interactive':
                return True
            if log.get('user_input') and log.get('response_time', 0) > 1.0:
                return True
        return False
    
    def _check_context_persistence(self, activity_timeline: List[Dict]) -> float:
        """Check how long context has been persistent."""
        if len(activity_timeline) < 2:
            return 0.0
        
        timestamps = [entry['timestamp'] for entry in activity_timeline]
        time_span = (timestamps[-1] - timestamps[0]).total_seconds()
        return time_span / 3600  # Convert to hours
    
    def _check_coordinated_execution(self, activity_timeline: List[Dict]) -> bool:
        """Check for coordinated tool execution patterns."""
        # Simplified: check for sequential tool calls with related endpoints
        if len(activity_timeline) < 3:
            return False
        
        # Look for patterns like: scan -> analyze -> exploit
        endpoints = [entry.get('endpoint', '') for entry in activity_timeline]
        
        # Basic pattern matching
        scan_indicators = ['scan', 'discover', 'enumerate', 'nmap']
        analyze_indicators = ['analyze', 'vulnerability', 'test']
        exploit_indicators = ['exploit', 'execute', 'payload']
        
        has_scan = any(ind in str(endpoints).lower() for ind in scan_indicators)
        has_analyze = any(ind in str(endpoints).lower() for ind in analyze_indicators)
        has_exploit = any(ind in str(endpoints).lower() for ind in exploit_indicators)
        
        return has_scan and has_analyze and has_exploit
    
    def detect_autonomous_activity(self, api_logs: List[Dict], session_logs: List[Dict] = None) -> List[Dict]:
        """
        Main detection method - groups logs and detects autonomous activity.
        
        Args:
            api_logs: List of API log entries
            session_logs: Optional session log data
            
        Returns:
            List of alerts with severity and details
        """
        alerts = []
        grouped_logs = self.group_by_source_time(api_logs)
        
        for source_ip, activity_timeline in grouped_logs.items():
            # Get session logs for this source IP
            source_session_logs = [
                log for log in (session_logs or [])
                if log.get('source_ip') == source_ip
            ]
            
            metrics = self.calculate_metrics(activity_timeline, source_session_logs)
            
            if metrics['is_autonomous']:
                severity = 'CRITICAL' if metrics['confidence'] >= self.isolate_threshold else 'HIGH'
                action = 'ISOLATE' if metrics['confidence'] >= self.isolate_threshold else 'INVESTIGATE'
                
                alert = {
                    'source_ip': source_ip,
                    'severity': severity,
                    'confidence': metrics['confidence'],
                    'action': action,
                    'metrics': {
                        'ops_per_second': metrics['ops_per_second'],
                        'sustained_duration': metrics['sustained_duration'],
                        'io_ratio': metrics['io_ratio'],
                        'unique_targets': metrics['unique_targets'],
                    },
                    'timestamp': datetime.now().isoformat(),
                }
                
                alerts.append(alert)
                logger.warning(
                    f"Autonomous activity detected: {source_ip} "
                    f"(confidence: {metrics['confidence']:.2%}, action: {action})"
                )
        
        return alerts


# Configuration template
DEFAULT_CONFIG = {
    'tempo_threshold': 2.0,  # operations per second
    'duration_threshold': 900,  # 15 minutes in seconds
    'investigate_threshold': 0.70,  # 70% confidence
    'isolate_threshold': 0.85,  # 85% confidence
}

if __name__ == '__main__':
    # Example usage
    detector = AutonomousTempoDetector(DEFAULT_CONFIG)
    
    # Sample API logs (for testing)
    sample_logs = [
        {
            'source_ip': '192.168.1.100',
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'endpoint': '/api/scan',
            'method': 'POST',
            'input_size': 1000000,
            'output_size': 1000,
        },
        # Add more sample logs for testing
    ]
    
    alerts = detector.detect_autonomous_activity(sample_logs)
    print(f"Detected {len(alerts)} autonomous activity alerts")

