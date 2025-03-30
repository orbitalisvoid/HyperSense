# Feature Management Plugin System

## Overview

This project demonstrates an advanced plugin-based architecture for processing real-time video frames using OpenCV. The system allows for dynamically enabling or disabling features such as **Kalman Filter**, **Optical Flow**, and **Face Detection**. The features are implemented as shared libraries (DLL, SO, or DYLIB files) and are dynamically loaded by the main program at runtime. The configuration for enabling/disabling features is managed by a server and periodically fetched by the client application.

The system integrates computer vision with a **plugin management system**, allowing real-time frame processing and feature toggling without restarting the application.

## Features

- **Dynamic Plugin Loading**: Load and execute features like Kalman Filter, Optical Flow, and Face Detection as shared libraries.
- **Real-time Video Processing**: Process frames captured from a webcam in real time using OpenCV.
- **Feature Management**: Toggle features on/off via a REST API, enabling or disabling feature processing without application restart.
- **Modular and Scalable**: Easily add more features by creating additional shared libraries.

## System Architecture

1. **Client Application (C++)**: 
    - Captures video from the webcam.
    - Dynamically loads and processes frames using features implemented in shared libraries.
    - Displays processed frames in separate windows for each active feature.

2. **Server (Node.js + Express)**:
    - Manages feature configurations (enabled/disabled).
    - Provides an API endpoint to retrieve the current feature configuration.
    - The client periodically fetches the configuration from the server to update active features.

3. **Plugin System**: 
    - Plugins are shared libraries (DLL/SO/DYLIB files) with a standardized interface.
    - Plugins process frames using a `processFrame` function exposed in each library.

## Components

### 1. Client Application

- **Main Functionality**: 
    - Captures video frames from the webcam using OpenCV (`cv::VideoCapture`).
    - Fetches the current configuration from the server (`/api/get_subscription`).
    - Loads and processes frames using enabled features.
    - Displays the processed frames in separate windows.

- **Dependencies**:
    - OpenCV
    - PluginLoader (Custom Class)
    - cpr (for HTTP requests)

### 2. Server (Node.js)

- **Main Functionality**: 
    - Serves the `/api/get_subscription` endpoint.
    - Allows the client to fetch the configuration for which features should be enabled/disabled.

- **Dependencies**:
    - Express.js
    - JSON for feature configuration

### 3. Feature Plugins

- Each feature (Kalman Filter, Optical Flow, Face Detection) is implemented in a shared library.
- **Common Interface**: Each plugin must define the following C-compatible interface for the `processFrame` function:

    ```cpp
    struct CPluginResult
    {
        unsigned char *data;
        int width;
        int height;
        int channels;
        int hasData;
    };
    ```

- **Face Detection Plugin**: Uses OpenCV’s Haar Cascade Classifier to detect faces and display them in the processed frame.
- **Kalman Filter Plugin**: Displays the Kalman filter label in the processed frame.
- **Optical Flow Plugin**: Converts the frame to grayscale and displays the optical flow label.

## Getting Started

### Prerequisites

Before running the system, ensure that the following dependencies are installed:

1. **OpenCV**: Required for video capture and processing.
2. **Node.js**: For running the server-side API.
3. **cpr**: C++ HTTP client library used for making requests to the server.

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/orbitalisvoid/HyperSight.git
    cd feature-management-plugin
    ```

2. **Install Server Dependencies**:
    Navigate to the server directory and install the required Node.js packages:
    ```bash
    cd server
    npm install
    ```

3. **Build the Client Application**:
    - If you’re using CMake, navigate to the client directory and run:
    ```bash
    mkdir build
    cd build
    cmake ..
    make
    ```

4. **Build Feature Plugins**:
    - The feature plugins need to be compiled as shared libraries (DLL/SO/DYLIB) based on your operating system.
    - Make sure OpenCV is linked correctly during the build process.

### Running the Application

1. **Start the Server**:
    - Run the Node.js server to start serving the feature configuration:
    ```bash
    cd server
    node server.js
    ```

2. **Run the Client**:
    - After building the client application, run it to start processing the webcam feed:
    ```bash
    ./client_application
    ```

3. **Toggle Features**:
    - Use the server's `/api/get_subscription` endpoint to update the feature configuration.
    - The client will periodically fetch this configuration and enable/disable features accordingly.

## Configuration

The server's feature configuration is a simple JSON object:

```json
{
  "kalman_filter": false,
  "optical_flow": true,
  "face_detection": true
}
```

To update the configuration, modify the `subscriptionData` object in the server code and restart the server.

## Customizing Plugins

To add new features:

1. Create a new plugin following the same structure as the existing features (e.g., **Face Detection**, **Kalman Filter**).
2. Implement the `processFrame` function in the plugin.
3. Build the plugin as a shared library.
4. Add the feature to the client-side configuration (e.g., `features` map).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV for powerful computer vision capabilities.
- Node.js and Express for easy server-side API management.
- cpr for simplified HTTP requests in C++.