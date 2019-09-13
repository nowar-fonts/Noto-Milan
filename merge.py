import sys
import copy
import json
import codecs
from types import SimpleNamespace as Namespace
from fontlib.merge import MergeBelow
from fontlib.pkana import ApplyPalt
from fontlib.dereference import Dereference
from fontlib.transform import Transform, ChangeAdvanceWidth
from fontlib.gsub import GetGsubFlat
from fontlib.gsub import ApplyGsubSingle
import configure

def NameFont(param, font):
	family = configure.GenerateFamily(param)
	subfamily = configure.GenerateSubfamily(param)
	friendly = configure.GenerateFriendlyFamily(param)

	font['head']['fontRevision'] = configure.config.fontRevision
	font['OS_2']['achVendID'] = configure.config.vendorId
	font['OS_2']['usWeightClass'] = param.weight
	font['OS_2']['usWidthClass'] = param.width
	font['name'] = [
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 0,
			"nameString": configure.config.copyright
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 1,
			"nameString": friendly
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 2,
			"nameString": "Regular"
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 3,
			"nameString": "{} {}".format(friendly, configure.config.version)
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 4,
			"nameString": friendly
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 5,
			"nameString": configure.config.version
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 6,
			"nameString": friendly.replace(" ", "-")
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 13,
			"nameString": configure.config.license
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 16,
			"nameString": family
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 17,
			"nameString": subfamily
		},
	]

	if 'CFF_' in font:
		cff = font['CFF_']
		cff['version'] = configure.config.version
		if 'notice' in cff:
			del cff['notice']
		cff['copyright'] = configure.config.copyright
		cff['fontName'] = friendly.replace(" ", "-")
		cff['fullName'] = friendly
		cff['familyName'] = family
		cff['weight'] = subfamily

if __name__ == '__main__':
	param = sys.argv[1]
	param = Namespace(**json.loads(param))

	dep = configure.ResolveDependency(param)

	with open("noto/{}.otd".format(configure.GenerateFilename(dep['Latin'])), 'rb') as baseFile:
		baseFont = json.loads(baseFile.read().decode('UTF-8', errors='replace'))
	NameFont(param, baseFont)

	baseFont['hhea']['ascender'] = 850
	baseFont['hhea']['descender'] = -150
	baseFont['hhea']['lineGap'] = 200
	baseFont['OS_2']['sTypoAscender'] = 850
	baseFont['OS_2']['sTypoDescender'] = -150
	baseFont['OS_2']['sTypoLineGap'] = 200
	baseFont['OS_2']['fsSelection']['useTypoMetrics'] = True
	baseFont['OS_2']['usWinAscent'] = 1050
	baseFont['OS_2']['usWinDescent'] = 300

	# oldstyle figure
	if configure.GetRegion(param) == "OSF":
		ApplyGsubSingle('pnum', baseFont)
		ApplyGsubSingle('onum', baseFont)

	# replace numerals
	if param.family in [ "WarcraftSans", "WarcraftUI" ]:
		with open("noto/{}.otd".format(configure.GenerateFilename(dep['Numeral'])), 'rb') as numFile:
			numFont = json.loads(numFile.read().decode('UTF-8', errors='replace'))

			maxWidth = 490
			numWidth = numFont['glyf']['zero']['advanceWidth']
			changeWidth = maxWidth - numWidth if numWidth > maxWidth else 0

			gsubPnum = GetGsubFlat('pnum', numFont)
			gsubTnum = GetGsubFlat('tnum', numFont)
			gsubOnum = GetGsubFlat('onum', numFont)

			num = [ 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine' ]
			pnum = [ gsubPnum[n] for n in num ]
			onum = [ gsubOnum[n] for n in pnum ]
			tonum = [ gsubOnum[n] for n in num ]

			# dereference glyphs for futher modification
			for n in num + pnum + onum + tonum:
				numFont['glyf'][n] = Dereference(numFont['glyf'][n], numFont)

			for n in num + tonum:
				tGlyph = numFont['glyf'][n]
				tWidth = tGlyph['advanceWidth']
				pName = gsubPnum[n]
				pGlyph = numFont['glyf'][pName]
				pWidth = pGlyph['advanceWidth']
				if pWidth > tWidth:
					numFont['glyf'][pName] = copy.deepcopy(tGlyph)
					pGlyph = numFont['glyf'][pName]
					pWidth = tWidth
				if changeWidth != 0:
					ChangeAdvanceWidth(pGlyph, changeWidth)
					Transform(pGlyph, 1, 0, 0, 1, (changeWidth + 1) // 2, 0)

			for n in num + pnum + onum + tonum:
				baseFont['glyf'][n] = numFont['glyf'][n]
			ApplyGsubSingle('pnum', baseFont)

	# merge CJK
	if param.family in [ "Sans", "UI", "WarcraftSans", "WarcraftUI" ]:
		with open("milan/{}.otd".format(configure.GenerateFilename(dep['CJK'])), 'rb') as asianFile:
			asianFont = json.loads(asianFile.read().decode('UTF-8', errors = 'replace'))

		# pre-apply `palt` in UI family
		if "UI" in param.family:
			ApplyPalt(asianFont)

		# for zh-Hant NPC names
		asianFont['cmap'][str(0x2027)] = asianFont['cmap'][str(0x00B7)]

		MergeBelow(baseFont, asianFont)

		# use CJK middle dots, quotes, em-dash and ellipsis in non-UI family
		if "UI" not in param.family:
			for u in [
				0x00B7, # MIDDLE DOT
				0x2014, # EM DASH
				0x2018, # LEFT SINGLE QUOTATION MARK
				0x2019, # RIGHT SINGLE QUOTATION MARK
				0x201C, # LEFT DOUBLE QUOTATION MARK
				0x201D, # RIGHT DOUBLE QUOTATION MARK
				0x2026, # HORIZONTAL ELLIPSIS
				0x2027, # HYPHENATION POINT
			]:
				if str(u) in asianFont['cmap']:
					baseFont['glyf'][baseFont['cmap'][str(u)]] = asianFont['glyf'][asianFont['cmap'][str(u)]]

		# remap `丶` to `·` in RP variant
		if param.region == "RP":
			baseFont['cmap'][str(ord('丶'))] = baseFont['cmap'][str(ord('·'))]

	outStr = json.dumps(baseFont, ensure_ascii=False)
	with codecs.open("out/{}.otd".format(configure.GenerateFilename(param)), 'w', 'UTF-8') as outFile:
		outFile.write(outStr)
