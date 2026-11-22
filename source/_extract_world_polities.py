# -*- coding: utf-8 -*-
"""V11 世界政区 40 相位提取（historical-basemaps GPL-3.0）。
覆盖中国时间轴 -500~1945 的 40 个权威年份，教材相关政权中文映射，
过滤原始族群/无名字小块，DP 简化 + 南极裁除 + 面积标注 → _world_polities.json。
输出结构：{years:[[year,key],...], e0..e39:[{n,cn,tint,a,paths},...]}
渲染端按当前相位年份取最近权威相，中国细节矩形仍由 clipPath 镂空。"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
WD = r'D:\WorkBuddyData\2026-11-20-17-31-34'
HB = os.path.join(WD, '_dl_hb')
OUT = os.path.join(WD, '_world_polities.json')

# 覆盖中国时间轴的 40 个权威年份（year → 文件名）
YEARS = [-500,-400,-323,-300,-200,-100,-1,100,200,300,400,500,600,700,800,900,1000,1100,1200,1279,
         1300,1400,1492,1500,1530,1600,1650,1700,1715,1783,1800,1815,1878,1880,1900,1914,1920,1930,1938,1945]

def fname(y):
    return 'world_bc%d' % (-y) if y < 0 else 'world_%d' % y

# 教材相关政权中文名 + 色系（高中纲要下/选必主线）
MAP = {
 # 古代西亚北非
 'Achaemenid Empire':('波斯帝国','#46628a'),'Persia':('波斯','#46628a'),'Persian Empire':('波斯帝国','#46628a'),
 'Sasanian Empire':('萨珊波斯','#46628a'),'Sassanid Empire':('萨珊波斯','#46628a'),'Parthia':('安息（帕提亚）','#5e8a50'),
 'Seleucid Kingdom':('塞琉古王国','#96793f'),'Empire of Alexander':('亚历山大帝国','#8f5c42'),
 'Egypt':('埃及','#8f8542'),'Ptolemaic Kingdom':('托勒密埃及','#8f8542'),'Meroe':('库施（麦罗埃）','#8f4a4a'),
 'Kush':('库施','#8f4a4a'),'Axum':('阿克苏姆','#8f4a4a'),'Ethiopia':('埃塞俄比亚','#8f4a4a'),
 'Carthaginian Empire':('迦太基','#8f5c42'),'Carthage':('迦太基','#8f5c42'),
 # 希腊罗马
 'Greek city-states':('希腊城邦','#43826a'),'Greece':('希腊','#43826a'),'Macedon and Hellenic League':('马其顿','#43826a'),
 'Rome':('罗马','#5e8a50'),'Roman Republic':('罗马共和国','#5e8a50'),'Roman Empire':('罗马帝国','#5e8a50'),
 'Western Roman Empire':('西罗马帝国','#8f5c42'),'Eastern Roman Empire':('东罗马帝国','#46628a'),
 'Byzantine Empire':('拜占庭帝国','#46628a'),'Ostrogoths':('东哥特','#8f5c42'),'Visigoths':('西哥特','#8f5c42'),
 'Visigothic Kingdom':('西哥特王国','#8f5c42'),'Franks':('法兰克王国','#5e8a50'),'Frankish Kingdom':('法兰克王国','#5e8a50'),
 'Holy Roman Empire':('神圣罗马帝国','#8f8542'),'Papal States':('教皇国','#a89468'),
 # 南亚
 'Magadha':('摩揭陀','#8f7a42'),'Mauryan Empire':('孔雀帝国','#8f7a42'),'Gupta Empire':('笈多帝国','#8f7a42'),
 'Hindu kingdoms':('印度诸国','#8f7a42'),'Hindu states':('印度诸国','#8f7a42'),
 'Sultanate of Delhi':('德里苏丹国','#8f4a4a'),'Delhi Sultanate':('德里苏丹国','#8f4a4a'),
 'Mughal Empire':('莫卧儿帝国','#5e8a50'),'Mughal':('莫卧儿帝国','#5e8a50'),'British Raj':('英属印度','#8f5c42'),
 # 伊斯兰世界
 'Abbasid Caliphate':('阿拔斯王朝','#46628a'),'Umayyad Caliphate':('倭马亚王朝','#46628a'),
 'Fatimid Caliphate':('法蒂玛王朝','#46628a'),'Emirate of Córdoba':('科尔多瓦埃米尔国','#8f8542'),
 'Ottoman Empire':('奥斯曼帝国','#46628a'),'Safavid Empire':('萨非王朝','#8f5c42'),'Safavid Persia':('萨非王朝','#8f5c42'),
 'Mamluke Sultanate':('马穆鲁克王朝','#8f8542'),'Islamic city-states':('伊斯兰城邦','#8f8542'),
 'Almohad Caliphate':('穆瓦希德王朝','#8f4a4a'),'Hafsid Caliphate':('哈夫斯王朝','#8f4a4a'),
 # 草原游牧帝国
 'Xiongnu':('匈奴','#8f7a42'),'Hunnic Empire':('匈人帝国','#8f7a42'),'Huns':('匈人','#8f7a42'),
 'Göktürks':('突厥','#8f7a42'),'Western Gokturk Khaganate':('西突厥','#8f7a42'),'Karluk':('葛逻禄','#8f7a42'),
 'Mongol Empire':('蒙古帝国','#8f5c42'),'Golden Horde':('金帐汗国','#8f7a42'),'Chagatai Khanate':('察合台汗国','#8f7a42'),
 'Ilkhanate':('伊儿汗国','#8f7a42'),'Timurid Emirates':('帖木儿帝国','#8f8542'),
 'Kara Khitai Khaganate':('西辽','#8f7a42'),'Oirat Confederation':('瓦剌','#8f7a42'),
 'central Asian khanates':('中亚诸汗国','#8f7a42'),'Crimean Khanate':('克里米亚汗国','#8f7a42'),
 # 东亚（中国由江山图层负责，这里仅保留域外可见的大政权名）
 'Ming Chinese Empire':('明朝','#9e2a2b'),'Qing Empire':('清朝','#9e2a2b'),'Chinese warlords':('民国军阀','#9e2a2b'),
 'Japan':('日本','#8f4a4a'),'Imperial Japan (Fujiwara)':('日本（藤原）','#8f4a4a'),'Empire of Japan':('日本帝国','#8f4a4a'),
 'Yamato':('大和','#8f4a4a'),'Korea':('朝鲜','#96793f'),'Goryeo':('高丽','#96793f'),'Koguryo':('高句丽','#96793f'),
 'Paekche':('百济','#96793f'),'Silla':('新罗','#96793f'),'Gojoseon':('古朝鲜','#96793f'),
 'Đại Việt':('越南','#43826a'),'Champa':('占城','#43826a'),'Champa City States':('占城','#43826a'),
 'Siam':('暹罗','#43826a'),'Ayutthaya':('阿瑜陀耶','#43826a'),'Rattanakosin Kingdom':('暹罗','#43826a'),
 'Khmer Empire':('高棉帝国','#43826a'),'Srivijaya Empire':('室利佛逝','#43826a'),'Majapahit':('满者伯夷','#43826a'),
 'Bagan':('蒲甘','#43826a'),'Malacca':('马六甲','#8f4a4a'),'Dutch East Indies':('荷属东印度','#96793f'),
 # 非洲
 'Empire of Ghana':('加纳帝国','#96793f'),'Ghana':('加纳','#96793f'),'Mali':('马里帝国','#96793f'),
 'Songhai':('桑海帝国','#96793f'),'Kanem-Bornu':('加涅姆-博尔努','#96793f'),'Great Zimbabwe':('大津巴布韦','#8f8542'),
 'Merina Kingdom':('梅里纳王国','#8f8542'),'Asante':('阿散蒂','#96793f'),'Segu':('塞古','#96793f'),
 # 美洲
 'Aztec Empire':('阿兹特克帝国','#43826a'),'Aztec':('阿兹特克','#43826a'),'Inca Empire':('印加帝国','#8f5c42'),
 'Inca':('印加','#8f5c42'),'Maya city-states':('玛雅城邦','#43826a'),'Maya states':('玛雅诸国','#43826a'),
 'Maya':('玛雅','#43826a'),'Huari Empire':('瓦里帝国','#8f7a42'),'Tiahuanaco Empire':('蒂亚瓦纳科','#5e8a50'),
 'Teotihuacan':('特奥蒂瓦坎','#8f8542'),'Olmec':('奥尔梅克','#8f8542'),
 # 欧洲近代
 'Spain':('西班牙','#8f4a4a'),'Spanish Empire':('西班牙帝国','#8f4a4a'),'Portugal':('葡萄牙','#96793f'),
 'Portuguese Empire':('葡萄牙帝国','#96793f'),'England':('英格兰','#a05f5f'),'England and Ireland':('英格兰','#a05f5f'),
 'United Kingdom':('英国','#8f5c42'),'Great Britain':('英国','#8f5c42'),'British Empire':('英国','#8f5c42'),
 'France':('法国','#5e8a50'),'Kingdom of France':('法兰西王国','#5e8a50'),'Russia':('俄罗斯','#8f9e8f'),
 'Russian Empire':('俄罗斯帝国','#8f9e8f'),'Tsardom of Russia':('沙皇俄国','#8f9e8f'),
 'Grand Duchy of Moscow':('莫斯科公国','#8f9e8f'),'USSR':('苏联','#8f5c42'),
 'Prussia':('普鲁士','#5f7aa3'),'Austrian Empire':('奥地利帝国','#96793f'),'Poland-Lithuania':('波兰立陶宛','#5f7aa3'),
 'Polish-Lithuanian Commonwealth':('波兰立陶宛联邦','#5f7aa3'),'Dutch Republic':('荷兰共和国','#96793f'),
 'Netherlands':('荷兰','#96793f'),'Sweden':('瑞典','#5f7aa3'),'Denmark':('丹麦','#5f7aa3'),
 'Denmark-Norway':('丹麦-挪威','#5f7aa3'),'Norway':('挪威','#5f7aa3'),'Venice':('威尼斯','#a89468'),
 'Genoa':('热那亚','#a89468'),'Swiss Confederation':('瑞士','#8f8542'),'Hungary':('匈牙利','#96793f'),
 'Calmar Union':('卡尔马联盟','#5f7aa3'),'Kalmar Union':('卡尔马联盟','#5f7aa3'),
 # 近现代
 'United States':('美国','#a05f5f'),'United States of America':('美国','#a05f5f'),'America':('美国','#a05f5f'),
 'Germany':('德国','#5f7aa3'),'Italy':('意大利','#8f4a4a'),'Kingdom of Italy':('意大利王国','#8f4a4a'),
 'Austria':('奥地利','#96793f'),'Poland':('波兰','#5f7aa3'),'Czechoslovakia':('捷克斯洛伐克','#5f7aa3'),
 'Yugoslavia':('南斯拉夫','#8f8542'),'Turkey':('土耳其','#8f5c42'),'Iran':('伊朗','#46628a'),
 'Egypt':('埃及','#8f8542'),'Saudi Arabia':('沙特阿拉伯','#8f8542'),'Mongolia':('蒙古','#8f7a42'),
 'Canada':('加拿大','#a05f5f'),'Australia':('澳大利亚','#8f8542'),'New Zealand':('新西兰','#8f8542'),
 'Mexico':('墨西哥','#5e8a50'),'Brazil':('巴西','#5e8a50'),'Argentina':('阿根廷','#96793f'),
 'Chile':('智利','#8f4a4a'),'Peru':('秘鲁','#8f8542'),'Colombia':('哥伦比亚','#5f7aa3'),
 'India':('印度','#8f7a42'),'Burma':('缅甸','#43826a'),'Ceylon':('锡兰','#43826a'),
 'Philippines':('菲律宾','#43826a'),'Indonesia':('印度尼西亚','#43826a'),'Malaysia':('马来西亚','#43826a'),
 'Republic of China':('中华民国','#9e2a2b'),'China':('中国','#9e2a2b'),
 # 补充：中国王朝（矩形镂空外仍可见部分）+ 高频缺映射
 'Han':('汉朝','#9e2a2b'),'Han Empire':('汉朝','#9e2a2b'),'Jin':('晋朝','#9e2a2b'),
 'Jin Empire':('晋朝','#9e2a2b'),'Toba Wei':('北魏','#9e2a2b'),'Sui Empire':('隋朝','#9e2a2b'),
 'Tang Empire':('唐朝','#9e2a2b'),'Song Empire':('宋朝','#9e2a2b'),'Ming Empire':('明朝','#9e2a2b'),
 'Manchu Empire':('清朝','#9e2a2b'),'Chinese Warlords':('民国军阀','#9e2a2b'),
 'Parthian Empire':('安息（帕提亚）','#5e8a50'),'Kushan Empire':('贵霜帝国','#8f7a42'),
 'Yuezhi':('大月氏','#8f7a42'),'Scythians':('斯基泰','#8f7a42'),'Ruanruan':('柔然','#8f7a42'),
 'Tibetan Empire':('吐蕃','#8f7a42'),'Tufan Empire':('吐蕃','#8f7a42'),'Tibet':('吐蕃','#8f7a42'),
 'Great Khanate':('蒙古帝国','#8f5c42'),'Mongols':('蒙古','#8f7a42'),'Mongol':('蒙古','#8f7a42'),
 'Khanate of the Golden Horde':('金帐汗国','#8f7a42'),'Tsardom of Muscovy':('沙皇俄国','#8f9e8f'),
 'Timurid Empire':('帖木儿帝国','#8f8542'),'Quazaq Khanate':('哈萨克汗国','#8f7a42'),
 'Nogai Horde':('诺盖汗国','#8f7a42'),'Oghuz Turks':('乌古斯突厥','#8f7a42'),
 'Kimek-Kipchak khaganate':('钦察汗国','#8f7a42'),'Cuman-Kipchak confederation':('库曼-钦察','#8f7a42'),
 'Kingdom of Brazil':('巴西','#5e8a50'),'Viceroyalty of Brazil':('巴西（葡属）','#5e8a50'),
 'Viceroyalty of New Spain':('新西班牙（墨西哥）','#8f4a4a'),'Viceroyalty of Peru':('秘鲁总督区','#8f8542'),
 'Viceroyalty of New Granada':('新格拉纳达','#5f7aa3'),'Viceroyalty of the Río de la Plata':('拉普拉塔总督区','#96793f'),
 'White Russia':('白俄罗斯','#5f7aa3'),'French West Africa':('法属西非','#96793f'),
 'Luisiana':('路易斯安那','#5e8a50'),'Greenland':('格陵兰','#5f7aa3'),'New South Wales':('新南威尔士','#8f8542'),
 'Saka Kingdom':('塞种','#8f7a42'),'Scythia':('斯基泰','#8f7a42'),
}
# 近现代国家/地区中文映射（V14.2：消除e38/e39中英混排，教材常见+主要国家全覆盖）
MAP.update({
 'Afghanistan':('阿富汗','#8f7a42'),'Albania':('阿尔巴尼亚','#5f7aa3'),'Algeria':('阿尔及利亚','#96793f'),
 'Algeria (France)':('法属阿尔及利亚','#96793f'),'Angola (Portugal)':('葡属安哥拉','#8f8542'),
 'Armenia':('亚美尼亚','#8f5c42'),'Belgium':('比利时','#5f7aa3'),'Belgian Congo':('比属刚果','#96793f'),
 'Bhutan':('不丹','#43826a'),'Bolivia':('玻利维亚','#5e8a50'),'Botswana':('博茨瓦纳','#8f8542'),
 'British Somaliland':('英属索马里兰','#8f5c42'),'Bulgaria':('保加利亚','#5f7aa3'),'Burundi':('布隆迪','#96793f'),
 'Cambodia':('柬埔寨','#43826a'),'Cochin China':('交趾支那','#8f4a4a'),'Congo (France)':('法属刚果','#96793f'),
 'Costa Rica':('哥斯达黎加','#5e8a50'),'Cuba':('古巴','#8f4a4a'),'Dominican Republic':('多米尼加','#5f7aa3'),
 'Dominion of Newfoundland':('纽芬兰自治领','#a05f5f'),'Ecuador':('厄瓜多尔','#5f7aa3'),
 'Eritrea (Italy)':('意属厄立特里亚','#8f8542'),'Estonia':('爱沙尼亚','#5f7aa3'),
 'Ethiopia (Italy)':('意属埃塞俄比亚','#8f4a4a'),'Finland':('芬兰','#5f7aa3'),
 'French Cameroons':('法属喀麦隆','#96793f'),'French Equatorial Africa':('法属赤道非洲','#96793f'),
 'French Guiana':('法属圭亚那','#96793f'),'French Indo-China':('法属印度支那','#5e8a50'),
 'Gold Coast':('黄金海岸','#96793f'),'Guatemala':('危地马拉','#5e8a50'),'Guyana':('圭亚那','#5f7aa3'),
 'Honduras':('洪都拉斯','#5e8a50'),'Ireland':('爱尔兰','#5e8a50'),'Israel':('以色列','#46628a'),
 'Italian Somaliland':('意属索马里兰','#8f8542'),'Kenya':('肯尼亚','#8f8542'),'Laos':('老挝','#43826a'),
 'Latvia':('拉脱维亚','#5f7aa3'),'Liberia':('利比里亚','#5f7aa3'),'Libya':('利比亚','#8f8542'),
 'Lithuania':('立陶宛','#5f7aa3'),'Madagascar (France)':('法属马达加斯加','#96793f'),
 'Malawi':('马拉维','#8f8542'),'Mandatory Palestine (GB)':('巴勒斯坦（英委任）','#8f8542'),
 'Mesopotamia (GB)':('美索不达米亚（英委任）','#8f5c42'),'Morocco (France)':('法属摩洛哥','#96793f'),
 'Mozambique (Portugal)':('葡属莫桑比克','#8f8542'),'Muscat and Oman':('阿曼','#8f8542'),
 'Nepal':('尼泊尔','#43826a'),'Nicaragua':('尼加拉瓜','#5e8a50'),'Nigeria':('尼日利亚','#96793f'),
 'Northern Rhodesia':('北罗得西亚','#8f8542'),'Panama':('巴拿马','#5e8a50'),'Paraguay':('巴拉圭','#96793f'),
 'Romania':('罗马尼亚','#5f7aa3'),'Sierra Leone':('塞拉利昂','#8f8542'),'Southern Rhodesia':('南罗得西亚','#8f8542'),
 'Spanish Sahara':('西属撒哈拉','#8f8542'),'Sudan':('苏丹','#8f8542'),'Suriname':('苏里南','#5f7aa3'),
 'Switzerland':('瑞士','#8f8542'),'Syria (France)':('法属叙利亚','#96793f'),'Tunisia':('突尼斯','#8f8542'),
 'Uganda':('乌干达','#8f8542'),'Union of South Africa':('南非联邦','#a05f5f'),'Uruguay':('乌拉圭','#96793f'),
 'Venezuela':('委内瑞拉','#5f7aa3'),'Xinjiang':('新疆','#9e2a2b'),'Yemen':('也门','#8f8542'),
 'Yemen (UK)':('英属也门','#8f8542'),'Tanzania, United Republic of':('坦桑尼亚','#8f8542'),
 'Rio De Oro':('西撒哈拉','#8f8542'),'Hejaz':('汉志','#8f8542'),"Emirate of Bin Shal'an":('阿布扎比','#8f8542'),
 'Trucial Oman':('特鲁西尔阿曼','#8f8542'),'Congo':('刚果','#96793f'),
 # 1945相
 'Algeria':('阿尔及利亚','#96793f'),'Annam':('安南','#43826a'),'Bangladesh':('孟加拉国','#8f7a42'),
 'Benin':('贝宁','#8f8542'),'Burkina Faso':('布基纳法索','#8f8542'),'Cameroon':('喀麦隆','#96793f'),
 'Chad':('乍得','#8f8542'),'Cyraneica (UK Lybia)':('昔兰尼加','#8f8542'),
 'Fezzan (Frech Lybia)':('费赞','#8f8542'),'Gabon':('加蓬','#8f8542'),'Germany (Soviet)':('德国（苏占）','#5f7aa3'),
 'Germany (UK)':('德国（英占）','#5f7aa3'),'Germany (USA)':('德国（美占）','#5f7aa3'),
 'Guinea':('几内亚','#8f8542'),'Iceland':('冰岛','#5f7aa3'),'Iraq':('伊拉克','#8f5c42'),
 'Ivory Coast':('象牙海岸','#96793f'),'Japan (USA)':('日本（美占）','#8f4a4a'),
 'Jordan':('约旦','#8f8542'),'Korea (USA)':('韩国（美占）','#96793f'),'Korea (USSR)':('朝鲜（苏占）','#8f5c42'),
 'Manchuria':('中国东北','#9e2a2b'),'Manchukuo':('伪满洲国','#8f5c42'),'Mauritania':('毛里塔尼亚','#8f8542'),
 'Morocco':('摩洛哥','#96793f'),'Namibia':('纳米比亚','#8f8542'),'Niger':('尼日尔','#8f8542'),
 'Pakistan':('巴基斯坦','#8f7a42'),'Papua New Guinea':('巴布亚新几内亚','#43826a'),
 'Rhodesia':('罗得西亚','#8f8542'),'Senegal':('塞内加尔','#96793f'),'Somalia':('索马里','#8f8542'),
 'South Africa':('南非','#a05f5f'),'Syria':('叙利亚','#8f5c42'),'Thailand':('泰国','#43826a'),
 'Tonkin':('东京（越北）','#43826a'),'Tripolitana (UK Lybia)':('的黎波里塔尼亚','#8f8542'),
 'United Arab Emirates':('阿联酋','#8f8542'),'Western Sahara':('西撒哈拉','#8f8542'),'Zaire':('扎伊尔','#8f8542'),
 'Dutch Guinea':('荷属几内亚','#96793f'),'Eritrea':('厄立特里亚','#8f8542'),
 'Oman (British Raj)':('阿曼（英属印度）','#8f8542'),'Oman':('阿曼','#8f8542'),
 'Hail':('哈伊勒','#8f8542'),'Togo':('多哥','#8f8542'),'Nyasaland':('尼亚萨兰','#8f8542'),
})
# V14.6 世界史内容扩充：中古～近代教材相关政权中文名（填补大量英文名空白，提升中外对照可读性）
# 配色分组：伊斯兰世界褐金 / 基督教欧洲蓝灰 / 草原游牧红褐 / 印度金 / 东南亚绿 / 非洲红 / 美洲绿
MAP.update({
 # —— 古典晚期/魏晋南北朝（e8~e11）
 'Sixteen Kingdoms':('十六国','#8f5c42'),'Northern Liang':('北凉','#8f5c42'),
 'Satavahanihara':('百乘王朝','#96793f'),'Himyarite Kingdom':('希木叶尔','#8f7a42'),
 'Caucasian Alans':('高加索阿兰人','#8f5c42'),'Suren Kingdom':('贵霜（苏伦）','#96793f'),
 'Yueban':('悦般','#8f5c42'),'Simhala':('僧伽罗','#43826a'),'Geats':('耶阿特人','#5f7aa3'),
 'Swedes':('瑞典人','#5f7aa3'),'Moche':('莫切文化','#5e8a50'),
 # —— 隋唐/戒日帝国（e12~e14）
 'Kanauj':('曲女城（戒日帝国）','#96793f'),'Chalukyas':('遮娄其王朝','#96793f'),
 'Avars':('阿瓦尔人','#8f5c42'),'Sasanian dependencies':('萨珊属地','#8f7a42'),
 'Thai Kingdoms':('泰人诸国','#43826a'),'Pallavas':('帕拉瓦王朝','#96793f'),
 'Lombard principalities':('伦巴第诸公国','#5f7aa3'),'Kamarupa':('迦摩缕波','#96793f'),
 'Chen-La':('真腊','#43826a'),'Neustria':('纽斯特里亚','#5f7aa3'),'Khazars':('可萨','#8f5c42'),
 'Dvaravati':('堕罗钵底','#43826a'),'Funan':('扶南','#43826a'),'Makkura':('马库里亚','#8f4a4a'),
 'Alwa':('阿勒瓦','#8f4a4a'),'Nobatia':('诺巴提亚','#8f4a4a'),'Chauhans':('乔汉王朝','#96793f'),
 'Vazimba':('瓦津巴','#8f4a4a'),'minor states under Indian influence':('印度影响诸小国','#96793f'),
 # —— 宋辽金/中古盛期（e15~e18）
 'Uyghurs':('回鹘','#8f5c42'),'Berbers':('柏柏尔人','#8f7a42'),'Bedouins':('贝都因人','#8f7a42'),
 'Samanid Empire':('萨曼王朝','#8f7a42'),'Saffarids':('萨法尔王朝','#8f7a42'),
 'Khitans':('契丹','#8f5c42'),'Kyivan Rus':('基辅罗斯','#5f7aa3'),'Karluks':('葛逻禄','#8f5c42'),
 'Malay':('马来','#43826a'),'Aghlabid Emirate':('阿格拉布王朝','#8f7a42'),
 'East Francia':('东法兰克','#5f7aa3'),'Idrisid Caliphate':('伊德里斯王朝','#8f7a42'),
 'Rashtrakuta':('罗湿陀罗拘陀','#96793f'),'Sami':('萨米人','#5f7aa3'),'Mandes':('曼德人','#8f4a4a'),
 'Anasazi':('阿纳萨齐','#5e8a50'),'Azandes':('阿赞德人','#8f4a4a'),'Cushites':('库希特人','#8f4a4a'),
 'Malagasy':('马尔加什','#8f4a4a'),'Mogollon':('莫戈永文化','#5e8a50'),
 'Cuman Khanates':('库曼汗国','#8f5c42'),'Buwayhid Emirates':('白益王朝','#8f7a42'),
 'Rajput kingdoms':('拉其普特诸国','#96793f'),'Ghaznavid Emirate':('伽色尼王朝','#8f7a42'),
 'Liao':('辽','#8f5c42'),'Xixia':('西夏','#8f5c42'),'Other Rus Principalities':('罗斯诸公国','#5f7aa3'),
 'Principality of Novgorod':('诺夫哥罗德公国','#5f7aa3'),
 'Principality of Vladimir-Suzdal':('弗拉基米尔-苏兹达尔','#5f7aa3'),
 'Khwarazmian dynasty':('花剌子模','#8f7a42'),'Bulgar Khanate':('保加尔汗国','#8f5c42'),
 'Angevin Empire':('安茹帝国','#5f7aa3'),'Chola Empire':('朱罗帝国','#96793f'),
 'Principality of Galicia-Volhynia':('加利奇-沃伦','#5f7aa3'),'Ifat':('伊法特','#8f4a4a'),
 'Malays':('马来人','#43826a'),'Harapunchai':('哈利奔猜','#43826a'),
 # —— 元明/近代早期（e20~e25）
 'Ryazan':('梁赞','#5f7aa3'),'Novgorod':('诺夫哥罗德','#5f7aa3'),'Samis':('萨米人','#5f7aa3'),
 'Sukhothai':('素可泰','#43826a'),'Seljuk Caliphate':('塞尔柱','#8f7a42'),
 'Castile':('卡斯蒂利亚','#5f7aa3'),'English territory':('英属领地','#5f7aa3'),
 'Shogun Japan (Kamakura)':('镰仓幕府','#8f4a4a'),'Teutonic Knights':('条顿骑士团','#5f7aa3'),
 'Aragón':('阿拉贡','#5f7aa3'),'Kediri':('谏义里','#43826a'),'Aymara kingdoms':('艾马拉诸国','#5e8a50'),
 'minor Hindu kingdoms':('印度教诸小国','#96793f'),'Kashmir and Ladakh':('克什米尔与拉达克','#96793f'),
 'minor Hindu and Buddhist kingdoms':('印度教佛教诸小国','#96793f'),
})

# 原始族群/无明确政权 → 跳过（避免满屏无意义涂色）
SKIP_WORDS = ('hunter-gatherers','farmers','pastoralists','culture','cultures','tribes','peoples',
              'nomads','nomadic','hunters','fishers','shellfish','collectors','complex','focus',
              'chiefdoms','chiefdom','villages','settlement','settlements','archaeological',
              'culture group','language','confederation of tribes','statelets',
              # 原始族群/考古文化（无明确政权边界，教材不投影到政区）
              'khoisan','saami','sámi','samoy','tungus','athabaskan','athabascan','tuareg','touareg',
              'siberians','dorset','thule','inuit','paleo-','austronesians','melanesian','papuan',
              'maori','māori','tupis','guanches','ainu','ainus','bushmen','pygmy','lowland',
              'plateau fichers','west african cereal','savanna hunter','desert hunter',
              'north american pacific','eastern north american','subarctic forest','arctic marine',
              'andean hunter','amazon hunter','caribbean hunter','patagonian','pampas',
              'saharan pastoral','southern african','east african','central african',
              'polynesians','fiji','tonga','samoa','tuʻi tonga','shuar','algonquin','apache',
              'cherokee','cheyenne','comanche','crow','delaware','hopi','huron','iroquois','in nu',
              'innu','mi\'kma','navajo','nez perce','numic','pomo','calusa','natchez','muskogean')

def dp_simplify(pts, eps):
    if len(pts) < 3: return list(pts)
    closed = pts[0] == pts[-1]
    if closed: pts = pts[:-1]
    n = len(pts)
    if n < 3: return pts + ([pts[0]] if closed else [])
    keep = [False]*n; keep[0] = keep[n-1] = True
    stack = [(0,n-1)]
    while stack:
        i,j = stack.pop()
        if j <= i+1: continue
        ax,ay = pts[i]; bx,by = pts[j]
        dx,dy = bx-ax, by-ay; L=(dx*dx+dy*dy)**.5 or 1e-12
        dmax,idx = -1.0,-1
        for k in range(i+1,j):
            px,py = pts[k]
            d = abs(dx*(ay-py)-dy*(ax-px))/L
            if d>dmax: dmax,idx=d,k
        if dmax>eps: keep[idx]=True; stack.append((i,idx)); stack.append((idx,j))
    out=[p for p,f in zip(pts,keep) if f]
    if closed and out[0]!=out[-1]: out.append(out[0])
    return out

def ring_area(ring):
    a2=0.0
    for i in range(len(ring)-1):
        a2+=ring[i][0]*ring[i+1][1]-ring[i+1][0]*ring[i][1]
    return abs(a2)/2.0

# V14.6：边界精度提升 —— eps 0.25→0.08（约28km→9km），min_diag 0.12→0.07，
# 保留更多真实顶点，消除放大后"粗糙多边形/方块边界"。
def extract_rings(geom, eps=0.03, min_diag=0.05):
    rings=[]; g=geom.get('type'); c=geom.get('coordinates',[])
    if g=='Polygon': cand=[c[0]] if c else []
    elif g=='MultiPolygon': cand=[p[0] for p in c if p]
    else: cand=[]
    for r in cand:
        if not r: continue
        if min(p[1] for p in r)<-56: continue
        rs=dp_simplify(r,eps)
        if len(rs)<4: continue
        if ((max(p[0] for p in rs)-min(p[0] for p in rs))**2+
            (max(p[1] for p in rs)-min(p[1] for p in rs))**2)**.5<min_diag: continue
        # V14.6：坐标精度 1位(0.1°≈11km) → 2位(0.01°≈1.1km)，保留边界细节
        rings.append([[round(p[0],2),round(p[1],2)] for p in rs])
    return rings

def skip_name(n):
    nl=n.lower()
    return any(w in nl for w in SKIP_WORDS)

out={'years':[]}
for i,y in enumerate(YEARS):
    key='e%d'%i
    path=os.path.join(HB,fname(y)+'.geojson')
    g=json.load(open(path,encoding='utf-8'))
    got={}; total=0
    for ft in g.get('features',[]):
        en=str(ft['properties'].get('NAME') or '').strip()
        if not en or skip_name(en): continue
        rings=extract_rings(ft.get('geometry',{}))
        if not rings: continue
        a=sum(ring_area(r) for r in rings)
        cn_tint=MAP.get(en)
        # V14.6 内容优化：有中文名（教材相关）的政权看面积>=1.0；
        # 无中文名的多为澳洲原住民部落/美洲考古文化，对高中历史无价值，只保留面积>=4 的大政权
        # （避免它们占体积、添色块噪声）。宁可缺不可假：不做硬译。
        if cn_tint:
            if a<1.0: continue
        else:
            if a<4.0: continue
        if cn_tint: cn,tint=cn_tint
        else:
            cn=en; tint='#a99a72'   # 未映射政权：保留英文原名 + 中性色（地图上不显示标签）
        e=got.setdefault(cn,{'n':en,'cn':cn,'tint':tint,'paths':[],'a':0.0})
        e['paths'].extend(rings); e['a']+=a; total+=1
    # V14.6：排序改为「中文政权优先，其次面积」，保证 120 上限不会挤掉教材相关中文政权
    def _rank(x):
        has_cn = any('\u4e00' <= ch <= '\u9fff' for ch in x['cn'])
        return (1 if has_cn else 0, x['a'])
    lst=sorted(got.values(),key=_rank,reverse=True)
    # 数量硬上限：每相最多 120 政权
    if len(lst)>120: lst=lst[:120]
    for e in lst: e['a']=round(e['a'],1)
    out[key]=lst
    out['years'].append([y,key])
    print(key,y,fname(y),'→',len(lst),'政权, top:',[(x['cn'],round(x['a'])) for x in lst[:8]])

json.dump(out,open(OUT,'w',encoding='utf-8'),ensure_ascii=False)
print('WROTE',OUT,os.path.getsize(OUT)//1024,'KB','years',len(out['years']))
