#!/usr/bin/env python

"""
test code for nc_particles

not very complete

designed to be run with pytest

"""
# for py2/3 compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

import nc_particles

def test_init():
    """
    Can the classes be intitialized?
    """
    w = nc_particles.Writer()
    r = nc_particles.Reader()


