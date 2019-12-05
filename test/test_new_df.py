#!/usr/bin/env python3
# Jordan huang<good5dog5@gmail.com>

import os
import sys
import subprocess
import pandas as pd
from unittest import TestCase


class new_df_test(TestCase):
    def setUp(self):
        self.new_df = pd.read_csv('../new_df.csv')

    def test_discount(self):
        for i in self.new_df['discount'].tolist():
            assert i<1 and i > 0



