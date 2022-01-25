#!/usr/bin/env python3
# coding: utf-8
"""

Copyright (c) 2021, Aleksey Komissarov (ad3002@gmail.com)
based on Evgeny Zdobnov (ez@ezlab.org)
Licensed under the MIT license. See LICENSE.md file.

"""

class BatchFatalError(Exception):
    """
    Error that prevents batch mode from running.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class BuscoError(Exception):
    """
    Module-specific exception
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
