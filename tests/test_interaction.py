#!/usr/bin/python
#
# Copyright (C) 2009 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Test crontab interaction.
"""

import os
import sys

sys.path.insert(0, '../')

import unittest
from crontab import CronTab
try:
    from test import test_support
except ImportError:
    from test import support as test_support

INITAL_TAB = """
# First Comment
*/30 * * * * firstcommand
* 10-20/3 * * * range
# Middle Comment
* * * 10 * byweek
 00 5  *   *   *      spaced
@reboot rebooted
# Last Comment"""

COMMANDS = [
    'firstcommand',
    'range',
    'byweek',
    'spaced',
    'rebooted',
]

RESULT_TAB = """
# First Comment
*/30 * * * * firstcommand
* 10-20/3 * * * range
# Middle Comment
* * * 10 * byweek
0 5 * * * spaced
@reboot rebooted
# Last Comment
"""

class BasicTestCase(unittest.TestCase):
    """Test basic functionality of crontab."""
    def setUp(self):
        self.crontab = CronTab(tab=INITAL_TAB)

    def test_01_presevation(self):
        """All Entries Re-Rendered Correctly"""
        self.assertEqual(self.crontab.intab, INITAL_TAB,
            "Inital values are set currently")
        self.crontab.write()
        results = RESULT_TAB.split('\n')
        line_no = 0
        for line in self.crontab.intab.split('\n'):
            self.assertEqual(line, results[line_no])
            line_no += 1

    def test_02_access(self):
        """All Entries Are Accessable"""
        line_no = 0
        for cron in self.crontab:
            self.assertEqual(str(cron.command), COMMANDS[line_no])
            line_no += 1

    def test_03_blank(self):
        """Render Blank"""
        job = self.crontab.new(command='blank')
        self.assertEqual(job.render(), '* * * * * blank')

    def test_04_number(self):
        """Render Number"""
        job = self.crontab.new(command='number')
        job.minute.on(4)
        self.assertEqual(job.render(), '4 * * * * number')

    def test_05_fields(self):
        """Render Hours Days and Weeks"""
        job = self.crontab.new(command='fields')
        job.hour.on(4)
        self.assertEqual(job.render(), '* 4 * * * fields')
        job.dom.on(5)
        self.assertEqual(job.render(), '* 4 5 * * fields')
        job.month.on(6)
        self.assertEqual(job.render(), '* 4 5 6 * fields')
        job.dow.on(7)
        self.assertEqual(job.render(), '* 4 5 6 7 fields')

    def test_06_clear(self):
        """Render Hours Days and Weeks"""
        job = self.crontab.new(command='clear')
        job.minute.on(3)
        job.hour.on(4)
        job.dom.on(5)
        job.month.on(6)
        job.dow.on(7)
        self.assertEqual(job.render(), '3 4 5 6 7 clear')
        job.clear()
        self.assertEqual(job.render(), '* * * * * clear')

    def test_07_range(self):
        job = self.crontab.new(command='range')
        job.minute.during(4,10)
        self.assertEqual(job.render(), '4-10 * * * * range')
        job.minute.during(15,19)
        self.assertEqual(job.render(), '4-10,15-19 * * * * range')
        job.minute.clear()
        self.assertEqual(job.render(), '* * * * * range')
        job.minute.during(15,19)
        self.assertEqual(job.render(), '15-19 * * * * range')

    def test_08_sequence(self):
        job = self.crontab.new(command='seq')
        job.hour.every(4)
        self.assertEqual(job.render(), '* */4 * * * seq')
        job.hour.during(2, 10)
        self.assertEqual(job.render(), '* */4,2-10 * * * seq')
        job.hour.clear()
        self.assertEqual(job.render(), '* * * * * seq')
        job.hour.during(2, 10).every(4)
        self.assertEqual(job.render(), '* 2-10/4 * * * seq')


if __name__ == '__main__':
    test_support.run_unittest(
       BasicTestCase,
    )
