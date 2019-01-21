#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2019 Abdelkrime Aries <kariminfo0@gmail.com>
#
#  ---- AUTHORS ----
# 2019	Abdelkrime Aries <kariminfo0@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
from aruudy.poetry import foot as f

re_haraka = re.compile(u"[\u064E\u064F\u0650\u0653]")

def get_ameter (text):
    """Get the Arabic meter of a given text.
    Produces the Arabic meter of a given text in prosody form.
    The Arabic meter is composed of two letters:
    - "w" watad (peg) which are vocalized letters
    - "s" sabab (cord) which are vowels and unvocalized letters

    Parameters
    ----------
    text : str
        Arabic text in prosody form.

    Returns
    -------
    str
        Arabic meter of the input text.
        A string composed of "w" and "s".

    """
    ameter = ""
    parts = []
    buf = ""
    for c in text:
        buf += c
        if re_haraka.search(c):
            if buf[: -2].strip():
                ameter += "s" #sabab
                parts.append(buf[: -2])
                buf = buf[-2:]
            ameter += "w" #watad
            parts.append(buf)
            buf = ""
    if buf.strip():
        ameter += "s"
        parts.append(buf)

    return ameter, parts

def a2e_meter (ameter):
    """Transforms an Arabic meter to an English one.
    The Arabic meter uses vocalization as a basis:
    - "w" watad (peg) which are vocalized letters
    - "s" sabab (cord) which are vowels and unvocalized letters
    While English meter uses syllables:
    - "-" for long syllables, equivalent to "ws" in the Arabic one
    - "u" for short syllables, equivalent to "w" in the Arabic one.

    Parameters
    ----------
    ameter : str
        The Arabic meter using the two letters: "w" and "s".

    Returns
    -------
    str
        The English meter using the two characters: "-" and "u".

    """
    res = ameter
    res = res.replace("ws", "-")
    res = res.replace("w", "u")
    return res

def e2a_meter (emeter):
    """Transforms an English meter to an Arabic one.
    The English meter uses syllables as a basis:
    - "-" for long syllables, equivalent to "ws" in the Arabic one
    - "u" for short syllables, equivalent to "w" in the Arabic one.
    While the Arabic meter uses vocalization:
    - "w" watad (peg) which are vocalized letters
    - "s" sabab (cord) which are vowels and unvocalized letters

    Parameters
    ----------
    emeter : str
        The English meter using the two characters: "-" and "u".

    Returns
    -------
    str
        The Arabic meter using the two letters: "w" and "s".

    """
    res = emeter
    res = res.replace("-", "ws")
    res = res.replace("u", "w")
    return res

def extract_meter(feet, used=True):
    """Extract the meter description from a list of :class:`~aruudy.poetry.foot.Tafiila` objects.

    Parameters
    ----------
    feet : list(Tafiila)
        A list of :class:`~aruudy.poetry.foot.Tafiila` objects describing the meter.
    used : bool
        Meters, in Arabic, can have used forms different than standard ones.
        if True: the result is used form.
        Otherwise, it is standard form

    Returns
    -------
    dict
        A dictionary object describing the meter represented by the feet.
        The dictionary contains these elements:
        - type: a string describing the type of each foot (tafiila)
        - mnemonic: a string describing the mnemonic of each foot.
        - emeter: a string describing the English meter of each foot.

    """
    res = {
        "type": "",
        "mnemonic": "",
        "emeter": ""
    }

    sep = ""
    for foot in feet:
        meter = foot.get_meter(used)
        res["type"] += sep + f.ZUHAF_ILLA[meter["type"]]
        res["mnemonic"] += sep + meter["mnemonic"]
        res["emeter"] += sep + meter["emeter"]
        if not sep:
            sep = " "
    return res


buhuur = []

class BahrError (Exception):
    """Exception when :class:`~aruudy.poetry.meter.Bahr` does not have a specif attribute.

    Parameters
    ----------
    name : str
        The name of the attribute in question.

    """
    def __init__(self, name):
        Exception.__init__(self, "Bahr does not have an attribute called: " + name)

class Bahr(object):
    def __init__(self, info):
        self.keys = []
        for key in info:
            setattr(self, key, info[key])
            self.keys.append(key)
        buhuur.append(self)

        self.used_scansion = extract_meter(self.meter[0])
        self.used_scansion["ameter"] = e2a_meter(self.used_scansion["emeter"])
        self.keys.append("used_scansion")

        self.std_scansion = extract_meter(self.meter[0], used=False)
        self.std_scansion["ameter"] = e2a_meter(self.std_scansion["emeter"])
        self.keys.append("std_scansion")

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.get_names())

    def get_names(self):
        return self.get_value("name")

    def test_property(self, key, value, key2=None ):
        val = self.get_value(key, key2)
        return val == value

    def get_value(self, key, key2=None):
        if not key in self.keys:
            raise BahrError(key)
        res = getattr(self, key)
        if key2:
            return res[key2]
        return res

    def to_dict(self):
        dic = {}
        for key in self.keys:
            dic[key] = getattr(self, key)
        del dic["meter"]

        return dic

    def validate(self, emeter):

        for var in self.meter: # different variants
            res = []
            text_emeter = emeter
            for foot in var: # diffent feet of the variant
                text_foot, text_emeter = foot.process(text_emeter)
                if not text_foot:
                    res = None
                    break
                res.append(text_foot)
            if res:
                return res
        return None

