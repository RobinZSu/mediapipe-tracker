import math

# Simple EMA Filter
class EMAFilter:
    def __init__(self, alpha=0.1):
        """
        Initializes the rotation filter with a smoothing factor.
        
        Args:
            alpha (float): Smoothing factor for the EMA filter (0 < alpha ≤ 1).
        """
        self.alpha = alpha
        self.filtered_rx = None
        self.filtered_ry = None
        self.filtered_rz = None

    def filter(self, rx, ry, rz):
        """
        Filters the input rotations using an exponential moving average.
        
        Args:
            rx (float): Rotation about the X-axis (roll) in degrees.
            ry (float): Rotation about the Y-axis (pitch) in degrees.
            rz (float): Rotation about the Z-axis (yaw) in degrees.
        
        Returns:
            tuple: Filtered rotations (rx, ry, rz) in degrees.
        """
        if self.filtered_rx is None:  # Initialize with the first input
            self.filtered_rx = rx
            self.filtered_ry = ry
            self.filtered_rz = rz
        else:
            self.filtered_rx = self.alpha * rx + (1 - self.alpha) * self.filtered_rx
            self.filtered_ry = self.alpha * ry + (1 - self.alpha) * self.filtered_ry
            self.filtered_rz = self.alpha * rz + (1 - self.alpha) * self.filtered_rz

        return self.filtered_rx, self.filtered_ry, self.filtered_rz


# Python implementation of OneEuroFilter by jaantollander
# available at https://github.com/jaantollander/OneEuroFilter under MIT lisence
def smoothing_factor(t_e, cutoff):
    r = 2 * math.pi * cutoff * t_e
    return r / (r + 1)

def exponential_smoothing(a, x, x_prev):
    return a * x + (1 - a) * x_prev

class OneEuroFilter:
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=5.0, beta=0.8,
                 d_cutoff=0.1):
        """Initialize the one euro filter."""
        # The parameters.
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        # Previous values.
        self.x_prev = float(x0)
        self.dx_prev = float(dx0)
        self.t_prev = float(t0)

    def __call__(self, t, x):
        """Compute the filtered signal."""
        t_e = t - self.t_prev

        # The filtered derivative of the signal.
        a_d = smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = exponential_smoothing(a_d, dx, self.dx_prev)

        # The filtered signal.
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = smoothing_factor(t_e, cutoff)
        x_hat = exponential_smoothing(a, x, self.x_prev)

        # Memorize the previous values.
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat