#!/usr/bin/env python3
"""
Log Ingestion Pipeline Test
Tests the log ingestion pipeline with sample data
"""

import json
import requests
from datetime import datetime
from typing import Dict, List
import yaml

class LogIngestionTester:
    """Tests log ingestion pipeline"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def create_test_logs(self, count: int = 10) -> List[Dict]:
        """Create sample test logs"""
        logs = []
        base_time = datetime.now()
        
        for i in range(count):
            log = {
                'timestamp': (base_time.replace(microsecond=0)).isoformat() + 'Z',
                'source_ip': f'192.168.1.{100 + i}',
                'endpoint': f'/api/test/{i}',
                'method': 'GET',
                'status_code': 200,
                'response_time_ms': 50 + i,
                'user_agent': 'GATRA-Test-Client/1.0',
                'bytes_sent': 1024 + i * 100,
                'bytes_received': 512 + i * 50,
            }
            logs.append(log)
        
        return logs
    
    def test_elasticsearch_ingestion(self, endpoint: str, index: str = "gatra-test") -> bool:
        """Test Elasticsearch ingestion"""
        print(f"\nTesting Elasticsearch ingestion: {endpoint}")
        
        test_logs = self.create_test_logs(5)
        
        try:
            # Test single document ingestion
            url = f"{endpoint}/{index}/_doc"
            response = requests.post(
                url,
                json=test_logs[0],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"  ✓ Single document ingestion: Success")
                
                # Test bulk ingestion
                bulk_data = []
                for log in test_logs[1:]:
                    bulk_data.append(json.dumps({"index": {}}))
                    bulk_data.append(json.dumps(log))
                
                bulk_url = f"{endpoint}/{index}/_bulk"
                bulk_payload = "\n".join(bulk_data) + "\n"
                
                bulk_response = requests.post(
                    bulk_url,
                    data=bulk_payload,
                    headers={'Content-Type': 'application/x-ndjson'},
                    timeout=10
                )
                
                if bulk_response.status_code == 200:
                    print(f"  ✓ Bulk ingestion: Success")
                    
                    # Verify retrieval
                    import time
                    time.sleep(2)  # Wait for indexing
                    
                    search_url = f"{endpoint}/{index}/_search"
                    search_response = requests.get(
                        search_url,
                        params={'q': f'source_ip:{test_logs[0]["source_ip"]}'},
                        timeout=10
                    )
                    
                    if search_response.status_code == 200:
                        results = search_response.json()
                        hits = results.get('hits', {}).get('total', {}).get('value', 0)
                        print(f"  ✓ Document retrieval: {hits} documents found")
                        return True
                    else:
                        print(f"  ✗ Document retrieval: Failed")
                        return False
                else:
                    print(f"  ✗ Bulk ingestion: Failed ({bulk_response.status_code})")
                    return False
            else:
                print(f"  ✗ Single document ingestion: Failed ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
    
    def test_kafka_ingestion(self, brokers: List[str], topic: str = "gatra-test") -> bool:
        """Test Kafka ingestion (requires kafka-python library)"""
        print(f"\nTesting Kafka ingestion: {brokers}")
        
        try:
            from kafka import KafkaProducer, KafkaConsumer
            from kafka.errors import KafkaError
            
            # Create producer
            producer = KafkaProducer(
                bootstrap_servers=brokers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            # Send test message
            test_log = self.create_test_logs(1)[0]
            future = producer.send(topic, test_log)
            
            try:
                record_metadata = future.get(timeout=10)
                print(f"  ✓ Message sent: Topic={record_metadata.topic}, Partition={record_metadata.partition}, Offset={record_metadata.offset}")
                
                # Verify consumption
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=brokers,
                    auto_offset_reset='earliest',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    consumer_timeout_ms=5000
                )
                
                messages = list(consumer)
                if messages:
                    print(f"  ✓ Message consumed: {len(messages)} message(s) retrieved")
                    return True
                else:
                    print(f"  ✗ Message consumption: No messages found")
                    return False
                    
            except KafkaError as e:
                print(f"  ✗ Kafka error: {str(e)}")
                return False
            finally:
                producer.close()
                
        except ImportError:
            print(f"  ⚠ kafka-python library not installed")
            print(f"     Install with: pip install kafka-python")
            return None
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
    
    def run_tests(self):
        """Run all ingestion tests"""
        print("=" * 60)
        print("Log Ingestion Pipeline Test")
        print("=" * 60)
        
        # Test Elasticsearch if configured
        infra_config = self.config.get('infrastructure', {})
        log_agg = infra_config.get('log_aggregation', {})
        
        if log_agg.get('type') == 'elasticsearch':
            endpoint = log_agg.get('endpoint', '')
            if endpoint:
                index = log_agg.get('indices', ['gatra-test'])[0]
                self.test_elasticsearch_ingestion(endpoint, index)
        
        # Test Kafka if configured
        streaming = infra_config.get('streaming', {})
        if streaming.get('type') == 'kafka':
            brokers = streaming.get('brokers', [])
            if brokers:
                topic = streaming.get('topics', ['gatra-test'])[0]
                self.test_kafka_ingestion(brokers, topic)
        
        print("\n" + "=" * 60)
        print("Ingestion Test Complete")
        print("=" * 60)


if __name__ == '__main__':
    tester = LogIngestionTester()
    tester.run_tests()

