import matplotlib.pyplot as plt
import constants
import numpy as np

class Metrics:
    def __init__(self, log):
        # file for logging
        # the current link rate
        self.linkRateLog = open('linkRateLog.log', 'w')

        # the current buffer occupancy
        self.bufferLog = open('bufferLog.log', 'w')

        # the current packet loss
        self.packetLog = open('packetLog.log', 'w')

        # the current flow rate
        self.flowRateLog = open('flowRateLog.log', 'w')

        # the current window size
        self.windowLog = open('windowLog.log', 'w')

        # the current packet delay
        self.delayLog = open('delayLog.log', 'w')

        self.metrics = [self.linkRateLog, self.bufferLog,
                self.packetLog, self.flowRateLog, self.windowLog,
                self.delayLog]
        self.log = log

        # for each logged metric,
        # give indices denoting the current time interval's
        # lower bound [0] and upper bound [1]
        # contains also the sum of values found so far [2],
        # as well as the number of events that occurred in this time interval [3]
        self.CURRENT_TIME_INTERVAL = [
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
                [0, constants.LOG_TIME_INTERVAL, 0, 0]
        ]
    
    def done(self):
        """ Closes the log files.
        """
        self.linkRateLog.close()
        self.bufferLog.close()
        self.packetLog.close()
        self.flowRateLog.close()
        self.windowLog.close()
        self.delayLog.close()
        self.run()

    def logMetric(self, time, value, type):
        if self.log == 'avg':
            lowerTimeInterval = self.CURRENT_TIME_INTERVAL[type][0]
            upperTimeInterval = self.CURRENT_TIME_INTERVAL[type][1]
            # if past the previous time interval,
            # aggregate the values for that interval and log it
            if time >= upperTimeInterval:
                # if there were no previous events, don't log anything
                count = self.CURRENT_TIME_INTERVAL[type][3]
                if count > 0:
                    occupancy = self.CURRENT_TIME_INTERVAL[type][2] \
                        / count
                    self.metrics[type].write(str(upperTimeInterval)
                        + " " + str(occupancy) + "\n")

                # update the upper/lower bounds
                while time > upperTimeInterval:
                    self.CURRENT_TIME_INTERVAL[type][1] += constants.LOG_TIME_INTERVAL
                    upperTimeInterval = self.CURRENT_TIME_INTERVAL[type][1]
                self.CURRENT_TIME_INTERVAL[type][0] \
                    = self.CURRENT_TIME_INTERVAL[type][1] \
                    - constants.LOG_TIME_INTERVAL
                # reset
                self.CURRENT_TIME_INTERVAL[type][2] = 0
                self.CURRENT_TIME_INTERVAL[type][3] = 0
            # update the aggregate buffer link found so far
            self.CURRENT_TIME_INTERVAL[type][2] \
                += value
            self.CURRENT_TIME_INTERVAL[type][3] \
                += 1
        elif self.log == 'less':
            lowerTimeInterval = self.CURRENT_TIME_INTERVAL[type][0]
            upperTimeInterval = self.CURRENT_TIME_INTERVAL[type][1]
            # if no event of this type occurred in the last time interval(s),
            # have to move up the current time interval
            while time > upperTimeInterval:
                self.CURRENT_TIME_INTERVAL[type][1] += constants.LOG_TIME_INTERVAL
                upperTimeInterval = self.CURRENT_TIME_INTERVAL[type][1]
            if time >= lowerTimeInterval:
                self.metrics[type].write(str(upperTimeInterval)
                    + " "
                    + str(value) + "\n")
                # update the lower bound
                self.CURRENT_TIME_INTERVAL[type][0] \
                    = self.CURRENT_TIME_INTERVAL[type][1]
        else: # self.log == 'more'
            self.metrics[type].write(str(time)
            + " "
            + str(value) + "\n")

    def linkRate(self, fig):
        time, linkRate = np.loadtxt('linkRateLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)


        ax1 = fig.add_subplot(311)

        ax1.set_xlabel('Time (sec)')
        ax1.set_ylabel('Link rate (Mbps)')

        ax1.plot(time, linkRate, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def bufferOccupancy(self, fig):
        time, buffer = np.loadtxt('bufferLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax2 = fig.add_subplot(312)

        ax2.set_xlabel('Time (sec)')
        ax2.set_ylabel('Buffer Occupancy (pkts)')

        ax2.plot(time, buffer, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))


    def packetLoss(self, fig):
        time, packetLoss = np.loadtxt('packetLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax3 = fig.add_subplot(313)

        ax3.set_xlabel('Time (sec)')
        ax3.set_ylabel('Packet loss (pkts)')

        ax3.plot(time, packetLoss, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax3.get_position()
        ax3.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def flowRate(self, fig):
        time, flowRate = np.loadtxt('flowRateLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax4 = fig.add_subplot(311)

        ax4.set_xlabel('Time (sec)')
        ax4.set_ylabel('Flow rate (Mbps)')

        ax4.plot(time, flowRate, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax4.get_position()
        ax4.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax4.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def windowSize(self, fig):
        time, windowSize = np.loadtxt('windowLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax5 = fig.add_subplot(312)

        ax5.set_xlabel('Time (sec)')
        ax5.set_ylabel('Window size (pkts)')

        ax5.plot(time, windowSize, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax5.get_position()
        ax5.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax5.legend(loc='center left', bbox_to_anchor=(1, 0.5))


    def packetDelay(self, fig):
        time, packetDelay = np.loadtxt('packetLog.txt', delimiter=' ',
                usecols = (0, 1), unpack = True)

        ax6 = fig.add_subplot(313)

        ax6.set_xlabel('Time (sec)')
        ax6.set_ylabel('Packet delay (ms)')

        ax6.plot(time, packetDelay, c='r', label='L1')

        # Shrink current axis by 20%
        box = ax6.get_position()
        ax6.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax6.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def run(self):
        # Starting the metric logging.
        fig = plt.figure(figsize=(10, 6))
        fig2 = plt.figure(figsize=(10, 6))
        self.linkRate(fig)
        self.bufferOccupancy(fig)
        # self.packetLoss(fig)
        # self.flowRate(fig2)
        self.windowSize(fig2)
        # self.packetDelay(fig2)
        fig.subplots_adjust(left = 0.08, right = 0.87, hspace = 0.78)

        plt.show()

