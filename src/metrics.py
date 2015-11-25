import matplotlib.pyplot as plt
import numpy as np

class Metrics:
    def linkRate(self, fig):
        time, linkRate = np.loadtxt('linkRateLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)


        ax1 = fig.add_subplot(611)

        ax1.set_xlabel('Time (sec)')
        ax1.set_ylabel('Link rate (Mbps)')

        ax1.plot(time, linkRate, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        leg = ax1.legend()

    def bufferOccupancy(self, fig):
        time, buffer = np.loadtxt('bufferLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax2 = fig.add_subplot(612)

        ax2.set_xlabel('Time (sec)')
        ax2.set_ylabel('Buffer Occupancy (pkts)')

        ax2.plot(time, buffer, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        leg = ax2.legend()

    def packetLoss(self, fig):
        time, packetLoss = np.loadtxt('packetLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax3 = fig.add_subplot(613)

        ax3.set_xlabel('Time (sec)')
        ax3.set_ylabel('Packet loss (pkts)')

        ax3.plot(time, packetLoss, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax3.get_position()
        ax3.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        leg = ax3.legend()

    def flowRate(self, fig):
        time, flowRate = np.loadtxt('flowRateLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax4 = fig.add_subplot(614)

        ax4.set_xlabel('Time (sec)')
        ax4.set_ylabel('Flow rate (Mbps)')

        ax4.plot(time, flowRate, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax4.get_position()
        ax4.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax4.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        leg = ax4.legend()

    def windowSize(self, fig):
        time, windowSize = np.loadtxt('windowLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax5 = fig.add_subplot(615)

        ax5.set_xlabel('Time (sec)')
        ax5.set_ylabel('Window size (pkts)')

        ax5.plot(time, windowSize, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax5.get_position()
        ax5.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax5.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        leg = ax5.legend()

    def packetDelay(self, fig):
        time, packetDelay = np.loadtxt('packetLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax6 = fig.add_subplot(616)

        ax6.set_xlabel('Time (sec)')
        ax6.set_ylabel('Packet delay (ms)')

        ax6.plot(time, packetDelay, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax6.get_position()
        ax6.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax6.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        leg = ax6.legend()

    def run(self):
        # Starting the metric logging.
        fig = plt.figure(figsize=(10, 10))
        self.linkRate(fig)
        # self.bufferOccupancy(fig)
        # self.packetLoss(fig)
        # self.flowRate(fig)
        # self.windowSize(fig)
        # self.packetDelay(fig)

        plt.show()

if __name__ == '__main__':
    metric = Metrics()
    metric.run()
