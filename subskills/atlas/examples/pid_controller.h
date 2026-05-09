/**
 * PID Controller — minimal C++ header for semantic atlas testing.
 *
 * Implements a classic proportional-integral-derivative controller with
 * output clamping and enable/disable state management.
 */
#ifndef PID_CONTROLLER_H
#define PID_CONTROLLER_H

#include <cmath>
#include <algorithm>

class PIDController {
public:
    // Constructor — initializes gains and state.
    PIDController(float kp, float ki, float kd, float setpoint)
        : _kp(kp), _ki(ki), _kd(kd), _setpoint(setpoint),
          _integral(0.0f), _prevError(0.0f), _output(0.0f), _enabled(false) {}

    // Core computation — runs one PID iteration.
    // Returns clamped output in [0, 255].
    float compute(float currentValue, float dt) {
        if (!_enabled) {
            return 0.0f;
        }

        float error = _setpoint - currentValue;

        // Proportional term
        float pTerm = _kp * error;

        // Integral term with accumulation
        _integral += error * dt;

        // Derivative term
        float dTerm = 0.0f;
        if (dt > 0.0f) {
            dTerm = _kd * (error - _prevError) / dt;
        }

        _prevError = error;

        // Combined output
        _output = pTerm + _ki * _integral + dTerm;

        // Clamp to valid PWM range
        _output = std::clamp(_output, 0.0f, 255.0f);

        return _output;
    }

    // Enable the controller — resets internal state.
    void enable() {
        _enabled = true;
        reset();
    }

    // Disable the controller — output becomes 0.
    void disable() {
        _enabled = false;
        _output = 0.0f;
    }

    // Reset integral and previous error to zero.
    void reset() {
        _integral = 0.0f;
        _prevError = 0.0f;
        _output = 0.0f;
    }

    // Gain accessors
    float getKp() const { return _kp; }
    float getKi() const { return _ki; }
    float getKd() const { return _kd; }

    // Gain mutators
    void setGains(float kp, float ki, float kd) {
        _kp = kp;
        _ki = ki;
        _kd = kd;
    }

    // Setpoint accessors
    float getSetpoint() const { return _setpoint; }
    void setSetpoint(float sp) { _setpoint = sp; }

    // State query
    bool isEnabled() const { return _enabled; }

private:
    // PID gains
    float _kp;
    float _ki;
    float _kd;

    // Target value
    float _setpoint;

    // Internal state
    float _integral;   // Accumulated error integral
    float _prevError;  // Previous error for derivative calculation
    float _output;     // Last computed output

    // Control state
    bool _enabled;     // Enable/disable flag
};

#endif // PID_CONTROLLER_H
