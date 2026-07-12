import time

class MissionStateMachine:
    STATES = ["NORMAL", "OBSERVE", "SUSPICIOUS", "DISTRESS", "EMERGENCY"]
    
    def __init__(self, cooldown_steps=5):
        self.current_state = "NORMAL"
        self.cooldown_steps = cooldown_steps
        
        # Track steps since last state change to enforce cooldown
        self.steps_since_change = 0
        
        # For escalation: need 2 consecutive readings suggesting a state higher than current_state
        self.escalation_candidate = None
        self.escalation_count = 0
        
        # For de-escalation: need cooldown_steps since last change, and consecutive lower readings
        self.de_escalation_count = 0

    def compute_trust_score(self, telemetry: dict) -> float:
        """
        Fuses sensory telemetry to compute a combined risk/trust score between 0.0 and 1.0.
        Formula:
        Trust = (0.5 * Phone + 0.2 * Water + 0.15 * Movement + 0.1 * Rain + 0.05 * Light) * HealthFactor
        """
        # Ingest inputs (defaulting to 0.0 if not specified)
        phone = telemetry.get("phone", 0.0)
        water = telemetry.get("water", 0.0)
        movement = telemetry.get("movement", 0.0)
        
        # Ingest rain (handles both boolean and float risk inputs)
        rain_val = telemetry.get("rain", 0.0)
        if isinstance(rain_val, bool):
            rain = 1.0 if rain_val else 0.0
        else:
            rain = float(rain_val)
            
        light = telemetry.get("light", 0.0)
        
        # Base weighted sum
        base_trust = (0.5 * phone) + (0.2 * water) + (0.15 * movement) + (0.1 * rain) + (0.05 * light)
        
        # Extract Health Factor
        health = str(telemetry.get("health", "healthy")).lower()
        if health == "critical":
            health_factor = 1.30
        elif health == "warning":
            health_factor = 1.15
        else:
            health_factor = 1.0
            
        # Final trust calculation (clamped between 0.0 and 1.0)
        trust = base_trust * health_factor
        return min(max(trust, 0.0), 1.0)

    def get_target_state(self, score: float) -> str:
        """Maps the trust score to a target state."""
        if score > 0.90:
            return "EMERGENCY"
        elif score > 0.75:
            return "DISTRESS"
        elif score > 0.60:
            return "SUSPICIOUS"
        elif score > 0.40:
            return "OBSERVE"
        else:
            return "NORMAL"

    def update(self, telemetry: dict) -> tuple[str, float, bool]:
        """
        Updates the state machine with new telemetry data.
        Returns:
            (new_state, trust_score, state_changed)
        """
        score = self.compute_trust_score(telemetry)
        target_state = self.get_target_state(score)
        
        current_idx = self.STATES.index(self.current_state)
        target_idx = self.STATES.index(target_state)
        
        state_changed = False
        self.steps_since_change += 1
        
        if target_idx > current_idx:
            # Escalation: reset de-escalation counts
            self.de_escalation_count = 0
            
            # Need 2 consecutive readings suggesting a state higher than current_state
            # (Matches target_state or higher)
            if self.escalation_candidate == target_state:
                self.escalation_count += 1
            else:
                self.escalation_candidate = target_state
                self.escalation_count = 1
                
            if self.escalation_count >= 2:
                self.current_state = target_state
                self.steps_since_change = 0
                self.escalation_candidate = None
                self.escalation_count = 0
                state_changed = True
                
        elif target_idx < current_idx:
            # De-escalation: reset escalation candidate
            self.escalation_candidate = None
            self.escalation_count = 0
            
            # Check if we have passed the cooldown steps since the last transition
            if self.steps_since_change >= self.cooldown_steps:
                self.de_escalation_count += 1
                # Require 2 consecutive lower readings to de-escalate
                if self.de_escalation_count >= 2:
                    self.current_state = target_state
                    self.steps_since_change = 0
                    self.de_escalation_count = 0
                    state_changed = True
            else:
                # Cooldown active, ignore de-escalation to prevent flickering
                pass
        else:
            # Stable state: reset candidate tracking
            self.escalation_candidate = None
            self.escalation_count = 0
            self.de_escalation_count = 0
            
        return self.current_state, score, state_changed
