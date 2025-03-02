import threading
import time
import numpy as np
from flask import Flask, render_template, request, jsonify
from collections import deque
from datetime import datetime

# Configuration defaults remain unchanged.
CONFIG = {
    "cloud_providers": ["aws", "azure", "gcp"],
    "cost_rates": {
        "aws": 0.0000004,  # $0.40 per million requests
        "azure": 0.0000005,
        "gcp": 0.00000035
    },
    "auto_scale_thresholds": {
        "scale_up": 0.8,
        "scale_down": 0.3
    },
    "security": {
        "encryption": True,
        "compliance": "GDPR"
    }
}

# -------------------- Logging --------------------
class QuantumLogger:
    def __init__(self):
        self.log = deque(maxlen=1000)
        self.metrics = {
            "messages_processed": 0,
            "cloud_cost": 0.0,
            "prediction_accuracy": [],
            "current_scale": 1.0,
            "latency_p99": 0.0,
            "error_rate": 0.0,
            "ai_learning_rate": 0.1,      # Dummy parameter for learning improvements
            "ai_accuracy_history": []     # Historical accuracy values
        }
        # History for potential future use (e.g., graphing) is maintained.
        self.history = []

    def log_event(self, event, metadata=None):
        timestamp = datetime.now().isoformat()
        entry = {"timestamp": timestamp, "event": event, "metadata": metadata or {}}
        self.log.append(entry)
        print(f"[{timestamp}] {event} {metadata if metadata else ''}")

# -------------------- Cloud Connectors --------------------
class CloudGateway:
    def __init__(self, logger: QuantumLogger):
        self.logger = logger
        self.active_providers = CONFIG["cloud_providers"]
        self.connections = self._initialize_connections()
    
    def _initialize_connections(self):
        connections = {}
        for provider in self.active_providers:
            # Simulated connection strings for demonstration.
            connections[provider] = f"Simulated connection for {provider}"
        return connections
    
    def send_to_cloud(self, provider: str, messages):
        """
        Simulate sending messages to a cloud provider and update cost.
        """
        cost = len(messages) * CONFIG["cost_rates"][provider]
        # The cloud cost is updated in a thread-safe way.
        with hqs.lock:
            self.logger.metrics["cloud_cost"] += cost
        time.sleep(0.1)  # Simulated network/API call delay.
        self.logger.log_event("SENT_TO_CLOUD", {"provider": provider, "messages": len(messages), "cost": cost})
        return True

# -------------------- AI Components --------------------
class AIScaler:
    def __init__(self):
        self.current_scale = 1.0
        self.scaling_history = []
    
    def analyze_workload(self, traffic_data):
        """
        Simple auto-scaling logic based on the average of the recent load.
        """
        if len(traffic_data) < 10:
            return self.current_scale
        recent_load = np.mean(traffic_data[-10:])
        if recent_load > CONFIG["auto_scale_thresholds"]["scale_up"]:
            new_scale = min(2.0, self.current_scale * 1.25)
        elif recent_load < CONFIG["auto_scale_thresholds"]["scale_down"]:
            new_scale = max(0.5, self.current_scale * 0.8)
        else:
            new_scale = self.current_scale
        self.scaling_history.append(new_scale)
        self.current_scale = new_scale
        return new_scale

class AITrainer:
    def __init__(self, logger: QuantumLogger):
        self.logger = logger

    def train_model(self, training_data, labels):
        """
        Simulate AI training. The more messages processed, the higher the accuracy.
        The learning rate decays slightly after each training session.
        """
        self.logger.log_event("AI_TRAINING_STARTED")
        with hqs.lock:
            messages = self.logger.metrics["messages_processed"]
            current_lr = self.logger.metrics["ai_learning_rate"]
        new_accuracy = min(0.99, 0.8 + (messages / 10000) * current_lr)
        with hqs.lock:
            self.logger.metrics["ai_learning_rate"] *= 0.99
            self.logger.metrics["ai_accuracy_history"].append(new_accuracy)
        time.sleep(2)  # Simulated training duration.
        self.logger.log_event("AI_TRAINING_COMPLETED", {"accuracy": new_accuracy})
        return {"accuracy": new_accuracy, "learning_rate": self.logger.metrics["ai_learning_rate"]}

# -------------------- Security --------------------
class SecurityOrchestrator:
    def __init__(self):
        self.encryption_enabled = CONFIG["security"]["encryption"]
        self.compliance_mode = CONFIG["security"]["compliance"]
    
    def audit_message(self, message):
        """
        Check if the message passes security/compliance rules.
        Under GDPR, messages containing 'PII' are blocked.
        """
        if self.compliance_mode == "GDPR":
            return "PII" not in message
        return True

