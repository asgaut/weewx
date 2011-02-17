# -*- coding: utf-8 -*-
#
#    Copyright (c) 2011 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
#    $Revision$
#    $Author$
#    $Date$
#
"""Test module weewx.units"""

import unittest
import weewx.units

class ConverterTest(unittest.TestCase):
    
    def testConvert(self):
        #Test the US converter:
        c = weewx.units.Converter()
        value_t_m  = (20.01,  "degree_C", "group_temperature")
        value_t_us = (68.018, "degree_F", "group_temperature")
        self.assertEqual(c.convert(value_t_m), value_t_us)
        
        # Test converting a sequence:
        value_t_m_seq = ([10.0, 20.0, 30.0], "degree_C", "group_temperature")
        value_t_us_seq= ([50.0, 68.0, 86.0], "degree_F", "group_temperature")
        self.assertEqual(c.convert(value_t_m_seq), value_t_us_seq)

        # Now the metric converter:
        cm = weewx.units.Converter(weewx.units.MetricUnits)
        self.assertEqual(cm.convert(value_t_us), value_t_m)
        self.assertEqual(cm.convert(value_t_us_seq), value_t_m_seq)
        # Test a no-op conversion (US to US):
        self.assertEqual(c.convert(value_t_us), value_t_us)
        
        # Test impossible conversions:
        self.assertRaises(KeyError, c.convert, (20.01, "foo", "group_temperature"))
        self.assertRaises(KeyError, c.convert, (None, "foo", "group_temperature"))
        self.assertRaises(KeyError, c.convert, (20.01, "degree_C", "group_foo"))
        self.assertRaises(KeyError, c.convert, (20.01, None, "group_temperature"))
        self.assertRaises(KeyError, c.convert, (20.01, "degree_C", None))
        self.assertEqual(c.convert((20.01, None, None)), (20.01, None, None))
        
    def testConvertDict(self):
        d_m =  {'outTemp'   : (20.01, 'degree_C', 'group_temperature'),
                'barometer' : (1002.3, 'mbar', 'group_pressure')}
        d_us = {'outTemp'   : (68.018, "degree_F", "group_temperature"),
                'barometer' : (1002.3 / 33.86, "inHg", "group_pressure")}
        c = weewx.units.Converter()
        d_test = c.convertDict(d_m)
        self.assertEqual(d_us, d_test)
        # Go the other way:
        cm = weewx.units.Converter(weewx.units.MetricUnits)
        d_test = cm.convertDict(d_us)
        self.assertEqual(d_m, d_test)
        
        # Test impossible conversions:
        d_m['outTemp'] = (20.01, 'foo', 'group_temperature')
        self.assertRaises(KeyError, c.convert, d_m)
        d_m['outTemp'] = (20.01, 'degree_C', 'group_foo')
        self.assertRaises(KeyError, c.convert, d_m)
        
    def testTargetUnits(self):
        c = weewx.units.Converter()
        self.assertEqual(c.getTargetUnit('outTemp'),            ('degree_F', 'group_temperature'))
        self.assertEqual(c.getTargetUnit('outTemp', 'max'),     ('degree_F', 'group_temperature'))
        self.assertEqual(c.getTargetUnit('outTemp', 'maxtime'), ('unix_epoch', 'group_time'))
        self.assertEqual(c.getTargetUnit('outTemp', 'count'),   ('count', 'group_count'))
        self.assertEqual(c.getTargetUnit('outTemp', 'sum'),     ('degree_F', 'group_temperature'))
        self.assertEqual(c.getTargetUnit('wind', 'max'),        ('mile_per_hour', 'group_speed'))
        self.assertEqual(c.getTargetUnit('wind', 'vecdir'),     ('degree_compass', 'group_direction'))
        
class ValueHelperTest(unittest.TestCase):
    
    def testFormatting(self):
        value_t = (20.01, "degree_C", "group_temperature")
        vh = weewx.units.ValueHelper(value_t)
        self.assertEqual(vh.string(), "20.0°C")
        self.assertEqual(vh.nolabel("T=%.3f"), "T=20.010")
        self.assertEqual(vh.formatted, "20.0")
        self.assertEqual(vh.raw, 20.01)
        self.assertEqual(str(vh), "20.0°C")
        self.assertEqual(str(vh.degree_F), "68.0°F")
        
    def testFormattingWithConversion(self):
        value_t = (20.01, "degree_C", "group_temperature")
        converter = weewx.units.Converter()
        vh = weewx.units.ValueHelper.convertOnInit(converter, value_t)
        self.assertEqual(str(vh), "68.0°F")
        self.assertEqual(str(vh.degree_C), "20.0°C")
        # Try an impossible conversion:
        self.assertRaises(KeyError, getattr, vh, 'meter')
        
    def testNoneValue(self):
        value_t = (None, "degree_C", "group_temperature")
        converter = weewx.units.Converter()
        vh = weewx.units.ValueHelper.convertOnInit(converter, value_t)
        self.assertEqual(str(vh), "   N/A")
        self.assertEqual(str(vh.degree_C), "   N/A")
        
class ValueDictTest(unittest.TestCase):
    
    def testFormatting(self):
        d_m =  {'outTemp'   : (20.01, 'degree_C', 'group_temperature'),
                'barometer' : (1002.3, 'mbar', 'group_pressure')}
        # Test against the default (US) converter:
        vd = weewx.units.ValueDict(d_m)
        self.assertEqual(str(vd['outTemp']), "20.0°C")
        self.assertEqual(str(vd['outTemp'].degree_F), "68.0°F")
        
    def testFormattingWithConversion(self):
        d_m =  {'outTemp'   : (20.01, 'degree_C', 'group_temperature'),
                'barometer' : (1002.3, 'mbar', 'group_pressure')}
        # Test against the default (US) converter:
        c = weewx.units.Converter()
        vd = weewx.units.ValueDict.convertOnInit(c, d_m)
        self.assertEqual(str(vd['outTemp']), "68.0°F")
        
if __name__ == '__main__':
    unittest.main()
    