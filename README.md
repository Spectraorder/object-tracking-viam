# **Object Tracking with Raspberry Pi-Controlled Viam Rover**

This project utilizes Viam's APIs to control a robot's movement based on object detection through a vision service. The robot can identify an object, spin to find it, and then move toward it based on its position within the camera's field of view. The behavior is controlled asynchronously using Python's `asyncio` module, providing a smooth and responsive interaction with the environment.

### Main Features

- Object detection and tracking using Viam's vision services.
- Automated robot control based on the detected object's position relative to the camera.
- Continuous asynchronous operation for real-time responsiveness.

### Code Highlights

The code is built around three core functions:

1. **connect()**: Establishes connection to the robot using credentials.
2. **leftOrRight()**: Determines the position of the detected object (left, right, or center) and directs the robot accordingly.
3. **main()**: Main control loop for object detection and robot movement.

### Customization

Key parameters such as motor speed (`vel`), spin angle (`spinNum`), and forward movement (`straightNum`) can be adjusted to customize the robot's behavior to better suit various applications.