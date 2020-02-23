#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import logging


class _PluginObject:

    def init2(self, cfg, api):
        self.cfg = cfg
        self.api = api
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self.bAlive = False

    def get_interface(self):
        return "eth0"

    def start(self):
        self.logger.info("Started.")

    def stop(self):
        if self.bAlive:
            self.bAlive = False
            self.api.deactivate_interface("eth0")
        self.logger.info("Stopped.")

    def interface_appear(self, ifname):
        curCfg = self.cfg["main"]
        if ifname == "eth0":
            ret = {
                "prefix": curCfg["prefix"],
            }
            if "gateway" in curCfg:
                ret["gateway"] = curCfg["gateways"]
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
