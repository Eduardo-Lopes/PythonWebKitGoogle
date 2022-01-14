#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.

import os

class FileWatcher(object):
    def __init__(self, path):
        self._cached_stamp = 0
        self.filename = path
        self.token = ""

    def get(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            with open(self.filename) as f:
                self.token = f.read()
            
        return self.token

token = None

def on_send_request(webpage, request, response):
    global token
    headers = request.get_http_headers()
    if not headers is None:
        headers.append("Authorization",f"Bearer {token.get()}")

def on_document_loaded(webpage):
    webpage.connect("send-request", on_send_request)

def on_page_created(extension, webpage):
    webpage.connect("document-loaded", on_document_loaded)

def initialize(extension, arguments):
    global token
    print("initialize: extension =", extension)
    print("initialize: arguments =", arguments)
    token = FileWatcher(arguments.get_string())
    extension.connect("page-created", on_page_created)
