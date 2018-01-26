#!/usr/bin/env python
#
# MIT License
#
# Copyright (c) 2017 Fabrizio Colonna <colofabrix@tin.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function

import sys
import unittest

import test_awsobjects
import test_schedulers
import test_schedulable
import test_tagscheduler

# Initialize the test suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# Add tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_awsobjects))
suite.addTests(loader.loadTestsFromModule(test_schedulers))
suite.addTests(loader.loadTestsFromModule(test_schedulable))
suite.addTests(loader.loadTestsFromModule(test_tagscheduler))

# Initialize a runner, pass the suite and run it
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Return if tests passed or not
sys.exit(len(result.errors) > 0)

# vim: ft=python:ts=4:sw=4