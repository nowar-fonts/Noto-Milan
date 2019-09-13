import json
import codecs
from functools import reduce
from itertools import product
from types import SimpleNamespace as Namespace

class Config:
	version = "1.000"
	fontRevision = 1.000
	vendorId = "????"
	copyright = "Portions Copyright 2015 Google Inc. Portions Copyright(c) Beijing Founder Electronics Co.,Ltd.2019."
	license = "PERSONAL NON-COMMERCIAL USE ONLY. DO NOT DISTRIBUTE THIS FONT SOFTWARE. Noto Sans by Google is licensed under SIL OFL 1.1; Mi Lan Pro VF by Xiaomi is licensed under MIUI EULA."

	fontPackWeight = [ i for i in range(116, 860 + 1, 1) ]
	fontPackRegion = [ "OSF", "GB", "RP" ]

config = Config()

def GetMilanWeight(w):
	if w < 600:
		return max(150, 0.6 * w + 80)
	else:
		return min(w - 160, 700)

widthMap = {
	3: "Condensed",
	5: None,
	7: "Extended",
}

notoWidthMap = {
	3: 80,
	5: 90,
	7: 100,
}

def GetMorpheusWeight(w):
	if w < 400:
		return max(100, w - 100)
	else:
		return min(900, w + 100)

regionNameMap = {
	"GB": "GB18030",
	"RP": "Roleplaying",
	"OSF": "Oldstyle",
}

# set OS/2 encoding to make Windows show font icon in proper language
encoding = [
	"unspec", # 文字美
	"gbk",    # 简体字
	"big5",   # 繁體字
	"jis",    # あア亜
	"korean", # 한글
]

def GetRegion(p):
	if hasattr(p, "region"):
		return p.region
	else:
		return ""

def GenerateFamily(p):
	impl = {
		"Sans": lambda region: "Noto Milan " + regionNameMap[region],
		"UI": lambda region: "Noto Milan UI " + regionNameMap[region],
		"WarcraftSans": lambda region: "Noto Milan Warcraft " + regionNameMap[region],
		"WarcraftUI": lambda region: "Noto Milan Warcraft UI " + regionNameMap[region],
		"Latin": lambda region: "Noto Milan UI LCG",
	}
	return impl[p.family](GetRegion(p))

def GenerateSubfamily(p):
	if p.family == "Noto":
		width = "X{}".format(p.width)
	else:
		width = widthMap[p.width]
	weight = "W{}".format(p.weight)
	if hasattr(p, "italic") and p.italic:
		return ("{} {}".format(width, weight) if width else weight) + " Italic"
	else:
		return "{} {}".format(width, weight) if width else weight

def GenerateFriendlyFamily(p):
	return "{} {}".format(GenerateFamily(p), GenerateSubfamily(p))

def GenerateFilename(p):
	familyName = {
		"Sans": lambda region: "NotoMilan-" + region,
		"UI": lambda region: "NotoMilanUI-" + region,
		"WarcraftSans": lambda region: "NotoMilanWarcraft-" + region,
		"WarcraftUI": lambda region: "NowarMilanWarcraftUI-" + region,
		"Latin": lambda region: "NotoMilanUI",
		"Noto": lambda region: "NotoSans",
		"Milan": lambda region: "MilanPro",
	}
	return (p.encoding + "-" if p.family in [ "Sans", "UI", "WarcraftSans", "WarcraftUI" ] else "") + familyName[p.family](GetRegion(p)) + "-" + GenerateSubfamily(p).replace(" ", "")

def ResolveDependency(p):
	result = {
		"Latin": Namespace(
			family = "Noto",
			width = notoWidthMap[p.width],
			weight = p.weight
		)
	}
	if p.family in [ "WarcraftSans", "WarcraftUI" ]:
		result["Numeral"] = Namespace(
			family = "Noto",
			width = 80,
			weight = p.weight
		)
	if p.family in [ "Sans", "UI", "WarcraftSans", "WarcraftUI" ]:
		result["CJK"] = Namespace(
			family = "Milan",
			width = 5,
			weight = GetMilanWeight(p.weight),
		)
	return result

def GetMorpheus(weight):
	return Namespace(
		weight = GetMorpheusWeight(weight),
		width = 3,
		family = "Latin"
	)

def GetSkurri(weight):
	return Namespace(
		weight = weight,
		width = 7,
		family = "Latin"
	)

def GetLatinFont(weight, region):
	return Namespace(
		weight = weight,
		width = 7,
		family = "UI",
		region = region,
		encoding = "unspec"
	)

