import dataclasses


@dataclasses.dataclass(frozen=True)
class BaseName:
    n0 = "milk"
    n1 = "choco"


@dataclasses.dataclass(frozen=True)
class CharacterName:
    n0 = "BattleRoyle"
    n1 = "Assault"
    n2 = "Medic"
    n3 = "Bomber"
    n4 = "Recon"
    n5 = "Ghost"
    n6 = "Shield"
    n7 = "Launcher"
    n8 = "Invisible"
    n9 = "Hook"
    n10 = "Desperado"
    n11 = "Myocat"
    n12 = "Iron"
    n13 = "Carog"
    n14 = "Wheeleg"
    n15 = "Creamy"
    n16 = "Air"
    n17 = "Electric"
    n18 = "Blade"
    n19 = "Swiny"
    n20 = "Mago"


@dataclasses.dataclass(frozen=True)
class WeaponName:
    n1 = "AT-43"
    n2 = "SRG-17"
    n3 = "SB-18"
    n4 = "GG5"
    n5 = "UGG-01"
    n6 = "AP45"
    n7 = "RB15"
    n8 = "RS-11"
    n9 = "Foson"
    n10 = "R4K1"
    n11 = "BC901"
    n12 = "Bordeal"
    n13 = "BVM"
    n14 = "BB5-AIM"
    n15 = "BB7"
    n16 = "AGG-10"
    n17 = "EAG"
    n18 = "Gefield"
    n19 = "URRE"
    n20 = "Chris"
    n21 = "Collado"
    n22 = "RD10"
    n23 = "KDSG-11"
    n24 = "Spyra"
    n25 = "Cato"
    n26 = "Zigue"
    n27 = "Crossbow"
    n28 = "Commando"
    n29 = "R4K1-AIM"
    n30 = "RG44"
    n31 = "BF66"
    n32 = "SYL-724"
    n33 = "MACSMASH"
    n34 = "GP-01"


@dataclasses.dataclass(frozen=True)
class HeadName:
    n0 = "NOTHING"
    n1 = "MONOCULUS"
    n2 = "M.MOUSE"
    n3 = "NS-GLASSES"
    n4 = "DUMPLING"
    n5 = "S.N-FROG"
    n6 = "H.NAVY"
    n7 = "M.KITSUNE"
    n8 = "MICROSCOPE"
    n9 = "M.CHIKEN"
    n10 = "M.GAS"
    n11 = "H.NURSE"
    n12 = "MONOCLE"
    n13 = "P.CROWN"
    n14 = "C.D.CHEEK"
    n15 = "2nd H.BAND"
    n16 = "BAND"
    n17 = "A.MASK"
    n18 = "R.MASK"
    n19 = "R.ANGEL"
    n20 = "D.HORN"
    n21 = "R.MUFFS"
    n22 = "G.GOGGLE"
    n23 = "P.MASK"
    n24 = "K.MASK"
    n25 = "HALF MASK"
    n26 = "FLUSH"
    n27 = "BLACK-MK"
    n28 = "GALIEN"
    n29 = "CYCLOPS"
    n30 = "SP-GLASSES"
    n31 = "HEARTS"
    n32 = "C-HSET"
    n33 = "RED-RELLA"
    n34 = "BLACK-PATCH"
    n35 = "A.GLASSES"
    n36 = "SNOWCOOL"
    n37 = "BLUE-HSET"
    n38 = "PACIFER"
    n39 = "SPY"
    n40 = "JASON-B"
    n41 = "CAPTAIN-K"
    n42 = "SKY-ROCK"
    n43 = "ORA-GOGGLE"
    n44 = "PARIS-HIL"
    n45 = "SUPERSTAR"
    n46 = "BLACK"
    n47 = "DESERT"
    n48 = "MARINE.B"
    n49 = "KT-HSET"
    n50 = "ORANGE"
    n51 = "NOSE-COOL"
    n52 = "L-GLASSES"
    n53 = "C.BEARD"
    n54 = "M.WRESTLER"
    n55 = "SP.GOGGLE"
    n56 = "I.CROWN"
    n57 = "S.BEARD"
    n58 = "F-GHOST"
    n59 = "BAT-GLASSES"
    n60 = "H-PUMPKIN"
    n61 = "M.JOKER"
    n62 = "F.i.LOVE"
    n63 = "G.PIG"
    n64 = "C-TREE"
    n65 = "P.MUFFS"
    n66 = "H.SOLIDER"
    n67 = "M.RUDOLPH"
    n68 = "M-FRANK"
    n69 = "TALISMAN"
    n70 = "M-SKULL"
    n71 = "ANTLERS"
    n72 = "SANTAHAT"
    n73 = "SNOSE"
    n74 = "DRACULA"


