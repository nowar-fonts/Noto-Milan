# works on Mi Lan Pro VF Version 1.10, sha1sum = 7c489c6291067561733b20d2237963d6d36406d8

from fontTools.ttLib import TTFont, newTable
from fontTools.varLib.varStore import VarStoreInstancer

from pprint import pprint

infile = "MiLanProVF.ttf"
outfile = "MiLanProVF-fix.ttf"

font = TTFont(infile)

# fix gvar.glyphCount

gvar_raw = bytearray(font.getTableData('gvar'))

glyphCount = len(font['hmtx'].metrics)

gvar_raw[12] = glyphCount // 256
gvar_raw[13] = glyphCount % 256

gvar_ = newTable('gvar')
gvar_.decompile(bytes(gvar_raw), font)

# fix phantom points in gvar

fvar_ = font['fvar']

hvar_ = font['HVAR']

for name, tvl in gvar_.variations.items():
	widthIdx = hvar_.table.AdvWidthMap.mapping[name]
	dWidth = hvar_.table.VarStore.VarData[0].Item[widthIdx]
	tvl[0].coordinates[-3] = (dWidth[0], 0)
	tvl[1].coordinates[-3] = (dWidth[1], 0)

font['gvar'] = gvar_

# fonttool varLib.mutator connot interpolate this GPOS table.

del font['GPOS']

font.save(outfile)
