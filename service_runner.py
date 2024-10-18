from flask import Flask, request, jsonify
import requests
import subprocess
import os

app = Flask(__name__)

def get_used_ports():
    used_ports = set()
    try:
        result = subprocess.run(['ss','-tuln'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')

        for line in output.splitlines():
            parts = line.split()  # split by space
            if len(parts) >= 5:
                local_address = parts[4]
                if ':' in local_address:
                    ip_port = local_address.rsplit(':', 1)
                    port_part = ip_port[1].strip()
                    if port_part.isdigit():
                        used_ports.add(int(port_part))
    except Exception as e:
        print(f"Error occurred while checking used ports: {e}")
    return used_ports

def find_available_port(start_port=8081, end_port=9000):
    used_ports = get_used_ports()

    for port in range(start_port, end_port + 1):
        if port not in used_ports:
            return port

    raise Exception("No available ports found in the specified range.")


@app.route('/deploy', methods=['POST'])
def deploy():
    try:
        payload = request.json
        repo_owner = payload.get('repository_owner')
        repo_name = payload.get('repository_name')

        # get port info from MasterNode
        master_node_url = f"http://52.69.33.14:8082/info?username={repo_owner}&repoName={repo_name}"
        response = requests.get(master_node_url)

        if response.status_code == 200:
            port_data = response.json()
            available_port = port_data.get("port")
            cpu_limit = port_data.get("cpu")
            memory_limit = port_data.get("memory")

            print(f"{cpu_limit}")

            if not available_port:
                return jsonify({"error": "No available port found in the response."}), 500

            # send port to shell script
            script_path = '/home/ubuntu/deploy.sh'

            result = subprocess.run(['/bin/sh', script_path, repo_owner, repo_name, str(available_port), str(cpu_limit), str(memory_limit)],
                                capture_output=True,
                                text=True,
                                check=True)

            print(result)
            return f"Deployment script executed successfully.\nOutput: {result.stdout}", 200
        else:
            return jsonify({"error": f"Failed to fetch available port, status code: {response.status_code}"}), 500

    except subprocess.CalledProcessError as e:
        return f"Error executing deployment script: {e.stdout}\n{e.stderr}", 500
    except requests.RequestException as e:
        return jsonify({"error": f"Error connecting to info server: {str(e)}"}), 500

@app.route('/availablePort', methods=['GET'])
def available_port():
    try:
        port = find_available_port()
        return jsonify({"availablePort": port}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deleteContainer', methods=['POST'])
def delete_container():
    try:
        payload = request.json
        container_name = payload.get('container_name')

        if not container_name:
            return jsonify({"error": "Container name or ID is required"}), 400

        result = subprocess.run(['sudo','docker', 'rm', '-f', container_name],
                                capture_output=True,
                                text=True,
                                check=True)

        return jsonify({"message": f"Container {container_name} deleted successfully.\nOutput: {result.stdout}"}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error deleting container: {e.stdout}\n{e.stderr}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/restartContainer', methods=['POST'])
def restart_container():
    try:
        payload = request.json
        container_name = payload.get('container_name')

        if not container_name:
            return jsonify({"error": "Container name or ID is required"}), 400

        result = subprocess.run(['sudo','docker','restart', container_name],
                                capture_output=True,
                                text=True,
                                check=True)

        return jsonify({"message": f"Container {container_name} restart successfully.\nOutput: {result.stdout}"}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error restarting container: {e.stdout}\n{e.stderr}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
