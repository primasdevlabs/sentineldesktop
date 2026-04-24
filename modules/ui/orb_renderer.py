"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/ui/orb_renderer.py
Description: High-performance OpenGL renderer for the Sentinel 'Lock Orb'.
             Utilizes GLSL shaders to create a liquid-like, reactive AI 
             visualization that responds to voice amplitude and system state.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import sys
import math
import time
import numpy as np
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from typing import Optional, Dict

# --- GLSL Shaders ---

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
void main() { 
    // Pass coordinate data directly to fragment shader
    gl_Position = vec4(aPos, 1.0); 
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

// Uniforms provided by Python/PyQt
uniform float uTime;
uniform vec2 uResolution;
uniform float uAmplitude;
uniform int uState; // 0: Idle, 1: Listening, 2: Speaking, 3: Alert

void main() {
    // Normalize coordinates (-1.0 to 1.0) and correct aspect ratio
    vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution.xy) / min(uResolution.y, uResolution.x);
    float dist = length(uv);
    
    // Core parameters for the liquid sphere
    float baseRadius = 0.25;
    float pulse = 0.02 * sin(uTime * 2.0);
    
    // Adjust pulse dynamics based on system state
    if (uState == 1) {
        pulse = 0.05 * sin(uTime * 8.0); // Rapid listening pulse
    } else if (uState == 2) {
        pulse = uAmplitude * 0.1;       // Reactive voice pulse
    } else if (uState == 3) {
        pulse = 0.08 * sin(uTime * 15.0); // Urgent alert pulse
    }

    // Dynamic deformation logic (The "Liquid" effect)
    float angle = atan(uv.y, uv.x);
    float deformation = (uState == 2) 
        ? (0.05 * sin(angle * 5.0 + uTime * 10.0) * uAmplitude) 
        : (0.01 * sin(angle * 3.0 + uTime * 2.0));
    
    // Shape generation using smoothstep for anti-aliasing
    float orb = smoothstep(
        baseRadius + pulse + deformation, 
        (baseRadius + pulse + deformation) - 0.01, 
        dist
    );
    
    // Color Palette Selection
    vec3 color = vec3(0.0, 0.5, 1.0); // Sentinel Blue
    if (uState == 1) color = vec3(0.0, 1.0, 1.0); // Listening Cyan
    if (uState == 2) color = vec3(0.4, 0.7, 1.0) + (uAmplitude * 0.5); // Speaking Glow
    if (uState == 3) color = vec3(1.0, 0.2, 0.0); // Alert Red/Orange

    // Procedural outer glow
    float glow = 0.05 / (dist - baseRadius + 0.05);
    vec3 finalColor = color * orb + color * clamp(glow, 0.0, 1.0) * 0.5;
    
    // Set final output with alpha transparency
    FragColor = vec4(finalColor, orb + glow * 0.3);
}
"""

class OrbRenderer(QOpenGLWidget):
    """
    PyQt6 OpenGL Widget that renders the animated Sentinel Orb.
    
    This class manages the lifecycle of the OpenGL context, shader compilation,
    and the frame-by-frame updates of uniform variables.
    """
    
    def __init__(self, parent=None) -> None:
        """Initializes the renderer with animation timers and default state."""
        super().__init__(parent)
        self.uTime: float = 0.0
        self.uAmplitude: float = 0.0
        self.uState: int = 0
        
        # Core animation loop (target: 60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # ~62.5 FPS
        self.start_time: float = time.time()

    def update_animation(self) -> None:
        """Calculates elapsed time and triggers a widget repaint."""
        self.uTime = time.time() - self.start_time
        self.update()

    def set_state(self, status: Optional[str] = None) -> None:
        """
        Maps high-level system states to GLSL integer flags.
        
        Args:
            status: The state string (e.g., 'idle', 'listening', 'speaking').
        """
        mapping: Dict[str, int] = {
            "idle": 0, 
            "listening": 1, 
            "speaking": 2, 
            "alert": 3, 
            "thinking": 0, 
            "executing": 0
        }
        self.uState = mapping.get(status, 0)

    def set_amplitude(self, amp: float) -> None: 
        """
        Updates the reactive amplitude with basic EMA (Exponential Moving Average) 
        smoothing to prevent visual jitter.
        
        Args:
            amp: The current audio amplitude (0.0 to 1.0).
        """
        self.uAmplitude = (self.uAmplitude * 0.7) + (amp * 0.3)

    def initializeGL(self) -> None:
        """Sets up OpenGL environment and compiles shaders on GPU."""
        # Enable Alpha Blending for transparent UI elements
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Compile and link the GLSL shader program
        self.shader = compileProgram(
            compileShader(VERTEX_SHADER, GL_VERTEX_SHADER), 
            compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )

    def paintGL(self) -> None:
        """Primary render loop called by PyQt."""
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader)
        
        # Upload uniform data to the GPU
        glUniform1f(glGetUniformLocation(self.shader, "uTime"), self.uTime)
        glUniform2f(glGetUniformLocation(self.shader, "uResolution"), float(self.width()), float(self.height()))
        glUniform1f(glGetUniformLocation(self.shader, "uAmplitude"), self.uAmplitude)
        glUniform1i(glGetUniformLocation(self.shader, "uState"), self.uState)
        
        # Render a full-screen quad to draw the procedural fragment shader
        glBegin(GL_QUADS)
        glVertex3f(-1, -1, 0)
        glVertex3f(1, -1, 0)
        glVertex3f(1, 1, 0)
        glVertex3f(-1, 1, 0)
        glEnd()
