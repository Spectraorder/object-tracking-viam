import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient
from viam.components.camera import Camera
from viam.components.base import Base


async def connect():
    """
    Establishes a connection to the robot using credentials and options.

    Returns:
        RobotClient: Connected robot client.
    """
    creds = Credentials(
        type = 'robot-location-secret',
        payload = 'bjlx7g4cf89qw5joko6xjp9t5u1totjiw81ndkxishqrxwxw'
    )
    opts = RobotClient.Options(
        refresh_interval = 0,
        dial_options = DialOptions(credentials = creds)
    )
    return await RobotClient.at_address('hal-main.6n3fkdbbro.viam.cloud', opts)


def leftOrRight(detections, midpoint, last_position):
    """
    Determines the position of the detected object relative to the midpoint of the frame.

    Args:
        detections (list): List of detected objects.
        midpoint (float): Horizontal midpoint of the frame.
        last_position (str): Last known position of the object ("CW", "CCW", or None).

    Returns:
        Tuple[int, str]: Tuple containing the position of the object (0 for left, 1 for center, 2 for right)
        and the spin direction ("CW", "CCW", or None if unknown).
    """
    largest_area = 0
    largest = {"x_max": 0, "x_min": 0, "y_max": 0, "y_min": 0}

    if not detections:
        # If no objects are detected
        if last_position is not None:
            # If last known position is available, continue spinning in the last known direction
            return -1, last_position
        else:
            # If last known position is not available, start spinning slowly to find the object
            return -1, None

    for d in detections:
        a = (d.x_max - d.x_min) * (d.y_max - d.y_min)
        if a > largest_area:
            largest_area = a
            largest = d

    centerX = largest.x_min + largest.x_max / 2
    if centerX < midpoint - midpoint / 6:

        return 0, "CCW"  # Object is on the left
    if centerX > midpoint + midpoint / 6:
        return 2, "CW"  # Object is on the right
    else:
        return 1, last_position  # Object is centered


async def main():
    """
    Main function to control the robot's behavior based on object detection.
    """
    last_position = None
    spinNum = 10  # When turning, spin the motor this much
    straightNum = 50  # When going straight, spin motor this much
    numCycles = 400  # Run the loop X times
    vel = 250  # Motor speed when moving

    # Connect to robot client and set up components
    robot = await connect()
    base = Base.from_robot(robot, "viam_base")
    camera_name = "cam"
    camera = Camera.from_robot(robot, camera_name)
    frame = await camera.get_image(mime_type = "image/jpeg")

    # Grab the vision service for object detection
    my_detector = VisionClient.from_robot(robot, "my_color_detector")

    # Initial slow spin to find the object if not detected in the initial frame
    while last_position is None:
        print("No object detected. Start spinning slowly to find the object in a clockwise direction.")
        await base.spin(spinNum // 3, vel)  # Slow spin in a clockwise (CW) direction
        detections = await my_detector.get_detections_from_camera(camera_name)
        # Determine the object's position based on the initial spinning direction (CW)
        answer, last_position = leftOrRight(detections, frame.size[0] / 2, "CW")

    # Main loop. Detect the object, determine its position, and act accordingly.
    for i in range(numCycles):
        detections = await my_detector.get_detections_from_camera(camera_name)

        answer, last_position = leftOrRight(detections, frame.size[0] / 2, last_position)

        if answer == -1:
            # Object not detected, spin in the last known direction
            if last_position == "CCW":
                print("Last seen on the left. Spinning CCW.")
                await base.spin(spinNum // 3, vel)
            else:
                print("Last seen on the right. Spinning CW.")
                await base.spin(-spinNum // 3, vel)
        else:
            # Object detected, handle its position
            if answer == 0:
                print("Object on the left.")
                await base.spin(spinNum // 3, vel)
                await base.move_straight(straightNum, vel)
            elif answer == 1:
                print("Object centered.")
                await base.move_straight(straightNum, vel)
            elif answer == 2:
                print("Object on the right.")
                await base.spin(-spinNum // 3, vel)
                await base.move_straight(straightNum, vel)

    await robot.close()


if __name__ == "__main__":
    print("Starting up... ")
    asyncio.run(main())
    print("Done.")