# -------------------- Core Hybrid Queue System --------------------
class HybridQueueSystem:
    def __init__(self):
        self.logger = QuantumLogger()
        self.cloud = CloudGateway(self.logger)
        self.scaler = AIScaler()
        self.security = SecurityOrchestrator()
        self.ai_trainer = AITrainer(self.logger)
        self.local_queue = deque()
        self.traffic_data = deque(maxlen=100)
        self.simulation_running = False
        self.simulation_thread = None
        self.total_messages = 500000
        self.messages_ingested = 0
        self.cloud_routing_probability = 0.5
        # Lock for thread safety.
        self.lock = threading.Lock()
        
        # Start background threads.
        threading.Thread(target=self._monitor_system, daemon=True).start()
        threading.Thread(target=self._process_messages, daemon=True).start()
    
    def _monitor_system(self):
        """
        Monitor system metrics and update them every second.
        """
        while True:
            with self.lock:
                self.logger.metrics["current_scale"] = self.scaler.current_scale
                # Simulate more variation for latency and error rate.
                self.logger.metrics["latency_p99"] = np.random.uniform(5, 25)
                self.logger.metrics["error_rate"] = np.random.uniform(0, 5)
                # Compute simulated load as the ratio of messages_ingested to total_messages.
                simulated_load = self.messages_ingested / self.total_messages if self.total_messages > 0 else 0
            self.traffic_data.append(simulated_load)
            new_scale = self.scaler.analyze_workload(list(self.traffic_data))
            with self.lock:
                self.logger.metrics["current_scale"] = new_scale

                snapshot = {
                    "timestamp": datetime.now().isoformat(),
                    "messages_processed": self.logger.metrics["messages_processed"],
                    "cloud_cost": round(self.logger.metrics["cloud_cost"], 6),
                    "current_scale": self.logger.metrics["current_scale"],
                    "latency_p99": round(self.logger.metrics["latency_p99"], 2),
                    "error_rate": round(self.logger.metrics["error_rate"], 2)
                }
                self.logger.history.append(snapshot)
                if len(self.logger.history) > 60:
                    self.logger.history.pop(0)
            time.sleep(1)
    
    def _process_messages(self):
        """
        Process messages from the local queue.
        Messages that pass security are either sent to the cloud or processed locally.
        """
        while True:
            if self.local_queue:
                msg = self.local_queue.popleft()
                if self.security.audit_message(msg):
                    if np.random.random() < self.cloud_routing_probability:
                        self.cloud.send_to_cloud("aws", [msg])
                    else:
                        time.sleep(0.01 * self.scaler.current_scale)
                    with self.lock:
                        self.logger.metrics["messages_processed"] += 1
                        self.logger.metrics["prediction_accuracy"].append(np.random.uniform(0.8, 1.0))
                else:
                    self.logger.log_event("SECURITY_BLOCK", {"message": msg[:50] + "..."})
            time.sleep(0.1)
    
    def ingest_message(self, message):
        """
        Ingest a new message into the local queue.
        """
        if self.security.audit_message(message):
            self.local_queue.append(message)
            self.logger.log_event("MESSAGE_INGESTED", {"message": message[:50] + "..."})
            with self.lock:
                self.messages_ingested += 1
        else:
            self.logger.log_event("SECURITY_BLOCK", {"message": message[:50] + "..."})
    
    def start_simulation(self, total_messages, message_delay, routing_probability):
        """
        Start the message ingestion simulation.
        """
        with self.lock:
            if self.simulation_running:
                return False
            self.simulation_running = True
            self.total_messages = total_messages
            self.messages_ingested = 0
            self.cloud_routing_probability = routing_probability
        self.simulation_thread = threading.Thread(
            target=self._simulate_message_ingestion, 
            args=(total_messages, message_delay), 
            daemon=True
        )
        self.simulation_thread.start()
        return True
    
    def _simulate_message_ingestion(self, total_messages, message_delay):
        for i in range(total_messages):
            with self.lock:
                if not self.simulation_running:
                    break
            msg = f"MSG_{i}_SAMPLE_DATA_{'X'*256}"
            self.ingest_message(msg)
            time.sleep(message_delay)
        with self.lock:
            self.simulation_running = False
    
    def stop_simulation(self):
        with self.lock:
            self.simulation_running = False

    def get_simulation_status(self):
        with self.lock:
            return {
                "simulation_running": self.simulation_running,
                "total_messages": self.total_messages,
                "messages_ingested": self.messages_ingested,
                "cloud_routing_probability": self.cloud_routing_probability
            }

# -------------------- Enterprise Extensions --------------------
class HQSExtensions:
    @staticmethod
    def cost_forecast(simulated_traffic):
        rates = CONFIG["cost_rates"]
        # Cost forecast based on total messages processed.
        return {provider: round(rate * simulated_traffic, 6) for provider, rate in rates.items()}
    
    @staticmethod
    def generate_compliance_report():
        return {
            "GDPR_checks": int(np.random.randint(95, 100)),
            "HIPAA_compliant": False,
            "last_audit": datetime.now().isoformat()
        }

# Create a global instance of the HybridQueueSystem.
hqs = HybridQueueSystem()

# -------------------- Flask App and Endpoints --------------------
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/metrics', methods=["GET"])
def metrics():
    status = hqs.get_simulation_status()
    data = {
        "metrics": hqs.logger.metrics,
        "simulation": status,
        "scaling_history": hqs.scaler.scaling_history,
        "ai_accuracy_history": hqs.logger.metrics["ai_accuracy_history"],
        "history": hqs.logger.history
    }
    return jsonify(data)

@app.route('/start-simulation', methods=["POST"])
def start_simulation():
    req_data = request.get_json()
    total_messages = int(req_data.get("total_messages", 100))
    message_delay = float(req_data.get("message_delay", 0.1))
    routing_probability = float(req_data.get("routing_probability", 0.5))
    success = hqs.start_simulation(total_messages, message_delay, routing_probability)
    return jsonify({
        "started": success, 
        "total_messages": total_messages, 
        "message_delay": message_delay,
        "routing_probability": routing_probability
    })

@app.route('/stop-simulation', methods=["POST"])
def stop_simulation():
    hqs.stop_simulation()
    return jsonify({"stopped": True})

@app.route('/train', methods=["POST"])
def train():
    result = hqs.ai_trainer.train_model(None, None)
    return jsonify(result)

@app.route('/extensions', methods=["GET"])
def extensions():
    forecast = HQSExtensions.cost_forecast(1_000_000)
    compliance = HQSExtensions.generate_compliance_report()
    return jsonify({"cost_forecast": forecast, "compliance_report": compliance})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
