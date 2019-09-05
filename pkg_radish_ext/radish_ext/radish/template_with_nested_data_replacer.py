# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import re
from string import Template

from radish_ext.sdk.l import Logging


def dot_to_dict_notation(dot_notation):
    """ replace dot_notation to nested_python_dict_notation
    so that It can be later used in nested dictionary value evaluation

    Input: '''a.b[2].c.d['1'].e'''
    Output: '''['a']['b'][2]['c']['d']['1']['e']'''
    NOTE the list indices and 'numbers_as_keys' are kept

    :param dot_notation:
    :return:
    """

    return TemplateForNestedDict.dot_to_dict_notation(dot_notation)


class TemplateForNestedDict(Template):
    '''Render "string template with ${a.b.c} ${a.b.c} parameter" using some dict as a data_source
    OR LEAVE IT UNCHANGED if no data under a.b.c path in given dict as a data_source
    Note: it works with list indexes also: ${e.f[3].g}
    Note: Based on string.Template

    Usage:
    a  = """text with parametrized: ${realm_one.client_one.client_fields[0].a} sth"""
    ax = """text with parametrized: {some_value} sth""".format(some_value=some_value)
    assert_equal(ax, TemplateForNestedDict(a).safe_substitute(**test_data))

    where:
    some_value = 997
    test_data = {
        "realm_one": {
            "client_one": {
                "client_secret": """III - realm_one.client_one.client_secret""",
                "client_fields": [{'name': 'tyy', 'a': some_value}, {'name': 'zzzz', 'a': 'b'}]
            }
        }
    }

    '''

    # regexp to match dot_notation with spaces and 'minus' characters and []
    idpattern = r'[a-zA-Z_][a-zA-Z0-9_ -]*((\.[a-zA-Z_][a-zA-Z0-9_ -]*)|(\[[0-9]*\]))*'
    # how many reattempts for safe_substitute_circular()
    max_hops_luck = 7

    def __init__(self, template):
        super(TemplateForNestedDict, self).__init__(template)
        self.log = Logging.get_object_logger(self)

    @classmethod
    def dot_to_dict_notation(cls, dot_notation):
        """ replace dot_notation to nested_python_dict_notation
        so that It can be later used in nested dictionary value evaluation

        Input: '''a.b[2].c.d['1'].e'''
        Output: '''['a']['b'][2]['c']['d']['1']['e']'''
        NOTE the list indices and 'numbers_as_keys' are kept

        :param dot_notation:
        :return:
        """

        # https://regex101.com/r/5BhJeE/2
        # https://regex101.com/r/5BhJeE/1/codegen?language=python
        regex = r"(?:[\.'\[])*([_a-z][_a-z0-9- ]*)(?:[\.\]'])*"
        subst = "['\\1']"
        output = re.sub(regex, subst, dot_notation, 0, re.IGNORECASE | re.DOTALL)
        log = Logging.get_object_logger(cls)
        log.debug("transform: {dot_notation} ==> {output}".format(**locals()))
        return output

    def substitute(self, **kws):
        """attempt one template expansion or throw an exception """

        return self.__substitute(False, **kws)

    def safe_substitute(self, **kws):
        """attempt one template expansion or return template unchanged """

        return self.__substitute(True, **kws)

    def safe_substitute_circular(self, **kws):
        """attempt up to 7 template expansions then return whatever got expanded """
        results = [self.template]

        def last_two_equal(ll):
            return ll[-1] == ll[-2]

        while True:
            results.append(self.__substitute(True, **kws))
            self.template = results[-1]
            # print("check length>self.max_hops_luck: {}".format(len(results)>self.max_hops_luck))
            # print("check last two equal: {}".format(last_two_equal(results)))
            if len(results) > self.max_hops_luck:
                self.log.debug(
                    "circular replace, break loop: too much iterations (max:{})".format(self.max_hops_luck))
                break
            if last_two_equal(results):
                self.log.debug("circular replace, break loop: no change in last rendering")
                break

        # print len(results)
        return results[-1]

    def __substitute(self, __safe_replace=True, **kws):
        """internal method that does the thing, it is intentionally made internal

        :type __safe_replace: bool #return unchanged if data location not found in **kws
        :type kws: **dict
        :rtype: string
        """

        mapping = kws

        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') or mo.group('braced')
            # print("key to search: {}".format(named))
            if named is not None:
                named_canonical = self.dot_to_dict_notation(named)
                try:
                    # val = mapping[named]
                    val = eval('{}{}'.format(mapping, named_canonical, ))
                    # We use this idiom instead of str() because the latter will
                    # fail if val is a Unicode containing non-ASCII characters.
                    return '%s' % (val,)
                except:
                    if not __safe_replace:
                        self.log.exception(
                            'MISSING DATA \n\tnamed: {named} ; \n\tnamed_canonical:{named_canonical}; \n\t in template: """{self.template}""" '.format(
                                **locals()))
                        raise
                    return mo.group()
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)

        output = self.pattern.sub(convert, self.template)
        self.log.info("IN : {template}".format(template=self.template))
        self.log.info("OUT: {output}".format(**locals()))
        return output