def GetLatinChatFont(weight, region):
	return Namespace(
		weight = weight,
		width = 3,
		family = "UI",
		region = region,
		encoding = "unspec"
	)

def GetHansFont(weight, region):
	return Namespace(
		weight = weight,
		width = 5,
		family = "WarcraftSans",
		region = region,
		encoding = "gbk"
	)

def GetHansCombatFont(weight, region):
	return Namespace(
		weight = weight,
		width = 7,
		family = "Sans",
		region = region,
		encoding = "gbk"
	)

def GetHansChatFont(weight, region):
	return Namespace(
		weight = weight,
		width = 3,
		family = "Sans",
		region = region,
		encoding = "gbk"
	)

def GetHantFont(weight, region):
	return Namespace(
		weight = weight,
		width = 5,
		family = "WarcraftSans",
		region = region,
		encoding = "big5"
	)

def GetHantCombatFont(weight, region):
	return Namespace(
		weight = weight,
		width = 7,
		family = "Sans",
		region = region,
		encoding = "big5"
	)

def GetHantNoteFont(weight, region):
	return Namespace(
		weight = weight,
		width = 5,
		family = "Sans",
		region = region,
		encoding = "big5"
	)

def GetHantChatFont(weight, region):
	return Namespace(
		weight = weight,
		width = 3,
		family = "Sans",
		region = region,
		encoding = "big5"
	)


def GetKoreanFont(weight, region):
	return Namespace(
		weight = weight,
		width = 5,
		family = "Sans",
		region = region,
		encoding = "korean"
	)

def GetKoreanCombatFont(weight, region):
	return Namespace(
		weight = weight,
		width = 7,
		family = "Sans",
		region = region,
		encoding = "korean"
	)

def GetKoreanDisplayFont(weight, region):
	return Namespace(
		weight = weight,
		width = 3,
		family = "Sans",
		region = region,
		encoding = "korean"
	)

def ParamToArgument(conf):
	escapeList = [ ' ', '"', '{', '}' ]
	js = json.dumps(conf.__dict__)
	for c in escapeList:
		js = js.replace(c, '\\' + c)
	return js

