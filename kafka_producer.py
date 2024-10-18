from kafka import KafkaProducer
import subprocess
import time
import psutil
import requests

KAFKA_TOPIC = 'container_stats'
KAFKA_BOOTSTRAP_SERVERS = '52.194.247.253:9092'

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        public_ip = response.text
    except requests.RequestException as e:
        print(f"Error retrieving public IP: {e}")
        public_ip = "Unknown"
    return public_ip

def get_machine_stats(ip):
    cpu_usage = psutil.cpu_percent()

    memory_info = psutil.virtual_memory()
    used_memory_mib = memory_info.used / (1024 ** 2)

    machine_stats = f"{ip}: CPU {cpu_usage:.2f}%, RAM {used_memory_mib:.1f}MiB"
    return machine_stats

def send_stats_to_kafka():
    public_ip = get_public_ip()  # 獲取對外公網 IP

    while True:
        result = subprocess.run(['/home/ubuntu/get_container_cpu_ram.sh'], stdout=subprocess.PIPE)

        stats = result.stdout.decode('utf-8').strip().split("\n")

        machine_stats = get_machine_stats(public_ip)
        producer.send(KAFKA_TOPIC, machine_stats.encode('utf-8'))
        print(f"Sent to Kafka: {machine_stats}")

        for stat in stats:
            producer.send(KAFKA_TOPIC, stat.encode('utf-8'))
            print(f"Sent to Kafka: {stat}")

        time.sleep(0.3)

if __name__ == "__main__":
    send_stats_to_kafka()
