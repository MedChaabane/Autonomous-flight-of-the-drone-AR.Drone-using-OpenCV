# Autonomous-flight-of-the-drone-AR.Drone-1.0


## Prerequisites

- [opencv-python](https://pypi.org/project/opencv-python/) 

- [pygame](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame) 

- [ffmpeg](https://github.com/kkroening/ffmpeg-python) 

# Description of the code:

The code allows a manual override of the Drone control at any time. Press any steering
key to switch to manual mode. In the following table, we present the different actions that
can be performed by the drone and each corresponding key.

![table](https://github.com/MohamedChaabane2/Autonomous-flight-of-the-drone-AR.Drone-1.0/blob/master/img/table.png)


After startup, you will see the front camera livestream in a window. At first, the drone
will wait for the activation of the autonomous flight mode. This mode can be triggered
before or after taking off.

![img1](https://github.com/MohamedChaabane2/Autonomous-flight-of-the-drone-AR.Drone-1.0/blob/master/img/img1.png)

By pressing ’w’, the drone will start searching the livestream for circular shapes.

![img2](https://github.com/MohamedChaabane2/Autonomous-flight-of-the-drone-AR.Drone-1.0/blob/master/img/img2.png)

After that, the program will try to detect the shape and locates its center.

![img3](https://github.com/MohamedChaabane2/Autonomous-flight-of-the-drone-AR.Drone-1.0/blob/master/img/img3.png)

By holding the trackable object into the field of view for around 5 seconds, the drone
will save the color distribution of the object. So, we have initialized the algorithm by taking
an image of the ball, converting the image to HSV color-space, and tuning thresholds
on the channels in a way that only the ball will be in the ranges (between the lower and
upper threshold of each channel), while the background will not. The CamShift algorithm
will search, in each frame, the location in which the most neighbor pixels are in those
ranges. The locations are searched based on the location of the object in the previous
frame.

![img4](https://github.com/MohamedChaabane2/Autonomous-flight-of-the-drone-AR.Drone-1.0/blob/master/img/img4.png)

Now, the drone will continuously scan the image for the object based on its color. If
the object is moved away from the horizontal center of the image, the drone will rotate left
or right to position the object in the center again. The size of the initial object bounding
box is saved by the program. If the object is coming closer to the camera, the drone will
fly backwards until the the object has the initial distance from the drone again. If the
object is moved away, the drone will fly forward until the initial distance is reached.

This approach uses two different detection stages. The Drone will first search for a circle
in its field of view, using the HoughCircle detection algorithm from OpenCV. If a circle is
found and remains roughly at the same spot for a given time, the tracking stage is initialized.
For this, we use the CamShift algorithm: A rectangular region inside the circle is
analyzed for its color or brightness distribution. From this point, the image is constantly
scanned for the current best match to that first identifying distribution. The drone will
then follow the tracking object, which could, for example, be a colored ball or a flashlight.

The autonomous flight is based on the CamShift algorithm. This algorithm converts
the image to a HSV color representation and then uses the hue values for the color-based
tracking. It should be noted that varying lighting conditions will influence the robustness
of the tracking. As an alternative approach, the brightness channel can be used instead of
the hue channel. In this case, the drone can follow a very bright object, e.g. a flashlight.
This approach is very robust in dark environments. In brighter environments, an opaque filter can be applied to the camera to increase the tracking robustness.

## [More detailed documentation of the code](https://github.com/MohamedChaabane2/Autonomous-flight-of-the-drone-AR.Drone-1.0/blob/master/Documentation.pdf)