if __name__ == "__main__":
	makefile = {
		"variable": {
			"VERSION": config.version,
		},
		"rule": {
			".PHONY": {
				"depend": [ "poster-instances" ]
			},
			"all": {
				"command": [
					"echo Noto Milan has more than 2000 flavors. Choose a specific flavor to make.",
					"exit 1",
				]
			},
			"clean": {
				"command": [
					"-rm -rf noto/*.otd milan/*.otd out/*.otd",
					"-rm -rf {}".format(" ".join([ "{}-{}/".format(r, w) for r, w in product(config.fontPackRegion, config.fontPackWeight) ])),
				]
			},
			"milan/MiLanProVF-fix.ttf": {
				"depend": [ "milan/MiLanProVF.ttf" ],
				"command": [
					"cd milan/; python milan-fix.py"
				]
			}
		},
	}

	makefile["rule"]["poster-instances"] = {
		"depend": [ "out/{}.ttf".format(GenerateFilename(GetHansFont(w, "GB"))) for w in range(125, 850 + 1, 25) ],
	}

	# font pack for each regional variant and weight
	for r, w in product(config.fontPackRegion, config.fontPackWeight):
		target = "{}-{}".format(r, w)
		pack = "NotoMilan-{}.7z".format(target)
		fontlist = {
			"ARIALN": GetLatinChatFont(w, r),
			"FRIZQT__": GetLatinFont(w, r),
			"MORPHEUS": GetMorpheus(w),
			"skurri": GetSkurri(w),

			"FRIZQT___CYR": GetLatinFont(w, r),
			"MORPHEUS_CYR": GetMorpheus(w),
			"SKURRI_CYR": GetSkurri(w),

			"ARKai_C": GetHansCombatFont(w, r),
			"ARKai_T": GetHansFont(w, r),
			"ARHei": GetHansChatFont(w, r),

			"arheiuhk_bd": GetHantChatFont(w, r),
			"bHEI00M": GetHantNoteFont(w, r),
			"bHEI01B": GetHantChatFont(w, r),
			"bKAI00M": GetHantCombatFont(w, r),
			"blei00d": GetHantFont(w, r),
		}

		makefile["rule"][pack] = {
			"depend": [ "{}/Fonts/{}.ttf".format(target, f) for f in fontlist ],
			"command": [
				"cd {};".format(target) +
				"cp ../LICENSE.txt Fonts/LICENSE.txt;" +
				"7z a -t7z -m0=LZMA:d=512m:fb=273 -ms ../$@ Fonts/"
			]
		}

		for f, p in fontlist.items():
			makefile["rule"]["{}/Fonts/{}.ttf".format(target, f)] = {
				"depend": [ "out/{}.ttf".format(GenerateFilename(p)) ],
				"command": [
					"mkdir -p {}/Fonts".format(target),
					"cp $^ $@",
				]
			}

	# Sans, UI
	for f, w, wd, r in product([ "Sans", "UI" ], config.fontPackWeight, [3, 5, 7], regionNameMap.keys()):
		param = Namespace(
			family = f,
			weight = w,
			width = wd,
			region = r,
			encoding = "unspec",
		)
		makefile["rule"]["out/{}.ttf".format(GenerateFilename(param))] = {
			"depend": ["out/{}.otd".format(GenerateFilename(param))],
			"command": [ "otfccbuild -O3 --keep-average-char-width $< -o $@ 2>/dev/null" ]
		}
		dep = ResolveDependency(param)
		makefile["rule"]["out/{}.otd".format(GenerateFilename(param))] = {
			"depend": [
				"noto/{}.otd".format(GenerateFilename(dep["Latin"])),
				"milan/{}.otd".format(GenerateFilename(dep["CJK"])),
			],
			"command": [ 
				"mkdir -p out/",
				"python merge.py {}".format(ParamToArgument(param))
			]
		}
		makefile["rule"]["noto/{}.otd".format(GenerateFilename(dep["Latin"]))] = {
			"depend": [ "noto/{}.ttf".format(GenerateFilename(dep["Latin"])) ],
			"command": [ "otfccdump --ignore-hints $< -o $@" ]
		}
		makefile["rule"]["noto/{}.ttf".format(GenerateFilename(dep["Latin"]))] = {
			"depend": [ "noto/NotoSans-VF.ttf" ],
			"command": [ "fonttools varLib.mutator $< wght={} wdth={} -o $@ ".format(dep["Latin"].weight, dep["Latin"].width) ]
		}
		makefile["rule"]["milan/{}.otd".format(GenerateFilename(dep["CJK"]))] = {
			"depend": [ "milan/{}.ttf".format(GenerateFilename(dep["CJK"])) ],
			"command": [ "otfccdump --ignore-hints $< -o $@" ]
		}
		makefile["rule"]["milan/{}.ttf".format(GenerateFilename(dep["CJK"]))] = {
			"depend": [ "milan/MiLanProVF-fix.ttf" ],
			"command": [ "fonttools varLib.mutator $< wght={} -o $@ ".format(dep["CJK"].weight) ]
		}

		# set encoding
		for e in [ "gbk", "big5", "jis", "korean" ]:
			enc = Namespace(
				family = f,
				weight = w,
				width = wd,
				region = r,
				encoding = e,
			)
			makefile["rule"]["out/{}.ttf".format(GenerateFilename(enc))] = {
				"depend": ["out/{}.otd".format(GenerateFilename(enc))],
				"command": [ "otfccbuild -O3 --keep-average-char-width $< -o $@ 2>/dev/null" ]
			}
			makefile["rule"]["out/{}.otd".format(GenerateFilename(enc))] = {
				"depend": ["out/{}.otd".format(GenerateFilename(param))],
				"command": [ "python set-encoding.py {}".format(ParamToArgument(enc)) ]
			}

	# WarcraftSans
	for w, r in product(config.fontPackWeight, regionNameMap.keys()):
		param = Namespace(
			family = "WarcraftSans",
			weight = w,
			width = 5,
			region = r,
			encoding = "unspec",
		)
		makefile["rule"]["out/{}.ttf".format(GenerateFilename(param))] = {
			"depend": ["out/{}.otd".format(GenerateFilename(param))],
			"command": [ "otfccbuild -O3 --keep-average-char-width $< -o $@ 2>/dev/null" ]
		}
		dep = ResolveDependency(param)
		makefile["rule"]["out/{}.otd".format(GenerateFilename(param))] = {
			"depend": [
				"noto/{}.otd".format(GenerateFilename(dep["Latin"])),
				"noto/{}.otd".format(GenerateFilename(dep["Numeral"])),
				"milan/{}.otd".format(GenerateFilename(dep["CJK"])),
			],
			"command": [ 
				"mkdir -p out/",
				"python merge.py {}".format(ParamToArgument(param))
			]
		}
		makefile["rule"]["noto/{}.otd".format(GenerateFilename(dep["Latin"]))] = {
			"depend": [ "noto/{}.ttf".format(GenerateFilename(dep["Latin"])) ],
			"command": [ "otfccdump --ignore-hints $< -o $@" ]
		}
		makefile["rule"]["noto/{}.ttf".format(GenerateFilename(dep["Latin"]))] = {
			"depend": [ "noto/NotoSans-VF.ttf" ],
			"command": [ "fonttools varLib.mutator $< wght={} wdth={} -o $@ ".format(dep["Latin"].weight, dep["Latin"].width) ]
		}
		makefile["rule"]["noto/{}.otd".format(GenerateFilename(dep["Numeral"]))] = {
			"depend": [ "noto/{}.ttf".format(GenerateFilename(dep["Numeral"])) ],
			"command": [ "otfccdump --ignore-hints $< -o $@" ]
		}
		makefile["rule"]["noto/{}.ttf".format(GenerateFilename(dep["Numeral"]))] = {
			"depend": [ "noto/NotoSans-VF.ttf" ],
			"command": [ "fonttools varLib.mutator $< wght={} wdth={} -o $@ ".format(dep["Numeral"].weight, dep["Numeral"].width) ]
		}
		makefile["rule"]["milan/{}.otd".format(GenerateFilename(dep["CJK"]))] = {
			"depend": [ "milan/{}.ttf".format(GenerateFilename(dep["CJK"])) ],
			"command": [ "otfccdump --ignore-hints $< -o $@" ]
		}
		makefile["rule"]["milan/{}.ttf".format(GenerateFilename(dep["CJK"]))] = {
			"depend": [ "milan/MiLanProVF-fix.ttf" ],
			"command": [ "fonttools varLib.mutator $< wght={} -o $@ ".format(dep["CJK"].weight) ]
		}

		for e in [ "gbk", "big5", "jis", "korean" ]:
			enc = Namespace(
				family = "WarcraftSans",
				weight = w,
				width = 5,
				region = r,
				encoding = e,
			)
			makefile["rule"]["out/{}.ttf".format(GenerateFilename(enc))] = {
				"depend": ["out/{}.otd".format(GenerateFilename(enc))],
				"command": [ "otfccbuild -O3 --keep-average-char-width $< -o $@ 2>/dev/null" ]
			}
			makefile["rule"]["out/{}.otd".format(GenerateFilename(enc))] = {
				"depend": ["out/{}.otd".format(GenerateFilename(param))],
				"command": [ "python set-encoding.py {}".format(ParamToArgument(enc)) ]
			}

	# Latin
	for w, wd in product(config.fontPackWeight + [ GetMorpheusWeight(w) for w in config.fontPackWeight ], [3, 5, 7]):
		param = Namespace(
			family = "Latin",
			weight = w,
			width = wd,
		)
		makefile["rule"]["out/{}.ttf".format(GenerateFilename(param))] = {
			"depend": ["out/{}.otd".format(GenerateFilename(param))],
			"command": [ "otfccbuild -O3 --keep-average-char-width $< -o $@ 2>/dev/null" ]
		}
		dep = ResolveDependency(param)
		makefile["rule"]["out/{}.otd".format(GenerateFilename(param))] = {
			"depend": [
				"noto/{}.otd".format(GenerateFilename(dep["Latin"])),
			],
			"command": [ 
				"mkdir -p out/",
				"python merge.py {}".format(ParamToArgument(param))
			]
		}
		makefile["rule"]["noto/{}.otd".format(GenerateFilename(dep["Latin"]))] = {
			"depend": [ "noto/{}.ttf".format(GenerateFilename(dep["Latin"])) ],
			"command": [ "otfccdump --ignore-hints $< -o $@" ]
		}
		makefile["rule"]["noto/{}.ttf".format(GenerateFilename(dep["Latin"]))] = {
			"depend": [ "noto/NotoSans-VF.ttf" ],
			"command": [ "fonttools varLib.mutator $< wght={} wdth={} -o $@ ".format(dep["Latin"].weight, dep["Latin"].width) ]
		}

	# dump `makefile` dict to actual “GNU Makefile”
	makedump = ""

	for var, val in makefile["variable"].items():
		makedump += "{} = {}\n".format(var, val)

	for tar, recipe in makefile["rule"].items():
		dep = recipe["depend"] if "depend" in recipe else []
		makedump += "{}: {}\n".format(tar, " ".join(dep))
		com = recipe["command"] if "command" in recipe else []
		for c in com:
			makedump += "\t{}\n".format(c)

	with codecs.open("Makefile", 'w', 'UTF-8') as mf:
		mf.write(makedump)
