import pandas as pd
from io import StringIO   # <-- dùng cái này thay vì pd.compat.StringIO

data = """perfume;brand;country;gender;rating_value;rating_count;year;mainaccord1;mainaccord2;mainaccord3;mainaccord4;mainaccord5;weighted_rating;top_1;top_2;top_3;middle_1;middle_2;middle_3;base_1;base_2;base_3;price_category;longevity_score;sillage_score;perfume_id
alien;mugler;France;women;4.0;29858;2005.0;white floral;amber;floral;None;None;3.999716909319473;jasmine sambac;None;None;cashmeran;None;None;amber;None;None;High-end;Moderate;High;P001
shalimar-eau-de-parfum;guerlain;France;women;4.0;16654;1990.0;citrus;amber;woody;vanilla;balsamic;3.999503800462821;citruses;bergamot;lemon;iris;patchouli;vetiver;vanilla;incense;leather;Average;Moderate;Moderate;P002
this-is-her;zadig-voltaire;France;women;4.0;7888;2016.0;vanilla;sweet;woody;balsamic;powdery;3.999008053352847;pink pepper;silkwood blossom;jasmine sambac;whipped cream;vanilla;chestnut;sandalwood;cashmere wood;None;Average;Strong;Moderate;P003
london;burberry;UK;women;4.0;7834;2006.0;white floral;citrus;fruity;floral;rose;3.9990019105639765;honeysuckle;tangerine;rose;jasmine;tiare flower;peony;musk;sandalwood;patchouli;Average;Strong;High;P004
individuel;montblanc;France;men;4.0;7462;2003.0;sweet;fruity;aromatic;warm spicy;woody;3.998957434130076;lavender;cinnamon;pineapple;orange blossom;violet;geranium;raspberry;vanilla;sandalwood;Average;Strong;Moderate;P005
deep-red;hugo-boss;Germany;women;4.0;7048;2001.0;citrus;fruity;woody;vanilla;powdery;3.998903032533133;blood orange;black currant;clementine;ginger;ginger flower;tuberose;vanilla;sandalwood;musk;Average;Moderate;Moderate;P006
burberry-women;burberry;UK;women;4.0;6923;1995.0;fruity;powdery;woody;vanilla;sweet;3.998885473187076;peach;apricot;pear;sandalwood;jasmine;moss;vanilla;cedar;musk;Average;Strong;High;P007
florabotanica;balenciaga;Spain;women;4.0;6373;2012.0;aromatic;green;rose;floral;cannabis;3.998801027706003;mint;None;None;rose;carnation;cannabis;vetiver;amber;None;Average;Very Strong;Soft;P008
lalique-le-parfum;lalique;France;women;4.0;5990;2005.0;vanilla;aromatic;powdery;sweet;fresh spicy;3.9987342437635074;west indian bay;pink pepper;bergamot;heliotrope;almond;jasmine;vanilla;tonka bean;sandalwood;Average;Moderate;High;P009
very-good-girl;carolina-herrera;USA;women;4.0;5085;2021.0;fruity;rose;fresh;vanilla;tropical;3.9985423982779897;litchi;red currant;None;rose;None;None;vanilla;vetiver;None;Average;Moderate;High;P010
belle-d-opium;yves-saint-laurent;France;women;4.0;5078;2010.0;white floral;fruity;amber;warm spicy;woody;3.998540687477847;casablanca lily;gardenia;jasmine;incense;fruity notes;white pepper;sandalwood;patchouli;amber;Average;Moderate;Heavy;P011
touch-for-men;burberry;UK;men;4.0;4274;2000.0;fresh spicy;ozonic;musky;aquatic;woody;3.9983133062243947;violet leaf;artemisia;mandarin orange;white pepper;cedar;nutmeg;white musk;tonka bean;vetiver;Average;Light;High;P012
moonlight-in-heaven;by-kilian;France;unisex;4.0;3649;2016.0;sweet;citrus;tropical;aromatic;coconut;3.9980808511836554;grapefruit;lemon;pink pepper;mango;coconut;rice;vetiver;tonka bean;None;High-end;Moderate;High;P013
white-musk;the-body-shop;UK;women;4.0;3508;1981.0;musky;powdery;white floral;iris;earthy;3.9980192672093486;musk;lily;ylang-ylang;musk;lily;jasmine;musk;iris;jasmine;Affordable;Strong;High;P014
quorum;antonio-puig;Spain;men;4.0;2730;1981.0;woody;aromatic;mossy;earthy;tobacco;3.997593102908705;artemisia;caraway;lemon;pine tree;sandalwood;patchouli;oakmoss;tobacco;leather;Average;Very Strong;High;P015
dear-polly;vilhelm-parfumerie;USA;unisex;4.0;2513;2015.0;green;citrus;fresh;fresh spicy;amber;3.997439441046742;bergamot;apple;None;black tea;None;None;black amber;musk;oakmoss;Average;Very Strong;Moderate;P016
bvlgari-man;bvlgari;Italy;men;4.0;2319;2010.0;woody;ozonic;amber;aquatic;aromatic;3.9972844493347512;violet leaf;lotus;bergamot;vetyver;woodsy notes;cashmere wood;white honey;musk;benzoin;Average;Strong;High;P017
teint-de-neige;lorenzo-villoresi;Italy;unisex;4.0;2261;2000.0;powdery;vanilla;sweet;floral;musky;3.9972344010542984;powdery notes;rose;ylang-ylang;rose;tonka bean;floral notes;heliotrope;musk;rose;Average;Strong;Moderate;P018
boss-in-motion;hugo-boss;Germany;men;4.0;2200;2002.0;citrus;fresh spicy;warm spicy;woody;aromatic;3.99717973432206;orange;bergamot;violet leaf;pink pepper;cinnamon;nutmeg;musk;sandalwood;woodsy notes;Average;Strong;High;P019
bee;zoologist-perfumes;Canada;unisex;4.0;2186;2019.0;vanilla;beeswax;honey;powdery;amber;3.9971668815487877;beeswax;ginger;orange;mimosa;broom;heliotrope;vanilla;benzoin;tonka bean;Average;Strong;High;P020
idole-l-intense;lancome;France;women;4.0;2108;2020.0;woody;rose;musky;citrus;floral;3.997093072851662;bitter orange;mandarin orange;None;turkish rose;grasse rose;musk;cashmere wood;patchouli;madagascar vanilla;Average;Moderate;Heavy;P021
ange-ou-demon-le-secret-eau-de-toilette;givenchy;France;women;4.0;1812;2013.0;sweet;fruity;fresh;green;white floral;3.996774151266819;candy apple;sugar;None;tea;jasmine;rose;patchouli;musk;None;Average;Light;Moderate;P022
1881-men;cerruti;Italy;men;4.0;1796;1990.0;woody;aromatic;fresh spicy;earthy;green;3.9967549068299317;juniper;cypress;lavender;vetiver;ylang-ylang;rose;oakmoss;pine tree;cedar;Average;Strong;Moderate;P023
aqua-allegoria-bergamote-calabria;guerlain;France;unisex;4.0;1761;2017.0;citrus;warm spicy;aromatic;fresh spicy;woody;3.996711998533388;calabrian bergamot;petitgrain;None;ginger;cardamom;None;white musk;woody notes;None;Average;Strong;Moderate;P024
aura-mugler-eau-de-parfum-sensuelle;mugler;France;women;4.0;1704;2019.0;green;white floral;warm spicy;musky;powdery;3.9966396371111497;gardenia;cinnamon leaf;None;green notes;None;None;white musk;sandalwood;None;High-end;Strong;Moderate;P025
lacoste-pour-homme;lacoste-fragrances;France;men;4.0;1673;2002.0;fruity;warm spicy;woody;sweet;vanilla;3.9965989293153097;plum;apple;grapefruit;cinnamon;pink pepper;cardamom;vanilla;rum;musk;Average;Very Strong;Heavy;P026
climat-vintage;lancome;France;women;4.0;1668;1967.0;white floral;fresh;aldehydic;woody;powdery;3.9965922709936876;narcissus;lily-of-the-valley;violet;aldehydes;rosemary;tuberose;civet;musk;vetiver;Average;Moderate;Moderate;P027
l-eau-d-issey-pour-homme-sport;issey-miyake;Japan;men;4.0;1569;2012.0;citrus;fresh spicy;woody;aromatic;leather;3.996454851371844;grapefruit;bergamot;None;nutmeg;leather;None;vetiver;virginia cedar;ambergris;Average;Moderate;High;P028
kenneth-cole-black-for-men;kenneth-cole;USA;men;4.0;1473;2003.0;green;fresh spicy;citrus;aromatic;warm spicy;3.9963105808045265;mandarin orange;water mint;ginger;lotus;incense;cedar;musk;violet leaf;suede;Average;Strong;Heavy;P029
geranium-pour-monsieur;frederic-malle;France;men;4.0;1412;2009.0;aromatic;fresh spicy;green;warm spicy;rose;3.9962126458302336;mint;geranium;star anise;clove;cinnamon;None;musk;sandalwood;incense;High-end;Moderate;High;P030
silky-woods;goldfield-banks-australia;Australia;unisex;4.0;1299;2021.0;vanilla;powdery;warm spicy;leather;musky;3.996016778085985;ceylon cinnamon;saffron;None;suede;agarwood (oud);madagascar ylang-ylang;tahitian vanilla;australian sandalwood;tobacco leaf;Average;Moderate;High;P031
far-away-rebel;avon;USA;women;4.0;1245;2018.0;sweet;fruity;vanilla;chocolate;lactonic;3.9959158423828613;whipped cream;black currant;red fruits;orange blossom;madagascar vanilla;jasmine sambac;chocolate;caramel;salt;Affordable;Very Strong;Heavy;P032
invictus-intense;paco-rabanne;Spain;men;4.0;1241;2016.0;amber;fresh spicy;whiskey;animalic;white floral;3.9959081617855556;orange blossom;black pepper;None;whiskey;laurels;None;amber;ambergris;salt;Average;Moderate;High;P033
my-land;trussardi;Italy;men;4.0;1223;2012.0;citrus;leather;woody;aromatic;lavender;3.995873238557552;green mandarin;bergamot;None;lavender;violet;calone;leather;cashmere wood;tonka bean;Average;Strong;Soft;P034
island-kiss;escada;Germany;women;4.0;1169;2004.0;fruity;sweet;tropical;floral;None;3.9957647981108892;mango;passionfruit;raspberry;white peach;red berries;hibiscus;musk;sandalwood;white woods;Average;Moderate;Moderate;P035
fiore-d-ulivo;xerjoff;Italy;women;4.0;1143;2009.0;floral;citrus;aromatic;fresh spicy;musky;3.9957105274114726;amalfi lemon;lotus;basil;olive blossom;magnolia;jasmine;musk;benzoin;amber;High-end;Light;High;P036
accento;xerjoff;Italy;unisex;4.0;1087;2019.0;musky;powdery;sweet;earthy;fruity;3.995588778569629;pineapple;hyacinth;None;iris;jasmine;pink pepper;musk;vetiver;amber;High-end;Moderate;Soft;P037
mon-paris-intensement;yves-saint-laurent;France;women;4.0;1077;2020.0;fruity;rose;floral;sweet;vanilla;3.995566306733509;raspberry;black currant;pear;may rose;bulgarian rose;peony;vanilla;patchouli;white musk;Average;Light;High;P038
l-homme-sport;lanvin;France;men;4.0;1048;2009.0;aromatic;citrus;fresh spicy;herbal;lavender;3.9954998242595026;amalfi lemon;bergamot;pepper;sage;lavender;None;oakmoss;indonesian patchouli leaf;musk;Average;Light;High;P039
viva-la-juicy-rose;juicy-couture;USA;women;4.0;1011;2015.0;rose;floral;fresh;fruity;citrus;3.9954120506683592;pear;mandarin orange;jasmine;rose;peony;jasmine sambac;ambroxan;orris;benzoin;Average;Strong;Moderate;P040
scandal-a-paris;jean-paul-gaultier;France;women;4.0;996;2019.0;honey;sweet;fruity;white floral;floral;3.995375483590796;pear;None;None;jasmine;None;None;honey;None;None;Average;Strong;Moderate;P041
tubereuse-imperiale;bdk-parfums;France;unisex;4.0;980;2016.0;white floral;tuberose;woody;yellow floral;vanilla;3.9953358307169764;geranium;rosebay willowherb;None;indian tuberose;ylang-ylang;jasmine sambac;madagascar vanilla;benzoin;sandalwood;Average;Strong;Moderate;P042
essence-eau-de-musc;narciso-rodriguez;USA;women;4.0;970;2011.0;powdery;musky;iris;violet;rose;3.9953107004945463;iris;rose;None;musk;None;None;amber;None;None;Average;Moderate;Moderate;P043
l-aimant;coty;USA;women;4.0;961;1927.0;woody;aldehydic;powdery;sweet;rose;3.995287850632311;aldehydes;neroli;peach;ylang-ylang;rose;jasmine;musk;vanille;sandalwood;Average;Moderate;Moderate;P044
far-away-royale;avon;USA;women;4.0;954;2020.0;amber;vanilla;balsamic;sweet;white floral;3.9952699239771077;coriander extract;plum;bergamot;jasmine;orange blossom;tunisian neroli;madagascar vanilla;myrrh;peru balsam;Affordable;Strong;Heavy;P045
humor-5;natura;Brazil;women;4.0;942;2009.0;sweet;fruity;cherry;vanilla;powdery;3.995238873149824;cherry;raspberry;big strawberry;jasmine;heliotrope;lily-of-the-valley;vanilla;amber;sandalwood;Affordable;Strong;Moderate;P046
gardenia;zara;Spain;women;4.0;929;2021.0;vanilla;coffee;white floral;warm spicy;sweet;3.9952047714148087;orange blossom;None;None;coffee;None;None;vanilla;None;None;Affordable;Strong;High;P047
belle-de-nuit;fragonard;France;women;4.0;928;2001.0;rose;powdery;floral;fruity;violet;3.9952021279591388;gardenia;ylang-ylang;mirabilis;rose;violet;geranium;dried plum;musk;woody notes;Average;Moderate;High;P048
the-iceberg-fragrance;iceberg;Italy;women;4.0;909;2008.0;powdery;aromatic;sweet;fruity;woody;3.995151342684055;coriander;pear;bergamot;pistachio;almond;violet;suede;vanilla;patchouli;Average;Very Strong;High;P049
gentlemen-only-intense;givenchy;France;men;4.0;903;2014.0;amber;leather;smoky;woody;warm spicy;3.9951350811167567;birch leaf;black pepper;green mandarin;leather;patchouli;texas cedar;tonka bean;incense;amber;Average;Very Strong;Soft;P050
"""

# Đọc CSV từ string
df = pd.read_csv(StringIO(data), sep=";")

# Xuất ra file Excel
output_file = "perfume_dataset.xlsx"
df.to_excel(output_file, index=False)

print(f"Đã tạo file {output_file}")
