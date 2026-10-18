import matplotlib.pyplot as plt


def plot_shear_force(results):
    """
    Plot the shear force diagram from beam analysis results.
    """

    x = results.x
    shear = results.shear

    plt.figure()

    plt.plot(x, shear)

    plt.axhline(0)

    plt.xlabel("Position along beam (m)")
    plt.ylabel("Shear force (N)")

    plt.title("Shear Force Diagram")

    plt.grid(True)

    plt.show()


def plot_bending_moment(results):
    """
    Plot the bending moment diagram from beam analysis results.
    """

    x = results.x
    moment = results.moment

    plt.figure()

    plt.plot(x, moment)

    plt.axhline(0)

    plt.xlabel("Position along beam (m)")
    plt.ylabel("Bending moment (Nm)")

    plt.title("Bending Moment Diagram")

    plt.grid(True)

    plt.show()


def plot_deflection(results):
    """
    Plot the deflection curve from beam analysis results.
    """

    x = results.x

    # Convert metres to millimetres for display
    deflection_mm = results.deflection * 1000

    plt.figure()

    plt.plot(x, deflection_mm)

    plt.axhline(0)

    plt.xlabel("Position along beam (m)")
    plt.ylabel("Deflection (mm)")

    plt.title("Deflection Curve")

    plt.grid(True)

    plt.show()