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
iptables -A PREROUTING -t mangle -p tcp --dport 22 -m state --state ESTABLISHED,RELATED -j ACCEPT