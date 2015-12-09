import argparse
import json
import pprint
import classes
import constants
import simulation
import metrics as m


def main():
    # parser = argparse.ArgumentParser(description = 'Run simulation on JSON file.')
    # parser.add_argument('--json', '-j', action = 'store', dest = 'json_file_name',
    #                     help = 'Store JSON file name')
    # options for parsing a JSON file
    parser = argparse.ArgumentParser(description = 'Run simulation on JSON file.')


    parser.add_argument('--json', '-j', action = 'store', dest = 'json_file_name',
                        help = 'Store JSON file name', required = True)

    #option for tcp reno or tcp fast
    tcp_type = parser.add_mutually_exclusive_group(required = True)
    tcp_type.add_argument('--Reno', dest = 'tcp_type',
            action = 'store_const', const = 'Reno',
            help = 'Uses the TCP-Reno congestion control algorithm')

    tcp_type.add_argument("--FAST", dest = 'tcp_type',
            action = 'store_const', const = 'FAST',
            help = 'Uses the TCP-FAST congestion control algorithm')

    # options for graphing metrics
    metrics = parser.add_argument_group()
    metrics.add_argument('-m', dest = 'metrics',
            action = 'store_true', help = 'Print graphs for metrics.\
                    Requires the following subarguments:')

    metricType = metrics.add_mutually_exclusive_group()

    metricType.add_argument('--more', dest = 'log',
            action = 'store_const', const = 'more',
            help = 'Prints a timetrace from collecting\
            all data. See constants.py for more info.\
            Requires the --m argument.')

    metricType.add_argument('--less', dest = 'log',
            action = 'store_const', const = 'less',
            help = 'Prints a timetrace from collecting\
            a single datum per discrete time interval. See constants.py for more info.\
            Subargument for the --m argument.')

    metricType.add_argument('--avg', dest = 'log',
            action = 'store_const', const = 'avg',
            help = 'Prints an approximate (average) timetrace\
            by collecting data over a discrete time interval. See constants.py\
            for more info. Subargument for the --m argument.')

    metrics.add_argument('-l', '--links', nargs='+', type = str,
            action = 'store', dest = 'links', metavar = 'LinkID',
            help = 'Specify which\
            links are to be logged. LinkID must given in the form\
            \'L1\', \'L2\', etc\'. Subargument for the --m argument.')

    metrics.add_argument('-f', '--flows', nargs='+', type = str,
            action = 'store', dest = 'flows', metavar = 'FlowID',
            help = 'Specify which\
            flows are to be logged. FlowID must given in the form\
            \'F1\', \'F2\', etc.\'. Subargument for the --m argument.')


    # TODO: not finished
    # options for verbose? for debugging purposes
    parser.add_argument('-v', action = 'store_true',
            dest = 'verbose',
            help = 'verbose: prints out information about events,\
            event time, and number of elements in priority queue')

    args = parser.parse_args()
    # all subargs must be present if --m is invoked
    if not args.metrics and (args.log is not None or args.links is not None or args.flows is not None):
        parser.print_usage()
        print "Error: -m argument is required."
        return
    # all subargs must be present if --m is invoked
    elif args.metrics and (args.log is None or args.links is None or args.flows is None):
        parser.print_usage()
        print "Error: All of --m's subargments required."
        return


    f = open(args.json_file_name)

    parsed_data = json.loads(f.read())
    if args.verbose:
        print "JSON DATA:"
        print "Parsed:"
        pprint.pprint(parsed_data)

    devices = {}
    links = {}
    flows = {}

    print "\n\n"

    print "Iterating over hosts:"
    for host_name in parsed_data['hosts']:
        print "Host ", host_name, "has data: ", parsed_data['hosts'][host_name]
        host = classes.Host(str(host_name))
        devices[str(host_name)] = host

    print "Iterating over routers:"
    print "TEST:"
    for router_name in parsed_data['routers']:
        print "Router ", router_name, "has data: ", parsed_data['routers'][router_name]
        router = classes.Router(str(router_name))
        devices[str(router_name)] = router
    print "Hosts and routers instantiated. ", "\n\n"

    print "Iterating over links and adding to hosts/routers:"
    for link_name in parsed_data['links']:
        link_data = parsed_data['links'][link_name]
        print "Link ", link_name, "has data: ", link_data

        link = classes.Link(str(link_name), link_data['link_rate'], link_data['link_delay'],
                            link_data['link_buffer'],
                            devices[link_data['devices'][0]], devices[link_data['devices'][1]])
        links[str(link_name)] = link



    print "Links instantiated.", "\n\n"

    print "Iterating over flows:"
    for flow_name in parsed_data['flows']:
        flow_data = parsed_data['flows'][flow_name]
        print "Flow ", flow_name, "has data: ", flow_data

        flow = classes.Flow(str(flow_name), devices[flow_data['flow_src']],
                            devices[flow_data['flow_dest']],
                            flow_data['data_amt'], flow_data['flow_start'], flow_data['theoRTT'])
        flows[str(flow_name)] = flow
    print "Flows instantiated.", "\n\n"

    # verifying metric inputs from command line are correct
    if args.metrics:
        for flowID in args.flows:
            if flowID not in flows.keys():
                print "Bad flowID in argument list."
                return
        for linkID in args.links:
            if linkID not in links.keys():
                print "Bad linkID in argument list."
                return

    network = classes.Network(devices, links, flows)
    met = None
    if args.metrics:
       met  = m.Metrics(args.log, args.flows, args.links)
    simulator = simulation.Simulator(network, args.tcp_type, met)

    # gen routing table
    print "Running..."
    if args.verbose:
        print "Static routing:"

    simulator.staticRouting()
    while not simulator.q.empty():
        result = simulator.processEvent()
        if args.verbose:
            print "processing one event\n" + str(result)

    if args.verbose:
        print "------------NETWORK------------"
        print "----------DEVICE DETAILS----------"
        for device_name in devices:
            print devices[device_name]

        print "----------LINK DETAILS----------"
        for link_name in links:
            print links[link_name]

        print "----------FLOW DETAILS----------"
        for flow_name in flows:
            print flows[flow_name]

        print "----------STARTING SIMULATION------------"

    # Have flows create sending events...
    for flow_name in flows:
        flow = flows[flow_name]

        counter = 0
        timer = flow.flow_start

        newGenEvent = simulation.Event(None, None, "INITIALIZEFLOW", timer, flow)
        simulator.insertEvent(newGenEvent)

    newDynamicRoutingEvent = simulation.Event(None, None, "REROUT", constants.REROUT_TIME, None)
    simulator.insertEvent(newDynamicRoutingEvent)

    while not simulator.q.empty():
        result = simulator.processEvent()
        if args.verbose:
            print "QUEUE SIZE: " + str(simulator.q.qsize()) + "\n" + str(result)

    for flow_name in flows:
        flow = flows[flow_name]
        print "DATA ACKNOWLEDGED: " + str(flow.data_acknowledged)
        print "DATA MADE: " + str(flow.data_amt)

    print "Simulation for ", args.json_file_name[:-4], args.tcp_type, args.log, " done!"
    simulator.done()


if __name__ == "__main__":
    main()