@dataclasses.dataclass(frozen=True)
class BodyName:
    n0 = "NOTHING"
    n1 = "BALDUR"
    n2 = "S.HEART"
    n3 = "C.DUFFLE"
    n4 = "HOODIE"
    n5 = "N.S.SUIT"
    n6 = "U.BASKET"
    n7 = "U.MILITARY"
    n8 = "J.RIDER"
    n9 = "QIPAO"
    n10 = "S.HAWAII"
    n11 = "COMMANDER"
    n12 = "N.CLOW"
    n13 = "JUMPSUIT"
    n14 = "EC.ARMOR"
    n15 = "F.SUIT"
    n16 = "S.NURSE"
    n17 = "PRINCE"
    n18 = "ALICE"
    n19 = "B.SUIT"
    n20 = "E.ROBE"
    n21 = "OLYMPUS"
    n22 = "D.CLOAK"
    n23 = "Y.TRAINING"
    n24 = "FFG"
    n25 = "M.COW(B)"
    n26 = "TIGER"
    n27 = "DRESS"
    n28 = "TUXEDO"
    n29 = "S.UNIFORM(W)"
    n30 = "S.UNIFORM(M)"
    n31 = "BABY DRESS"
    n32 = "BABY BEAR"
    n33 = "1st TOP"
    n34 = "BLUE-JAMA"
    n35 = "CH.BELT"
    n36 = "RB-CROWN"
    n37 = "POLICE"
    n38 = "CAR-T"
    n39 = "SAILOR-A"
    n40 = "ALADIN"
    n41 = "REDFLOWER"
    n42 = "HAWAIIAN"
    n43 = "RANCH"
    n44 = "LIFE-JACKET"
    n45 = "PENGUIN"
    n46 = "T-SKULL"
    n47 = "BOOM"
    n48 = "EMER-BAG"
    n49 = "C-GUEVARA"
    n50 = "BTJ"
    n51 = "p08"
    n52 = "GIGN"
    n53 = "DEVGRU"
    n54 = "SAS"
    n55 = "SAHARA"
    n56 = "DOCTOR-H"
    n57 = "MUSTARD"
    n58 = "RED-INNER"
    n59 = "POPI-POPI"
    n60 = "R.MUFFLER"
    n61 = "APRON"
    n62 = "S.SURFING"
    n63 = "W.ROBE"
    n64 = "I.PRINCE"
    n65 = "HOODIE"
    n66 = "N.SANTA"
    n67 = "U.DOCTOR"
    n68 = "PIRATE"
    n69 = "ROYALROBE"
    n70 = "B.SANTA"
    n71 = "H.SOLDIER"
    n72 = "RUDOLPH"
    n73 = "B-FRANK"
    n74 = "KSW"
    n75 = "B-SKULL"
    n76 = "M.COW(W)"
    n77 = "TIGER(W)"
    n78 = "PINK"
    n79 = "PINK"
    n80 = "R.UNIFORM(W)"
    n81 = "R.UNIFORM(M)"
    n82 = "PINK-JAMA"
    n83 = "RAIND-BELL"
    n84 = "XMAS-ROBE"
    n85 = "SANTA"
    n86 = "SMAN-SCARF"
    n87 = "ROBE"


@dataclasses.dataclass(frozen=True)
class BackName:
    n0 = "NOTHING"
    n1 = "DANTALION"
    n2 = "C.BACKPACK"
    n3 = "B.MOUSE"
    n4 = "SS-BOARD"
    n5 = "HELI-FAN"
    n6 = "KENTAUROS"
    n7 = "W.MECHANIC"
    n8 = "T.UNICORN"
    n9 = "SCROLL"
    n10 = "RADIO"
    n11 = "SPANNER"
    n12 = "E.EGG(D）"
    n13 = "INJECTOR"
    n14 = "S.ROSE"
    n15 = "PAPE"
    n16 = "P.WATCH"
    n17 = "G.BOTTLE"
    n18 = "D.BLADE"
    n19 = "M.MOON"
    n20 = "M.SUN"
    n21 = "A.ARROW"
    n22 = "COFFIN"
    n23 = "CARROT"
    n24 = "SHARKBAG"
    n25 = "HOTDOG"
    n26 = "MULTI-BAG"
    n27 = "POPSICLE"
    n28 = "BURGER"
    n29 = "KENSTICK"
    n30 = "DONUT"
    n31 = "L-TUBE"
    n32 = "PINKY-BEAR"
    n33 = "DUCK-SHOES"
    n34 = "PARROT"
    n35 = "BABY-B"
    n36 = "SURFING"
    n37 = "DUCKTUBE"
    n38 = "SUPER-B"
    n39 = "CARIBBEAN"
    n40 = "WARRIOR"
    n41 = "OXYGEN"
    n42 = "FIREMAN"
    n43 = "M-BAG"
    n44 = "F-BAG"
    n45 = "W-TALKIE"
    n46 = "L-BAG"
    n47 = "S-BAG"
    n48 = "DEVIL-B"
    n49 = "ANGEL-W"
    n50 = "CUPID-WING"
    n51 = "LINE-BPRACK"
    n52 = "PO-STICK"
    n53 = "G.B.COOKIE"
    n54 = "MANDOLIN"
    n55 = "F.WING"
    n56 = "SHARK-SURF"
    n57 = "B.RUDOLPH"
    n58 = "W.CRYSTAL"
    n59 = "H.SCYTHE"
    n60 = "MOMO"
    n61 = "E.EGG(F)"
    n62 = "E.EGG(S)"
    n63 = "B.WING(G)"
    n64 = "B.SNOWMAN"
    n65 = "I-CRYSTAL"
    n66 = "S.SPRING"
    n67 = "W.WING(G)"
    n68 = "W-SKULL"
    n69 = "T-W-ICE"
    n70 = "SHIBABAG"
    n71 = "BOUQUET"
    n72 = "BEIGE-BAG"
    n73 = "HEART-BOX"
    n74 = "XMAS-BOX"
    n75 = "XMAS-TREE"
    n76 = "XMAS-BAG"
    n77 = "BURGER"
    n78 = "BROOMSTICK"
    n79 = "PUMPKIN"
