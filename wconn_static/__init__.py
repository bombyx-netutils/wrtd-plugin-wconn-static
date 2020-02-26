#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import logging
import pyroute2
import ipaddress


class _PluginObject:

    def start(self, cfg, api):
        self.cfg = cfg
        self.api = api
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self.bAlive = False
        self.logger.info("Started.")

    def stop(self):
        if self.bAlive:
            self.bAlive = False
            self.api.deactivate_interface("eth0")
        self.logger.info("Stopped.")

    def interface_appear(self, ifname):
        curCfg = self.cfg["main"]
        if ifname == "eth0":
            ip = curCfg["prefix"].split("/")[0]
            bnet = ipaddress.IPv4Network(curCfg["prefix"], strict=False)
            with pyroute2.IPRoute() as ipp:
                idx = ipp.link_lookup(ifname=ifname)[0]
                ipp.link("set", index=idx, state="up")
                ipp.addr("add", index=idx, address=ip, mask=bnet.prefixlen, broadcast=str(bnet.broadcast_address))

            ret = {
                "prefix": curCfg["prefix"],
            }
            if "gateway" in curCfg:
                ret["gateway"] = curCfg["gateway"]
            if "nameservers" in curCfg:
                ret["nameservers"] = curCfg["nameservers"]
            if "routes" in curCfg:
                ret["routes"] = curCfg["routes"]
            if "internet-ip" in curCfg:
                ret["internet-ip"] = curCfg["internet-ip"]
            self.api.activate_interface(ifname, ret)
            self.logger.info("Interface \"%s\" managed." % (ifname))
            self.bAlive = True
            return True

        return False

    def interface_disappear(self, ifname):
        if ifname == "eth0":
            assert self.bAlive
            self.bAlive = False
            self.api.deactivate_interface("eth0")
