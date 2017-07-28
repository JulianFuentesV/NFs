#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer

from mininet.cli import CLI
from mininet.log import setLogLevel, info, output
from mininet.node import OVSSwitch, RemoteController
from mininet.topolib import TreeNet

class S(BaseHTTPRequestHandler):

    def _set_headers(self):
	self.send_response(200)
	self.send_header('Content-type','text/html')
	self.end_headers()

    def do_GET(self):
	self._set_headers()
	path = self.path
	action,params = path.split('?')
	key,functions = params.split('=')
	command = ''
	if(functions.find(',') == -1):
	    #Una sola funcion
	    print(functions)
	    command = command+getCmd(functions)
	else:
	    #Varias funciones
	    funcs = functions.split(',')
	    print('funcs')
	    print(funcs)
	    for f in funcs:
		command = command+getCmd(f)
	print(command)
	self.wfile.write("<html><body>ok</body></html>")
	runTopo(command)
	#self.wfile.write("<html><body><h1>hi!</h1><p>Path: "+path+"</p><p>Action: "+action+"</p><p>Params: "+params+" values: "+v1+v2+v3+"</p></body></html>")
	

def run(server_class=HTTPServer, handler_class=S, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting server on port 8081....')
    try:
	httpd.serve_forever()
    except KeyboardInterrupt:
	pass
    httpd.server_close()

def runTopo(command):
    c0 = RemoteController('c0', ip='127.0.0.1', port=6633)
    setLogLevel( 'info' )
    network = TreeNet( depth=2, fanout=2, switch=OVSSwitch, controller=None )
    network.addController(c0)
    network.start()
#    network.startTerms()
#    CLI.do_px("px print h1.cmd('ifconfig')")
    network['s1'].cmd('ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    network['s2'].cmd('ovs-vsctl set Bridge s2 protocols=OpenFlow13')
    network['s3'].cmd('ovs-vsctl set Bridge s3 protocols=OpenFlow13')
    network['c0'].cmd('export PYTHONPATH=/home/ubuntu/ryu:/home/ubuntu/pox:.')
    info(network['c0'].cmd('echo $PYTHONPATH'))
    network['c0'].cmdPrint('../ryu/bin/ryu-manager --use-syslog --verbose'+command)
#    CLI(network)
    network.stop()

def getCmd(id):
    if id == 'firewall':
	return ' ../ryu/ryu.app.rest_firewall'
    if id == 'loadBalancer':
	return ' ../ryu/ryu.app.sdnhub_apps.stateless_lb_rest'
    if id == 'router':
	return ' ../ryu/ryu.app.rest_router'

if __name__ == '__main__':
#    runTopo()
    from sys import argv

    if len(argv) == 2:
	run(port=int(argv[1]))
    else:
	run()
