from __future__ import absolute_import, division, print_function

from .utils import partition


def pour(offers):
    return offers, []  # accepts all offers


def has(offers, attribute):
    def pred(offer):
        for attrib in offer.attributes:
            if attrib.name == attribute:
                return True
        return False

    return partition(pred, offers)
