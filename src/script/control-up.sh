#!/bin/bash

# Use tc-u32 to match port(s)



#######################
###    Variables    ###
#######################

dmz_addr="192.168.192.0/22"
dmz_itf="enp"
out_itf="enp1s0"
vm_addr="10.0.2.15"
external_server="192.168.172.1"



#######################
###  Factory state  ###
#######################

iptables -F
iptables -F -t nat
iptables -F -t mangle
iptables -X

# FILTER
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# NAT
iptables -t nat -P PREROUTING ACCEPT
iptables -t nat -P INPUT ACCEPT
iptables -t nat -P OUTPUT ACCEPT
iptables -t nat -P POSTROUTING ACCEPT

# MANGLE
iptables -t mangle -P PREROUTING ACCEPT
iptables -t mangle -P INPUT ACCEPT
iptables -t mangle -P FORWARD ACCEPT
iptables -t mangle -P OUTPUT ACCEPT
iptables -t mangle -P POSTROUTING ACCEPT



######################
###    FIREWALL    ###
######################

iptables -P PREROUTING -t mangle -j DROP
iptables -A PREROUTING -t mangle -p udp --dport WG_UGP_PORTS -j ACCEPT
iptables -A PREROUTING -t mangle -p tcp	-m state --state ESTABLISHED,RELATED -j ACCEPT



#######################
### TRAFFIC CONTROL ###
#######################

tc qdisc add dev $DEV root handle 1:0 prio priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

# METRICS:
# delay ~= latency (latence)
# rate = throughput (débit)
tc qdisc add dev $DEV parent 1:2 handle 20: netem delay $LATENCY rate $THROUGHPUT

tc filter add dev $DEV parent 1:0 protocol ip u32 match ip sport $PORTS 0xffff flowid 1:2

tc filter add dev $DEV parent 1:0 protocol ip basic \
	match "cmp( u16 at 0 layer transport ge $PORT_MIN ) \
	and cmp( u16 at 0 layer transport le $PORT_MAX )" \
	flowid 1:2