tawiil = Bahr({
    "name": {
        "arabic": u"طويل",
        "english": "long",
        "trans": u"ṭawīl"
    },
    "meter": [
        [
        f.WWSWS([f.SALIM, f.QABDH]),
        f.WWSWSWS([f.SALIM, f.QABDH, f.KAFF]),
        f.WWSWS([f.SALIM, f.QABDH]),
        f.WWSWSWS([f.QABDH]),
        ]
    ],
    "key": u"طويلٌ له دون البحور فضائلٌ  فعولن مفاعيلن فعولن مفاعلن"
})

madiid = Bahr({
    "name": {
        "arabic": u"مديد",
        "english": "protracted",
        "trans": u"madīd"
    },
    "meter": [
        [
        f.WSWWSWS([f.SALIM, f.KHABN]),
        f.WSWWS([f.SALIM, f.KHABN]),
        f.WSWWSWS([f.SALIM, f.KHABN])
        ]
    ],
    "key": u"لمديد الشعر عندي صفاتُ  فاعلاتن فاعلن فاعلاتن"
})

basiit = Bahr({
    "name": {
        "arabic": u"بسيط",
        "english": "spread-out",
        "trans": u"basīṭ"
    },
    "meter": [
        [
        f.WSWSWWS([f.SALIM, f.KHABN, f.TAI]),
        f.WSWWS([f.SALIM, f.KHABN]),
        f.WSWSWWS([f.SALIM, f.KHABN, f.TAI]),
        f.WSWWS([f.KHABN, f.QATE]),
        ],
        [
        f.WSWSWWS([f.SALIM, f.KHABN, f.TAI]),
        f.WSWWS([f.SALIM, f.KHABN]),
        f.WSWSWWS([f.SALIM, f.KHABN, f.TAI, f.QATE, f.TADIIL]),
        ],
    ],
    "key": u"إن البسيط لديه يبسط الأملُ  مستفعلن فعلن مستفعلن فعلن"
})

wafir = Bahr({
    "name": {
        "arabic": u"وافر",
        "english": "abundant",
        "trans": u"wāfir"
    },
    "meter": [
        [
        f.WWSWWWS([f.SALIM, f.ASAB]),
        f.WWSWWWS([f.SALIM, f.ASAB]),
        f.WWSWS([f.SALIM]),
        ]
    ],
    "key": u"بحور الشعر وافرها جميل  مفاعلتن مفاعلتن فعولن"
})

kaamil = Bahr({
    "name": {
        "arabic": u"كامل",
        "english": "complete",
        "trans": u"kāmil"
    },
    "meter": [
        [
        f.WWWSWWS([f.SALIM, f.IDHMAR]),
        f.WWWSWWS([f.SALIM, f.IDHMAR]),
        f.WWWSWWS([f.SALIM, f.IDHMAR])
        ],
        [
        f.WWWSWWS([f.SALIM, f.IDHMAR]),
        f.WWWSWWS([f.SALIM, f.IDHMAR])
        ],
    ],
    "key": u"كمل الجمال من البحور الكامل متفاعلن متفاعلن متفاعلن"
})

hazj = Bahr({
    "name": {
        "arabic": u"هزج",
        "english": "trilling",
        "trans": u"hazaj",
    },
    "meter": [
        [
        f.WWSWSWS([f.SALIM, f.KAFF]),
        f.WWSWSWS([f.SALIM, f.KAFF])
        ]
    ],
    "key": u"على الأهزاج تسهيل      مفاعيلن مفاعيلن"
})

rajz = Bahr({
    "name": {
        "arabic": u"رجز",
        "english": "trembling",
        "trans": u"rajaz"
    },
    "meter": [
        [
        f.WSWSWWS([f.SALIM, f.KHABN]),
        f.WSWSWWS([f.SALIM, f.KHABN]),
        f.WSWSWWS([f.SALIM, f.KHABN])
        ]
    ],
    "key": u"في أبحر الأرجاز بحرٌ يسهل   مستفعلن مستفعلن مستفعلن"
})

raml = Bahr({
    "name": {
        "arabic": u"رمل",
        "english": "trotting",
        "trans": u"ramal",
    },
    "meter": [
        [
        f.WSWWSWS([f.SALIM, f.KHABN]),
        f.WSWWSWS([f.SALIM, f.KHABN]),
        f.WSWWSWS([f.SALIM, f.KHABN])
        ]
    ],
    "key": u"رمل الأبحر ترويه الثقات فاعلاتن فاعلاتن فاعلاتن"
})

