#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import logging
import pyroute2
import ipaddress


class _PluginObject:

    def init2(self, cfg, tmpDir, ownResolvConf, upCallback, downCallback):
        self.cfg = cfg
        self.tmpDir = tmpDir
        self.ownResolvConf = ownResolvConf
        self.upCallback = upCallback
        self.downCallback = downCallback
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self.businessAttrDict = dict()
        self.bAlive = False

    def get_interface(self):
        return "eth0"

    def start(self):
        curCfg = self.cfg["main"]
        if "nameservers" in curCfg:
            with open(self.ownResolvConf, "w") as f:
                for ns in curCfg["nameservers"]:
                    f.write("nameserver %s\n" % (ns))
            self.logger.info("Nameservers are \"%s\"." % ("\",\"".join(curCfg["nameservers"])))
        self.logger.info("Started.")

    def stop(self):
        with pyroute2.IPRoute() as ipp:
            idx = None
            idx = ipp.link_lookup(ifname="eth0")[0]
            ipp.link("set", index=idx, state="down")
            ipp.flush_addr(index=idx)
            self.downCallback()

        with open(self.ownResolvConf, "w") as f:
            f.write("")
        self.logger.info("Stopped.")

    def is_connected(self):
        return self.bAlive

    def get_ip(self):
        assert self.is_connected()
        curCfg = self.cfg["main"]
        return curCfg["internet-ip"].split("/")[0]

    def get_netmask(self):
        assert self.is_connected()
        curCfg = self.cfg["main"]
        return curCfg["prefix"].split("/")[1]

    def get_extra_prefix_list(self):
        assert self.is_connected()
        return []

    def get_business_attributes(self):
        assert self.is_connected()
        return self.businessAttrDict

    def interface_appear(self, ifname):
        curCfg = self.cfg["main"]
        if ifname == "eth0":
            ip = self.cfg["prefix"].split("/")[0]
            bnet = ipaddress.IPv4Network(curCfg["prefix"], strict=False)
            with pyroute2.IPRoute() as ipp:
                idx = ipp.link_lookup(ifname="eth0")[0]
                ipp.link("set", index=idx, state="up")
                ipp.addr("add", index=idx, address=ip, mask=bnet.prefixlen, broadcast=str(bnet.broadcast_address))
                if "gateway" in curCfg:
                    ipp.route('add', dst="0.0.0.0/0", gateway=curCfg["gateway"], oif=idx)
                if "routes" in curCfg:
                    for rt in curCfg["routes"]:
                        ipp.route('add', dst=rt["prefix"], gateway=rt["gateway"], oif=idx)
            self.logger.info("Interface \"%s\" managed." % (ifname))
            self.bAlive = True
            return True

        return False

    def interface_disappear(self, ifname):
        if ifname == "eth0":
            assert self.bAlive
            self.bAlive = False
            self.businessAttrDict = dict()
            self.downCallback()
