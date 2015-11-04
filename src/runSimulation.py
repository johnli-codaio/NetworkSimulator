import argparse
import json
import pprint
import classes

def main():
    """# parser = argparse.ArgumentParser(description = 'Run simulation on JSON file.')
    # parser.add_argument('--json', '-j', action = 'store', dest = 'json_file_name', 
    #                     help = 'Store JSON file name')
    # # TODO: options for method of congestion control?
    # # 

    # args = parser.parse_args()

    # f = open(args.json_file_name) 

    # TODO: uncomment above, this  line below is for testing"""
    f = open("test0.json")

    parsed_data = json.loads(f.read())

    pprint.pprint(parsed_data)

    devices = {}
    links = {}

    print "\n\n"

    print "Iterating over hosts:"
    for host_name in parsed_data['hosts']:
        print "Host ", str(host_name), "has data: ", parsed_data['hosts'][host_name]
        host = classes.Host(str(host_name))
        devices[str(host_name)] = host

    print "Iterating over routers:"
    for router_name in parsed_data['routers']:
        print "Router ", str(router_name), "has data: ", parsed_data['routers'][router_name]
        router = classes.Router(str(router_name))
        devices[str(router_name)] = router
    print "Hosts and routers found: ", devices, "\n\n"

    print "Iterating over links and adding to hosts/routers:"
    for link_name in parsed_data['links']:
        link_data = parsed_data['links'][link_name]
        print "Link ", str(link_name), "has data: ", link_data

        link = classes.Link(str(link_name), link_data['link_rate'], link_data['link_delay'], 
                            link_data['link_buffer'], 
                            link_data['devices'][0], link_data['devices'][1])
        links[str(link_name)] = link

        devices[str(link_data['devices'][0])].attachLink(link)
        devices[str(link_data['devices'][1])].attachLink(link)

    print "Links found: ", links, "\n\n"






if __name__ == "__main__":
    main()


