import os

class GenieXExplainer:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self.llm = None
        # Explanation cache: {(prev_state, current_state, rain, health): explanation_text}
        self.cache = {}
        
        # Try to load llama-cpp-python if model path is set
        if self.model_path and os.path.exists(self.model_path):
            try:
                from llama_cpp import Llama  # type: ignore
                print(f"[GenieX] Loading GGUF model from {self.model_path}...")
                self.llm = Llama(model_path=self.model_path, n_ctx=512, verbose=False)
                print("[GenieX] GGUF Model loaded successfully.")
            except Exception as e:
                print(f"[GenieX] Failed to load GGUF model: {e}. Falling back to rule-based explainer.")
        else:
            if self.model_path:
                print(f"[GenieX] GGUF model path not found at '{self.model_path}'. Using rule-based explainer.")
            else:
                print("[GenieX] No GGUF model path provided. Using rule-based explainer.")

    def _generate_rule_explanation(self, prev_state: str, current_state: str, telemetry: dict, trust_score: float) -> str:
        """Rule-based backup explanation generator."""
        pose = telemetry.get("pose", "unknown")
        confidence = telemetry.get("confidence", 0.0)
        movement = telemetry.get("movement", 0.0)
        rain = telemetry.get("rain", False)
        health = telemetry.get("health", "healthy")
        
        factors = []
        if rain:
            factors.append("rain was detected by Arduino")
        if pose == "horizontal":
            factors.append("phone is positioned horizontally")
        elif pose == "vertical":
            factors.append("phone is vertical")
        if movement > 0.7:
            factors.append("high acceleration movement registered")
        if health in ["critical", "warning"]:
            factors.append(f"device health is {health}")
            
        if not factors:
            factors.append("sensor metrics are stable")
            
        factors_str = " and ".join(factors)
        
        if current_state == "EMERGENCY":
            return f"Phone and Arduino agree. {factors_str.capitalize()}. Emergency state issued."
        elif current_state == "DISTRESS":
            return f"Distress detected. {factors_str.capitalize()}. Trust score increased to {trust_score:.2f}."
        elif current_state == "SUSPICIOUS":
            return f"Suspicious activity. {factors_str.capitalize()} indicates potential incident."
        elif current_state == "OBSERVE":
            return f"Observe state active. {factors_str.capitalize()} requires closer monitoring."
        else:
            return f"System returned to NORMAL. {factors_str.capitalize()} and conditions are stable."

    def explain(self, prev_state: str, current_state: str, telemetry: dict, trust_score: float) -> str:
        """
        Generates a plain-English explanation for a mission state transition.
        Caches explanations to prevent redundant work.
        """
        rain = bool(telemetry.get("rain", False))
        health = str(telemetry.get("health", "healthy")).lower()
        
        # Check cache
        cache_key = (prev_state, current_state, rain, health)
        if cache_key in self.cache:
            print(f"[GenieX] Cache Hit! Reusing explanation for {cache_key}")
            return self.cache[cache_key]
            
        pose = telemetry.get("pose", "unknown")
        confidence = telemetry.get("confidence", 0.0)
        movement = telemetry.get("movement", 0.0)
        
        explanation = None
        
        if self.llm:
            prompt = (
                f"Explain why the system state changed from {prev_state} to {current_state} based on: "
                f"Pose: {pose}, Confidence: {confidence:.2f}, Movement: {movement:.2f}, Rain: {'detected' if rain else 'none'}, "
                f"Health: {health}. Trust: {trust_score:.2f}. "
                "Write exactly one simple, concise sentence."
            )
            try:
                response = self.llm(
                    f"System: You are GenieX, a system state explainability assistant. Write exactly one sentence explaining the change.\n\nQ: {prompt}\nA:",
                    max_tokens=60,
                    stop=["\n", "Q:"],
                    temperature=0.2
                )
                txt = response["choices"][0]["text"].strip()
                txt = txt.replace('GenieX:', '').replace('A:', '').strip()
                if txt:
                    explanation = txt
            except Exception as e:
                print(f"[GenieX] LLM inference failed: {e}. Using rules.")

        if not explanation:
            explanation = self._generate_rule_explanation(prev_state, current_state, telemetry, trust_score)
            
        # Store in cache
        self.cache[cache_key] = explanation
        return explanation

    def _map_event_type(self, current_state: str, telemetry: dict) -> str:
        """Map state + telemetry to a high-level event_type for downstream systems."""
        water = telemetry.get("water", 0.0)
        movement = telemetry.get("movement", 0.0)
        health = telemetry.get("health", "healthy")

        if current_state == "EMERGENCY":
            # Emergency with high water -> drowning-like event
            if water >= 0.8:
                return "drowning"
            # Emergency with critical device/health -> hazard
            if health in ["critical"]:
                return "hazard"
            return "anomaly"

        if current_state in ["DISTRESS", "SUSPICIOUS"]:
            if water >= 0.6:
                return "hazard"
            return "anomaly"

        return "normal"

    def explain_structured(self, prev_state: str, current_state: str, telemetry: dict, trust_score: float) -> dict:
        """Returns a structured explanation dict suitable for the dashboard and TTS payloads.

        Output schema:
        {
            'event_type': 'drowning' | 'hazard' | 'anomaly' | 'normal',
            'confidence': float,  # trust score 0..1
            'reason': str,        # human-readable explanation
            'details': { ... }    # telemetry and intermediate signals
        }
        """
        # Reuse plain text explanation as the human-readable reason
        reason_text = self.explain(prev_state, current_state, telemetry, trust_score)

        event_type = self._map_event_type(current_state, telemetry)

        details = {
            "pose": telemetry.get("pose"),
            "pose_confidence": telemetry.get("confidence"),
            "water": telemetry.get("water"),
            "movement": telemetry.get("movement"),
            "rain": telemetry.get("rain"),
            "health": telemetry.get("health"),
        }

        structured = {
            "event_type": event_type,
            "confidence": float(trust_score),
            "reason": reason_text,
            "details": details,
        }

        return structured
