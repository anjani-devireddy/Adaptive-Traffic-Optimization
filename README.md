# 🚦 Adaptive Traffic Optimization System

An AI-powered adaptive traffic management system that analyzes traffic from multiple camera/video feeds, detects vehicles using **YOLO11n**, calculates traffic demand, and dynamically adjusts traffic signal timings.

The system is designed as a prototype for intelligent intersection management, using real-time computer vision to allocate more green-light time to approaches experiencing higher traffic demand.

---

## 📌 Project Overview

Traditional traffic signals commonly operate using fixed timing schedules. This can result in inefficient traffic flow when one direction has significantly more traffic than another.

This project addresses that problem by combining:

- Computer vision
- YOLO11n object detection
- Traffic-density analysis
- Vehicle-weighted traffic scoring
- Adaptive signal timing
- Multi-camera monitoring
- Flask web dashboard
- SQLite data logging

The system continuously analyzes four traffic video sources representing:

| Camera | Direction | Signal Phase |
|---|---|---|
| Camera 0 | North | North/South |
| Camera 1 | East | East/West |
| Camera 2 | South | North/South |
| Camera 3 | West | East/West |

The traffic demand from the four cameras is combined into two signal phases:

```text
North + South  → Phase 0
East + West    → Phase 1
