# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup


def allforms(t):
    return list({t, t.lower(), t.upper(), t.title()})


def token_regexes(elements, case_sensitive):
    tokens = [e.keys()[0].encode('utf-8') for e in elements]
    forms = [[t] if case_sensitive else allforms(t) for t in tokens]
    patterns = [r"\b{0}\b".format(f) for form in forms for f in form]
    return "|".join(patterns)


def element_slices(text, elements, settings):
    """Get slices of all elements in text.
    :param settings:
    :param elements:
    :param text:
    """
    case_sensitive = settings['case_sensitive']
    token_regex = re.compile(token_regexes(elements, case_sensitive))

    element_slices = []
    for match in token_regex.finditer(text):

        token = match.group()
        base = None
        for element in elements:

            check_element = element.keys()[0].encode('utf-8')
            check_token = token

            if case_sensitive is False:
                check_element = check_element.lower()
                check_token = check_token.lower()

            if check_element == check_token:
                base = element
                break

        element_slices.append((token,
                               (match.start(), match.end()),
                               (settings['element_identifier'], base)))
    return element_slices


def unit_slices(text, text_unit_key, text_unit_name, restricted_areas):
    """Get slices of the text units specified in settings.
    :param text_unit_name:
    :param text_unit_key:
    :param text:
    :param restricted_areas:
    """

    units = []
    if (text_unit_key, text_unit_name) == ('t', 'text'):
        # the whole text is one unit
        units.append((text_unit_key, (0, len(text)),
                      (text_unit_name, 0)))

    elif text_unit_name.startswith(('html', 'xml')):
        unit_soup = BeautifulSoup(text, "html.parser").find_all(text_unit_key)
        for i, a_text_unit in enumerate(unit_soup):
            a_text_unit = str(a_text_unit)
            _from = text.index(a_text_unit)
            _to = _from + len(a_text_unit)
            unit = (text_unit_key, (_from, _to), (text_unit_name, i))
            units.append(unit)

        if restricted_areas:
            restricted_elements = identify_restricted_areas(text,
                                                            restricted_areas)
            for unit in restricted_elements:
                units.append(unit)

    else:
        raise NotImplementedError

    return units


def identify_restricted_areas(text, restricted_areas):
    """
    """
    all_tags = BeautifulSoup(text, "html.parser").findAll(True)
    restricted_elements = []
    filter_tags = restricted_areas.get('tags', [])
    filter_classes = restricted_areas.get('classes', [])

    count = 1
    for tag in all_tags:
        if tag.name in filter_tags:
            a_text_unit = str(tag)
            _from = text.index(a_text_unit)
            _to = _from + len(a_text_unit)
            unit = ((tag.name, tag.text), (_from, _to), ('restricted_area', count))
            restricted_elements.append(unit)
            count += 1

        tag_classes = dict(tag.attrs).get('class', '')
        for fclass in filter_classes:
            for tclass in tag_classes:
                if fclass in tclass:
                    a_text_unit = str(tag)
                    _from = text.index(a_text_unit)
                    _to = _from + len(a_text_unit)
                    unit = ((tag.name, tag.text), (_from, _to), ('restricted_area', count))
                    restricted_elements.append(unit)
                    count += 1

    return restricted_elements
