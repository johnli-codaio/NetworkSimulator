import matplotlib.pyplot as plt
import numpy as np

class Metrics:
    def run(self):
        # Starting the metric logging.
        time, linkRate = np.loadtxt('linkRateLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        fig = plt.figure()

        ax1 = fig.add_subplot(111)

        ax1.set_xlabel('Time (sec)')
        ax1.set_ylabel('Link rate (Mbps)')

        ax1.plot(time, linkRate, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        leg = ax1.legend()

        plt.show()

