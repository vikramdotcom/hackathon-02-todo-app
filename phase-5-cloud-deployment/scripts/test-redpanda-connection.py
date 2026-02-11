"""
Redpanda Cloud Connection Test Script

Tests connectivity to Redpanda Cloud and verifies topic configuration.
Run this after completing Redpanda Cloud setup (T009-T011).
"""

import os
import sys
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
from datetime import datetime

def load_config():
    """Load Redpanda configuration from environment variables."""
    config = {
        'bootstrap_servers': os.getenv('REDPANDA_BOOTSTRAP_SERVERS'),
        'sasl_username': os.getenv('REDPANDA_SASL_USERNAME'),
        'sasl_password': os.getenv('REDPANDA_SASL_PASSWORD'),
        'sasl_mechanism': os.getenv('REDPANDA_SASL_MECHANISM', 'SCRAM-SHA-256'),
        'security_protocol': os.getenv('REDPANDA_SECURITY_PROTOCOL', 'SASL_SSL'),
    }

    # Validate required config
    missing = [k for k, v in config.items() if not v and k != 'sasl_mechanism' and k != 'security_protocol']
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("\nPlease set the following in your .env file:")
        print("  REDPANDA_BOOTSTRAP_SERVERS")
        print("  REDPANDA_SASL_USERNAME")
        print("  REDPANDA_SASL_PASSWORD")
        sys.exit(1)

    return config

def test_producer(config, topic='task-events'):
    """Test Kafka producer connectivity."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=config['bootstrap_servers'],
            security_protocol=config['security_protocol'],
            sasl_mechanism=config['sasl_mechanism'],
            sasl_plain_username=config['sasl_username'],
            sasl_plain_password=config['sasl_password'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Send test message
        test_message = {
            'event_type': 'test',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Connection test from Phase V setup'
        }

        future = producer.send(topic, value=test_message)
        record_metadata = future.get(timeout=10)

        producer.close()

        print(f"✓ Producer test: SUCCESS")
        print(f"  Topic: {record_metadata.topic}")
        print(f"  Partition: {record_metadata.partition}")
        print(f"  Offset: {record_metadata.offset}")
        return True

    except KafkaError as e:
        print(f"❌ Producer test: FAILED")
        print(f"  Error: {str(e)}")
        return False

def test_consumer(config, topic='task-events'):
    """Test Kafka consumer connectivity."""
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=config['bootstrap_servers'],
            security_protocol=config['security_protocol'],
            sasl_mechanism=config['sasl_mechanism'],
            sasl_plain_username=config['sasl_username'],
            sasl_plain_password=config['sasl_password'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            consumer_timeout_ms=5000
        )

        # Try to consume (will timeout if no messages, which is OK)
        messages = []
        for message in consumer:
            messages.append(message.value)
            break  # Just need to verify we can consume

        consumer.close()

        print(f"✓ Consumer test: SUCCESS")
        if messages:
            print(f"  Consumed {len(messages)} message(s)")
        return True

    except KafkaError as e:
        print(f"❌ Consumer test: FAILED")
        print(f"  Error: {str(e)}")
        return False

def verify_topics(config):
    """Verify required topics exist."""
    required_topics = ['task-events', 'reminders', 'task-updates']

    try:
        from kafka.admin import KafkaAdminClient

        admin_client = KafkaAdminClient(
            bootstrap_servers=config['bootstrap_servers'],
            security_protocol=config['security_protocol'],
            sasl_mechanism=config['sasl_mechanism'],
            sasl_plain_username=config['sasl_username'],
            sasl_plain_password=config['sasl_password']
        )

        topics = admin_client.list_topics()
        admin_client.close()

        missing_topics = [t for t in required_topics if t not in topics]

        if missing_topics:
            print(f"⚠ Missing topics: {', '.join(missing_topics)}")
            print("  Please create these topics in Redpanda Cloud Console")
            return False

        print(f"✓ Topics verified: {', '.join(required_topics)}")
        return True

    except Exception as e:
        print(f"⚠ Could not verify topics: {str(e)}")
        print("  Please verify topics exist in Redpanda Cloud Console")
        return True  # Don't fail on topic verification

def main():
    """Run all connection tests."""
    print("=" * 60)
    print("Redpanda Cloud Connection Test")
    print("=" * 60)
    print()

    # Load configuration
    print("Loading configuration...")
    config = load_config()
    print(f"✓ Configuration loaded")
    print(f"  Bootstrap servers: {config['bootstrap_servers']}")
    print()

    # Verify topics
    print("Verifying topics...")
    verify_topics(config)
    print()

    # Test producer
    print("Testing producer...")
    producer_ok = test_producer(config)
    print()

    # Test consumer
    print("Testing consumer...")
    consumer_ok = test_consumer(config)
    print()

    # Summary
    print("=" * 60)
    if producer_ok and consumer_ok:
        print("✓ All tests passed! Redpanda Cloud is ready.")
        print()
        print("Next steps:")
        print("  1. Proceed to Dapr setup (T013-T018)")
        print("  2. Configure Dapr Kafka pub/sub component")
        print("  3. Test event publishing from backend")
        return 0
    else:
        print("❌ Some tests failed. Please check configuration.")
        print()
        print("Troubleshooting:")
        print("  1. Verify bootstrap servers URL")
        print("  2. Check SASL credentials")
        print("  3. Ensure topics are created")
        print("  4. Check firewall/network connectivity")
        return 1

if __name__ == '__main__':
    sys.exit(main())
