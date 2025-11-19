#!/usr/bin/env python3
"""
GATRA Testing Framework
Validates agent deployments and detection capabilities
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List

# Import agents
sys.path.append('.')
from agent1_tempo_detector import AutonomousTempoDetector, DEFAULT_CONFIG as CONFIG1
from agent2_phase_tracker import AttackPhaseTracker, DEFAULT_CONFIG as CONFIG2
from agent3_exfiltration_analyzer import DataExfiltrationAnalyzer, DEFAULT_CONFIG as CONFIG3


class GATRATestFramework:
    """Test framework for GATRA agents"""
    
    def __init__(self):
        self.agent1 = AutonomousTempoDetector(CONFIG1)
        self.agent2 = AttackPhaseTracker(CONFIG2)
        self.agent3 = DataExfiltrationAnalyzer(CONFIG3)
        self.test_results = []
    
    def test_agent1_high_tempo(self) -> Dict:
        """Test Agent 1: High tempo detection"""
        print("\n[TEST] Agent 1: High Tempo Detection")
        
        # Create synthetic high-tempo attack logs
        base_time = datetime.now() - timedelta(minutes=20)
        logs = []
        
        for i in range(2000):  # 2000 operations over 20 minutes = ~1.67 ops/sec
            logs.append({
                'source_ip': '192.168.1.100',
                'timestamp': (base_time + timedelta(seconds=i*0.6)).isoformat(),
                'endpoint': f'/api/scan/{i}',
                'method': 'POST',
                'input_size': 1000000,
                'output_size': 1000,
            })
        
        alerts = self.agent1.detect_autonomous_activity(logs)
        
        result = {
            'test': 'agent1_high_tempo',
            'passed': len(alerts) > 0,
            'alerts_count': len(alerts),
            'details': alerts[0] if alerts else None,
        }
        
        print(f"  Result: {'PASS' if result['passed'] else 'FAIL'}")
        if alerts:
            print(f"  Confidence: {alerts[0]['confidence']:.2%}")
            print(f"  Action: {alerts[0]['action']}")
        
        return result
    
    def test_agent2_phase_detection(self) -> Dict:
        """Test Agent 2: Phase 2 detection"""
        print("\n[TEST] Agent 2: Phase 2 Detection")
        
        logs = [
            {
                'endpoint': '/api/scan',
                'method': 'POST',
                'description': 'Service discovery scan - 100+ services enumerated',
            },
            {
                'endpoint': '/api/dns',
                'method': 'GET',
                'description': 'DNS zone transfer and subdomain brute-force',
            },
            {
                'endpoint': '/api/webapp',
                'method': 'POST',
                'description': 'Web application parameter fuzzing',
            },
        ]
        
        result_phase = self.agent2.detect_phase_progression(logs)
        
        result = {
            'test': 'agent2_phase2_detection',
            'passed': result_phase.get('current_phase') == 2,
            'detected_phase': result_phase.get('current_phase'),
            'confidence': result_phase.get('confidence', 0),
            'details': result_phase,
        }
        
        print(f"  Result: {'PASS' if result['passed'] else 'FAIL'}")
        print(f"  Detected Phase: {result['detected_phase']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        
        return result
    
    def test_agent3_exfiltration(self) -> Dict:
        """Test Agent 3: Data exfiltration detection"""
        print("\n[TEST] Agent 3: Data Exfiltration Detection")
        
        logs = [
            {
                'source_ip': '192.168.1.100',
                'destination_ip': '52.1.2.3',
                'bytes_outbound': 150 * 1024 * 1024,  # 150 MB
                'timestamp': datetime.now().isoformat(),
            },
        ]
        
        alerts = self.agent3.detect_exfiltration(logs)
        
        result = {
            'test': 'agent3_exfiltration',
            'passed': len(alerts) > 0,
            'alerts_count': len(alerts),
            'total_mb': alerts[0]['total_mb'] if alerts else 0,
            'estimated_records': alerts[0].get('estimated_records', {}) if alerts else {},
        }
        
        print(f"  Result: {'PASS' if result['passed'] else 'FAIL'}")
        if alerts:
            print(f"  Total MB: {result['total_mb']:.2f}")
            print(f"  Estimated Records: {result['estimated_records'].get('total', 0):,}")
        
        return result
    
    def run_all_tests(self) -> Dict:
        """Run all test scenarios"""
        print("=" * 50)
        print("GATRA Test Framework")
        print("Running all test scenarios...")
        print("=" * 50)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {},
        }
        
        # Run tests
        test1 = self.test_agent1_high_tempo()
        results['tests'].append(test1)
        
        test2 = self.test_agent2_phase_detection()
        results['tests'].append(test2)
        
        test3 = self.test_agent3_exfiltration()
        results['tests'].append(test3)
        
        # Summary
        passed = sum(1 for t in results['tests'] if t['passed'])
        total = len(results['tests'])
        
        results['summary'] = {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': passed / total if total > 0 else 0,
        }
        
        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed']}")
        print(f"Failed: {results['summary']['failed']}")
        print(f"Pass Rate: {results['summary']['pass_rate']:.2%}")
        print("=" * 50)
        
        return results


if __name__ == '__main__':
    framework = GATRATestFramework()
    results = framework.run_all_tests()
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nTest results saved to test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if results['summary']['pass_rate'] == 1.0 else 1)

