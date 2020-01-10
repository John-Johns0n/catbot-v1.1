import pandas as pd
import nltk as nl
from discord import Embed as emb
import math
import pickle
from collections import defaultdict
from PIL import Image


class Catunits:
    def __init__(self):
        # data = pd.read_csv(str('unitdata.tsv'), sep='\t')
        # headers = data.iloc[0]
        # print(headers)
        # self._cats  = pd.DataFrame(data.values[1:], columns=headers)
        self._cats = pd.read_csv('unitdata9.2.tsv', sep='\t')
        try:
            self._customnames = pickle.load(open('customNames.pkl', 'rb'))  # this is a dictionary
        except FileNotFoundError:
            self._customnames = {}
    def getrow(self, row):
        if row < 0:
            return None
        returned = None
        try:
            returned = self._cats.iloc[row]
        except IndexError:
            returned = None
        return returned

    def getcolumn(self, column):
        return None

    def getUnitCode(self, identifier, errors):
        locator = None
        try:  # was this a string or a int?
            locator = [int(identifier), 0]
        except ValueError:
            locator = self.closeEnough(identifier, errors)
        return locator

    def getstatsEmbed(self, cat, level, actualname, unitcode):
        title = 'Stats of ' + cat[93]
        if len(cat[-4]) > 1:
            title = 'Stats of ' + cat[95]
            if nl.edit_distance(actualname.lower(), cat[95].lower()) > 0:
                title += '; (nearest match)'
        catEmbed = emb(description=title, color=0xff3300)
        catEmbed.set_author(name='Cat Bot')
        catEmbed.add_field(name='Level', value=str(level), inline=True)
        lvmult = float(self.levelMultiplier(cat[94], unitcode, level))
        hpv = str(math.ceil(int(cat[0]) * lvmult)) + ' HP - ' + str(round(int(cat[1]), 0)) + ' KB'
        catEmbed.add_field(name='HP - Knockbacks', value=hpv, inline=True)
        dmg = str(math.ceil(int(cat[3]) * lvmult))
        if int(cat[59]) > 0:
            dmg += '/' + str(math.ceil(int(cat[59]) * lvmult))
        if int(cat[60]) > 0:
            dmg += '/' + str(math.ceil(int(cat[60]) * lvmult))
        dps = ' Damage - ' + str(int(float(cat[98].replace(',', '.')) * lvmult)) + ' DPS'
        damagekind = ''
        if cat[12] == 1:
            damagekind += 'area'
        else:
            damagekind += 'single'
        if cat[44] > 0:
            if cat[45] > 0:
                damagekind += ', long range'
            elif cat[45] < 0:
                damagekind += ', omnistrike'
        damagetype = 'Damage (' + damagekind + ') - DPS'
        catEmbed.add_field(name=damagetype, value=dmg+dps, inline=True)
        tba = str(round(int(cat[97])/30, 2))
        catEmbed.add_field(name='Speed - Attack Frequency', value=str(round(int(cat[2]) ,0)) + ' - ' + tba + 's', inline=True)
        catEmbed.add_field(name='Cost - Respawn', value=str(round(int(cat[6]*1.5), 0)) + ' - ' + str(round(max(((cat[7]*2-254)/30), 2), 2)) + 's', inline=True)
        rangestr = ''
        if ',' in damagekind:  # it's long range or omni
            rangestr += str(round(int(cat[44]), 0)) + ' to ' + str(round(int(cat[44]+cat[45]))) + '; stands at ' + str(round(int(cat[5])))
        else:  # otherwise only range is needed
            rangestr += str(round(int(cat[5])))
        catEmbed.add_field(name='Range', value=rangestr, inline=True)
        catEmbed.set_thumbnail(url=self.cattotriaitpics(cat))
        offensivestr = ''
        if cat[23] > 0:  # strong
            offensivestr += 'Strong, '
        if cat[24] > 0:  # knockback
            offensivestr += 'Knockback ' + str(round(int(cat[24]))) + '%, '
        if cat[25] > 0:  # freezes
            offensivestr += 'Freeze ' + str(round(int(cat[25]))) + '% (' + str(round(int(cat[26] / 30, 2))) + 's), '
        if cat[27] > 0:  # slow
            offensivestr += 'Slow ' + str(round(int(cat[27]))) + '% (' + str(round(int(cat[28] / 30, 2))) + 's), '
        if cat[30] > 0:  # massive damage
            offensivestr += 'Massive Damage, '
        if cat[31] > 0:  # critical
            offensivestr += 'Critical ' + str(round(int(cat[31]))) + '%, '
        if cat[32] > 0:  # targets only
            offensivestr += 'Targets only, '
        if cat[33] > 0:  # cash
            offensivestr += 'Double money, '
        if cat[34] > 0:  # base destroyer
            offensivestr += 'Base destroyer, '
        if cat[35] > 0:  # wave attack
            offensivestr += 'Wave attack ' + str(round(int(cat[35]))) + '% (level ' + str(round(int(cat[36]))) + '), '
        if cat[37] > 0:  # weaken
            offensivestr += 'Weaken ' + str(round(int(cat[37]))) + '% (' + str(round(int(cat[39]))) + '% power, ' + str(round(int(cat[38] / 30, 2))) + 's), '
        if cat[40] > 0:  # strengthen
            offensivestr += 'Strengthen ' + str(round(int(cat[51]))) + '% (at ' + str(round(int(cat[50]))) + '% hp), '
        if cat[52] > 0:  # zombie killer
            offensivestr += 'Zombie killer, '
        if cat[53] > 0:  # witch killer (collab)
            offensivestr += 'Witch killer, '
        if cat[70] > 0:  # barrier breaks
            offensivestr += 'Barrier breaks ' + str(round(int(cat[70]))) + '%, '
        if cat[71] > 0:  # warp, currently unused
            offensivestr += 'Warp ' + str(round(int(cat[71]))) + '% (' + str(round(int(cat[73]))) + '-' + str(round(int(cat[74]))) + ', ' + str(round(int(cat[72] / 30, 2))) + 's), '
        if cat[81] > 0:  # insane damage
            offensivestr += 'Insane damage, '
        if cat[82] > 0:  # savage blow
            offensivestr += 'Savage Blow ' + str(round(int(cat[82]))) + '% (' + str(round(int(cat[83]))) + '% extra power), '
        if cat[86] > 0:  # volcano attack
            offensivestr += 'Volcano Attack ' + str(round(int(cat[86]))) + '% (' + str(round(int(cat[88]/4))) + '-' + str(round(int(cat[87]/4))) + ', ' + str(round(int(cat[89]))) + 's), '
        offensivestr = offensivestr[:-2]
        if len(offensivestr) > 3:
            catEmbed.add_field(name='Offensive abilities', value=offensivestr, inline=True)
        defensivestr = ''
        if cat[29] > 0:  # strong
            defensivestr += 'Resistant, '
        if cat[42] > 0:  # survive
            offensivestr += 'Survive ' + str(round(int(cat[42]))) + '%, '
        if cat[43] > 0:  # metal
            defensivestr += 'Metal, '
        if cat[46] > 0:  # wave immune
            defensivestr += 'Wave immune, '
        if cat[47] > 0:  # wave block
            defensivestr += 'Wave block, '
        if cat[48] > 0:  # knockback immune
            defensivestr += 'Knockback immune, '
        if cat[49] > 0:  # freeze immune
            defensivestr += 'Freeze immune, '
        if cat[50] > 0:  # slow immune
            defensivestr += 'Slow immune, '
        if cat[51] > 0:  # weaken immune
            defensivestr += 'Weaken immune, '
        if cat[75] > 0:  # warp immune
            defensivestr += 'Warp immune, '
        if cat[79] > 0:  # curse immune
            defensivestr += 'Curse immune, '
        if cat[80] > 0:  # insane resist
            defensivestr += 'Insanely resists, '
        if cat[84] > 0:  # dodge
            defensivestr += 'Dodge ' + str(round(int(cat[84]))) + '% (' + str(round(int(cat[85] / 30, 2))) + 's), '
        defensivestr = defensivestr[:-2]
        if len(defensivestr) > 3:
            catEmbed.add_field(name='Defensive abilities', value=defensivestr, inline=True)
        return catEmbed

    def closeEnough(self, strToCmp, errors):
        names = self._cats.loc[:, 'enname'].to_list()
        names = [str(x).lower() for x in names]
        # edit distance of everything in the tsv
        dss = list(map(lambda x: nl.edit_distance(x, strToCmp), names))

        closest = [i for i, x in enumerate(dss) if x == min(dss)]

        # from dictionary
        distancedict = defaultdict(list)
        for i in self._customnames:
            distancedict[nl.edit_distance(strToCmp, i)].append(self._customnames[i])
        customnames = []
        try:
            customnames = min(distancedict.items())
        except ValueError:  # empty custom names
            customnames.append(errors+1)
        if min(dss) > errors and customnames[0] > errors:  # both were too bad
            return None
        if min(dss) < customnames[0]:  # normal names were better
            return [closest, min(dss)]  # all of the closest and the distance of the closests
        else:  # custom names were better
            return [customnames[1], customnames[0]]  # the best matches of all custom names

    def levelMultiplier(self, rarity, unitkind, level=0):
        if unitkind in range(91, 99):
            isCrazed = True  # this is a crazed/manic unit
        else:
            isCrazed = False
        if unitkind == 78:
            isBahamut = True  # this is awakened bahamut cat
        else:
            isBahamut = False
        if isBahamut:
            toret = float(min(30, level)*0.25)
            if level > 30:
                toret += float((level-30)*0.125)
            return 2+toret*2
        if isCrazed:
            toret = float(min(20, level) * 0.25)
            if level > 20:
                toret += float((level-20)*0.125)
            return 2+toret*2
        toret = float(min(60, level)*0.25)
        if rarity == 'R':
            if level > 60:
                toret += float(min(10, level-60)*0.25)
            if level > 70:
                toret += float(min(20, level-70)*0.125)
            if level > 90:
                toret += float((level-90)*0.0625)
        else:
            if level > 60:
                toret += float(min(20, level-60)*0.125)
            if rarity in ['U', 'S'] and level > 80:
                toret += float((level-80)*0.0625)
            if rarity not in ['U', 'S'] and level > 80:
                toret += float((level-80)*0.125)
        return 2+toret*2

    def cattotriaitpics(self, cat):  # for each trait, add '1' to the string if it has the trait, '0' otherwise
        fstr = ''
        if cat[10] != 0:  # antired
            fstr += '1'
        else:
            fstr += '0'
        if cat[16] != 0:  # antifloating
            fstr += '1'
        else:
            fstr += '0'
        if cat[17] != 0:  # antiblack
            fstr += '1'
        else:
            fstr += '0'
        if cat[18] != 0:  # antimetal
            fstr += '1'
        else:
            fstr += '0'
        if cat[19] != 0:  # antiwhite
            fstr += '1'
        else:
            fstr += '0'
        if cat[20] != 0:  # antiangel
            fstr += '1'
        else:
            fstr += '0'
        if cat[21] != 0:  # antialien
            fstr += '1'
        else:
            fstr += '0'
        if cat[22] != 0:  # antizombie
            fstr += '1'
        else:
            fstr += '0'
        if cat[78] != 0:  # antirelic
            fstr += '1'
        else:
            fstr += '0'
        return 'https://raw.githubusercontent.com/ElMustacho/catbot-v1.1/master/traitpics/' + fstr + '.png'

    def givenewname(self, unitcode, newname):
        if newname in self._customnames:  # can't have a name refer to 2 different units
            return False
        self._customnames[newname] = unitcode
        self.storedict()
        return True

    def storedict(self):
        with open('customNames.pkl', 'wb') as f:
            pickle.dump(self._customnames, f, pickle.DEFAULT_PROTOCOL)
