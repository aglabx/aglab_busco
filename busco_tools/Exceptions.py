#!/usr/bin/env python3
# coding: utf-8
"""

Copyright (c) 2021, Aleksey Komissarov (ad3002@gmail.com)
based on Evgeny Zdobnov (ez@ezlab.org)
Licensed under the MIT license. See LICENSE.md file.

"""

class ToolException(Exception):
    """
    Module-specific exception
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class NoGenesError(Exception):
    def __init__(self, gene_predictor):
        self.gene_predictor = gene_predictor

class NoRerunFile(Exception):
    def __init__(self):
        pass