if __name__ == '__main__':

    some_value = 997
    test_data = {
        "keycloack-0": {"realm the second": 1},
        "realm_one": {"client_one": {
            "client_secret": '''III - realm_one.client_one.client_secret''',
            "client_fields": [{'name': 'first', 'a': some_value}, {'name': 'second', 'a': 'b'}, ]}},
        "a": {"b": [
            None,
            None,
            {'c': {'d': [None, {'e': 123}]}}]
        },
        "e": {"f": """${g.h}""", "two_infinite_loop": "yes please"}, "g": {"h": """${e.f}"""},
        "s": {"w": """${d.e}""", "three_infinite_loop": "no problem"}, "d": {"e": """${f.r}"""},
        "f": {"r": """${s.w}"""},
        "ccccccc": {"ddddddd": """${cccccc.dddddd}""", "eigth_hops": "you're doing sth. wrong, my crazy one.. nope."},
        "cccccc": {"dddddd": """${ccccc.ddddd}"""},
        "ccccc": {"ddddd": """${cccc.dddd}"""},
        "cccc": {"dddd": """${ccc.ddd}"""},
        "ccc": {"ddd": """${cc.dd}""", "four_hops": "welcome"},
        "cc": {"dd": """${c.d}"""},
        "c": {"d": """${keycloack-0.realm the second}"""},
    }

    dot_notation_raw = [
        """keycloack-0""",
        """keycloack-0.realm the second""",
        """realm_one""",
        """realm_one.client_one""",
        """realm_one.client_one.client_secret""",
        """realm_one.client_one.client_fields[0]""",
        """realm_one.client_one.client_fields[0].name""",
        """a.b[2].c.d[1].e""",
    ]

    dict_notation = [
        """['keycloack-0']""",
        """['keycloack-0']['realm the second']""",
        """['realm_one']""",
        """['realm_one']['client_one']""",
        """['realm_one']['client_one']['client_secret']""",
        """['realm_one']['client_one']['client_fields'][0]""",
        """['realm_one']['client_one']['client_fields'][0]['name']""",
        """['a']['b'][2]['c']['d'][1]['e']""",
    ]

    dot_notation_raw_missng = [
        """realm_one.client_two""",
        """realm_one.client_one.client_fields[13].name""",
        """a.b[2].c.d[0].e""",
        """a.b[2].c.d[1].e.f""",
    ]

    dict_notation_missing = [
        """['realm_one']['client_two']""",
        """['realm_one']['client_one']['client_fields'][13]['name']""",
        """['a']['b'][2]['c']['d'][0]['e']""",
        """['a']['b'][2]['c']['d'][1]['e']['f']""",
    ]

    from json import dumps

    print("TEST DATA: \n{}".format(dumps(test_data, indent=True, sort_keys=True)))

    import nose
    from nose.tools import assert_equal, raises


    def __check_dot_to_dict_notation(dot_notation, dict_notation):
        a = dot_notation
        a_expected = dict_notation
        # a_result = TemplateForNestedDict.dot_to_dict_notation(a)
        a_result = dot_to_dict_notation(a)
        assert_equal(a_expected, a_result)


    def test_dot_to_dict_notation():
        """verify proper transformation from dot-notation to python specific dictionary notation"""
        for ddoct, ddict in zip(dot_notation_raw, dict_notation):
            yield __check_dot_to_dict_notation, ddoct, ddict


    def test_verify_stuff_single_item():
        """verify composite replacement with existing data: ${realm_one.client_one.client_fields[0].a}
        """
        a = """text with parametrized: ${realm_one.client_one.client_fields[0].a} sth"""
        a_expected = """text with parametrized: {some_value} sth""".format(some_value=some_value)

        a_result = TemplateForNestedDict(a).safe_substitute(**test_data)
        assert_equal(a_expected, a_result)


    def test_verify_stuff_double_item():
        """verify composite double replacement with existing data: ${realm_one.client_one.client_fields[0].a}
        """
        a = """some fields values: [${realm_one.client_one.client_fields[0].name}|${realm_one.client_one.client_fields[1].name}] (from template) """
        a_expected = """some fields values: [first|second] (from template) """

        a_result = TemplateForNestedDict(a).safe_substitute(**test_data)
        assert_equal(a_expected, a_result)


    def test_verify_eigth_hops_no_luck():
        """verify_eigth_hops no luck"""
        a = """xxx ${ccccccc.ddddddd} - ${cccccc.dddddd} ${ccccc.ddddd} ${cccc.dddd} - ${ccc.ddd} ${cc.dd} ${c.d} ${keycloack-0.realm the second} yyy"""
        a_expected = """xxx ${keycloack-0.realm the second} - 1 1 1 - 1 1 1 1 yyy"""

        a_result = TemplateForNestedDict(a).safe_substitute_circular(**test_data)
        assert_equal(a_expected, a_result)


    def test_verify_four_hops():
        """verify_four_hops"""
        a = """xxx ${c.d} ${cc.dd} ${ccc.ddd} yyy"""
        a_expected = """xxx 1 1 1 yyy"""

        a_result = TemplateForNestedDict(a).safe_substitute_circular(**test_data)
        assert_equal(a_expected, a_result)


    def test_verify_one_sweep():
        """verify_one_sweep"""
        a = """xxx ${keycloack-0.realm the second} ${c.d} ${cc.dd} ${ccc.ddd} yyy"""
        a_expected = """xxx 1 ${keycloack-0.realm the second} ${c.d} ${cc.dd} yyy"""

        a_result = TemplateForNestedDict(a).safe_substitute(**test_data)
        assert_equal(a_expected, a_result)


    def test_verify_inifinite_loop_of_two():
        """verify_inifinite_loop_of_two"""
        a = """xxx ${e.f} yyy"""
        a_expected = """xxx ${g.h} yyy"""

        a_result = TemplateForNestedDict(a).safe_substitute_circular(**test_data)
        assert_equal(a_expected, a_result)


    def test_verify_inifinite_loop_of_three():
        """verify_inifinite_loop_of_three"""
        a = """xxx ${d.e} yyy"""
        a_expected = """xxx ${f.r} yyy"""

        a_result = TemplateForNestedDict(a).safe_substitute_circular(**test_data)
        assert_equal(a_expected, a_result)


    def __check_value_from_both_notations(dot_notation, dict_notation):
        # put dot notation into ${..}
        new_fashion_item = "${{{}}}".format(dot_notation)

        old_fashion_read_syntax = '{}{}'.format('test_data', dict_notation)
        try:
            old_fasion_value = "{}".format(eval(old_fashion_read_syntax))
        except:
            print("check string not modified".upper())
            old_fasion_value = new_fashion_item

        new_fasion_value = TemplateForNestedDict(new_fashion_item).safe_substitute_circular(**test_data)
        assert_equal(old_fasion_value, new_fasion_value)


    def test_verify_same_value_both_methods():
        """verify proper value resolved from both dot-notation and python specific dictionary notation"""
        for ddoct, ddict in zip(dot_notation_raw, dict_notation):
            yield __check_value_from_both_notations, ddoct, ddict


    def test_verify_orig_string_when_no_data():
        """verify same template returned when no data could be resolved"""
        for ddoct, ddict in zip(dot_notation_raw_missng, dict_notation_missing):
            yield __check_value_from_both_notations, ddoct, ddict


    @raises(Exception)
    def __verify_exception_when_no_data(dot_notation_raw):
        # put dot notation into ${..}
        a = "${{{}}}".format(dot_notation_raw)
        a_result = TemplateForNestedDict(a).substitute(**test_data)


    def test_verify_exception_when_no_data():
        for ddoct in dot_notation_raw_missng:
            yield __verify_exception_when_no_data, ddoct


    @raises(Exception)
    def test_nothing_to_expand_actually_unsafe():
        a = """test $not:hing { to_$expand} a(ctua)lly{ """
        a_expected = "{}".format(a)
        a_result = TemplateForNestedDict(a).substitute(**locals())


    def test_nothing_to_expand_actually():
        a = """test $not:hing { to_$expand} a(ctua)lly{ """
        a_expected = "{}".format(a)
        a_result = TemplateForNestedDict(a).safe_substitute(**locals())
        assert_equal(a_expected, a_result)


    def test_old_school_like_template():
        a = "${param_name}"
        param_name = "alamako"
        a_expected = "{}".format(param_name)
        a_result = TemplateForNestedDict(a).substitute(**locals())
        assert_equal(a_expected, a_result)
        a_result = TemplateForNestedDict(a).safe_substitute_circular(**locals())
        assert_equal(a_expected, a_result)


    @raises(Exception)
    def test_old_school_like_template_missing():
        a = "${param_name_foo_bar}"
        param_name = "alamako"
        a_expected = "{}".format(param_name)
        a_result = TemplateForNestedDict(a).substitute(**locals())
        assert_equal(a_expected, a_result)


    nose.runmodule()