sariie = Bahr({
    "name": {
        "arabic": u"سريع",
        "english": "swift",
        "trans": u"sarīʿ",
    },
    "meter": [
        [
        f.WSWSWWS([f.SALIM, f.KHABN, f.TAI, f.KHABL]),
        f.WSWSWWS([f.SALIM, f.KHABN, f.TAI, f.KHABL]),
        f.WSWWS([f.SALIM])
        ]
    ],
    "key": u"بحرٌ سريع ماله ساحل مستفعلن مستفعلن فاعلن"
})

munsarih = Bahr({
    "name": {
        "arabic": u"منسرح",
        "english": "quick-paced",
        "trans": u"munsariħ"
    },
    "meter": [
        [
        f.WSWSWWS([f.SALIM, f.KHABN]),
        f.WSWSWSW([f.SALIM, f.TAI]),
        f.WSWSWWS([f.TAI])
        ]
    ],
    "key": u"منسرح فيه يضرب المثل    مستفعلن مفعولات مفتعلن"
})

khafiif = Bahr({
    "name": {
        "arabic": u"خفيف",
        "english": "light",
        "trans": u"khafīf"
    },
    "meter": [
        [
        f.WSWWSWS([f.SALIM, f.KHABN, f.KAFF]),
        f.WSWSWWS([f.SALIM]),
        f.WSWWSWS([f.SALIM, f.KHABN, f.SHAKL])
        ]
    ],
    "key": u"يا خفيفاً خفّت به الحركات   فاعلاتن مستفعلن فاعلاتن"
})

mudharie = Bahr({
    "name": {
        "arabic": u"مضارع",
        "english": "similar",
        "trans": u"muḍāriʿ"
    },
    "meter": [
        [
        f.WWSWSWS([f.SALIM, f.QABDH,f.KAFF]),
        f.WSWWSWS([f.SALIM])
        ]
    ],
    "key": u"تعدّ المضارعات  مفاعيلُ فاعلاتن"
})

muqtadhib = Bahr({
    "name": {
        "arabic": u"مقتضب",
        "english": "untrained",
        "trans": u"muqtaḍab"
    },
    "meter": [
        [
        f.WSWSWSW([f.SALIM, f.KHABN]),
        f.WSWSWWS([f.TAI])
        ]
    ],
    "key": u"اقتضب كما سألوا مفعلات مفتعلن"
})

mujdath = Bahr({
    "name": {
        "arabic": u"مجتث",
        "english": "cut-off",
        "trans": u"mujtathth"
    },
    "meter": [
        [
        f.WSWSWWS([f.SALIM, f.KHABN]),
        f.WSWWSWS([f.SALIM, f.KHABN])
        ]
    ],
    "key": u"أن جثت الحركات  مستفعلن فاعلاتن"
})

mutaqaarib = Bahr({
    "name": {
        "arabic": u"متقارب",
        "english": "nearing",
        "trans": u"mutaqārib"
    },
    "meter": [
        [
        f.WWSWS([f.SALIM, f.QABDH]),
        f.WWSWS([f.SALIM, f.QABDH]),
        f.WWSWS([f.SALIM, f.QABDH]),
        f.WWSWS([f.SALIM, f.QABDH])
        ]
    ],
    "key": u"عن المتقارب قال الخليل      فعولن فعولن فعولن فعول"
})

mutadaarik = Bahr({
    "name": {
        "arabic": u"متدارك",
        "english": "overtaking",
        "trans": u"mutadārik"
    },
    "meter": [
        [
        f.WSWWS([f.SALIM, f.KHABN, f.QATE]),
        f.WSWWS([f.SALIM, f.KHABN, f.QATE]),
        f.WSWWS([f.SALIM, f.KHABN, f.QATE]),
        f.WSWWS([f.SALIM, f.KHABN, f.QATE])
        ]
    ],
    "key": u"حركات المحدث تنتقل  فعلن فعلن فعلن فعل"
})


def name_type(name):
    if re.match("^[a-zA-Z]", name):
        return "english"
    return "arabic"

def get_bahr(name, dic=True):
    """Search for poetry Bahr by name.

    Parameters
    ----------
    name : str
        name of the poetry Bahr (meter).
    dic : bool
        True(default): it returns a dict object with all information.
        If False, it returns an object of type Bahr

    Returns
    -------
    dict
        dict: containing the information.
        or a Bahr object.
        or None

    """
    label = name_type(name)
    for b in buhuur:
        if b.test_property("name", name, label):
            if dic:
                return b.to_dict()
            return b
    return None

def _get_values(attr1, attr2 = None):
    values = []
    for b in buhuur:
        values.append(b.get_value(attr1, attr2))
    return values

def get_names():
    return _get_values("name")

def arabic_names():
    return _get_values("name", "arabic")

def english_names():
    return _get_values("name", "english")

def trans_names():
    return _get_values("name", "trans")

def search_bahr(emeter, ameter=None, names=False):
    for b in buhuur:
        res = b.validate(emeter)
        if res:
            return b, res

    return None, None
