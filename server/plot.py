import matplotlib.pyplot as plt
import numpy as np

def setup_plot():
    map = plt.figure()
    ax_map = map.add_subplot(221, projection='3d')
    ax_map.set_xlabel("X axis")
    ax_map.set_ylabel("Y axis")
    ax_map.set_zlabel("Z axis")
    ax_map.set_xlim3d([-2.0, 2.0])
    ax_map.set_ylim3d([-2.0, 2.0])
    ax_map.set_zlim3d([-2.0, 2.0])
    ax_map.grid(False)
    ax_map.set_title("Accelerometer measurement")
    axa, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    ax_map = map.add_subplot(222, projection='3d')
    ax_map.set_xlabel("X axis")
    ax_map.set_ylabel("Y axis")
    ax_map.set_zlabel("Z axis")
    ax_map.set_xlim3d([-5.0, 5.0])
    ax_map.set_ylim3d([-5.0, 5.0])
    ax_map.set_zlim3d([-5.0, 5.0])
    ax_map.grid(False)
    ax_map.set_title("Gyroscope measurement")
    axg, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    ax_map = map.add_subplot(223, projection='3d')
    ax_map.set_xlabel("Alpha")
    ax_map.set_ylabel("Beta")
    ax_map.set_zlabel("Gamma")
    ax_map.set_xlim3d([-180, 180])
    ax_map.set_ylim3d([-180, 180])
    ax_map.set_zlim3d([-180, 180])
    ax_map.grid(True)
    ax_map.set_title("Magnetometer measurement")
    axm, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    ax_map = map.add_subplot(224, projection='3d')
    ax_map.set_xlabel("Alpha")
    ax_map.set_ylabel("Beta")
    ax_map.set_zlabel("Gamma")
    ax_map.set_xlim3d([-180, 180])
    ax_map.set_ylim3d([-180, 180])
    ax_map.set_zlim3d([-180, 180])
    ax_map.grid(True)
    ax_map.set_title("Kalman rotation")
    axr, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    print("Plot was initialized")

    return map, axa, axg, axm, axr


def update_line(hl, new_data):
    hist_points = 5
    xdata, ydata, zdata = hl._verts3d
    hl.set_xdata(np.array(np.append(xdata[-hist_points:], new_data[0])))
    hl.set_ydata(np.array(np.append(ydata[-hist_points:], new_data[1])))
    hl.set_3d_properties(np.array(np.append(zdata[-hist_points:], new_data[2])))
