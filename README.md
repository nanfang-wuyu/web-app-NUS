# Al Control System for Fan and Air Conditioner - NUS AIoT Summer Workshop

This repository contains the source code and documentation for the **AI Control System for Fan and Air Conditioner**, a project that won the **Second Prize** at the **Artificial Intelligence of Things Summer Workshop** at the **National University of Singapore**.

## Project Overview

The AI Control System is an autonomous solution designed to optimize energy usage in public spaces by intelligently controlling air conditioners and fans. The system operates in multiple modes based on real-time environmental data such as temperature, humidity, and occupancy, aiming to minimize energy waste while maintaining comfort.

### Key Features and Technologies:
- **Multi-mode Auto-Control**: Automatically adjusts air conditioner and fan settings according to real-time inputs from temperature, humidity, and occupancy sensors.
- **Energy Efficiency**: Helps reduce energy consumption in public spaces by switching between operating modes based on environmental data.
- **Raspberry Pi**: Acts as the core controller, managing sensors, actuators, and real-time data collection.
- **Decision Tree Algorithm**: Machine learning-based decision-making process for predicting the best settings for air conditioners and fans based on sensor data.
- **SQLite and Flask**: Backend technologies used for data storage and server-side logic.
- **Web-Based Data Visualization**: A web application built with JavaScript allows users to monitor real-time environmental data and system performance. Both global and local services are supported.

## Project Structure

- `/Data Collection and Train/` - Scripts and data for collecting environmental information and training the decision tree model.
- `/Real-Time Prediction/` - Contains the logic for real-time prediction and control based on live sensor data.
