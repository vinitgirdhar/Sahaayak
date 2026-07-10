#!/usr/bin/env python3
"""
Generate curated showcase SVG product art for the demo catalog.

These assets are local, deterministic, and product-matched, which avoids the
wrong/random photos currently shown in the UI.
"""

from pathlib import Path


OUTPUT_DIR = Path('my_app/static/uploads/showcase')
WIDTH = 1200
HEIGHT = 900


SHOWCASE_ART = {
    'organic_tomatoes.svg': ('Organic Tomatoes', 'Vegetables', 'tomato'),
    'fresh_spinach.svg': ('Fresh Spinach', 'Vegetables', 'spinach'),
    'premium_carrots.svg': ('Premium Carrots', 'Vegetables', 'carrot'),
    'red_onions.svg': ('Red Onions', 'Vegetables', 'onion'),
    'green_capsicum.svg': ('Green Capsicum', 'Vegetables', 'capsicum'),
    'fresh_broccoli.svg': ('Fresh Broccoli', 'Vegetables', 'broccoli'),
    'cauliflower.svg': ('Cauliflower', 'Vegetables', 'cauliflower'),
    'cucumber.svg': ('Cucumber', 'Vegetables', 'cucumber'),
    'basmati_rice.svg': ('Basmati Rice', 'Grains & Cereals', 'rice'),
    'turmeric_powder.svg': ('Turmeric Powder', 'Spices & Condiments', 'turmeric'),
    'cumin_seeds.svg': ('Cumin Seeds', 'Spices & Condiments', 'cumin'),
    'toor_dal.svg': ('Toor Dal', 'Dry Ingredients', 'dal'),
    'besan.svg': ('Besan (Gram Flour)', 'Dry Ingredients', 'flour'),
    'fresh_milk.svg': ('Fresh Milk (1L)', 'Dairy Products', 'milk'),
    'paneer.svg': ('Paneer (200g)', 'Dairy Products', 'paneer'),
    'white_bread.svg': ('White Bread', 'Bread & Bakery', 'bread'),
    'burger_buns.svg': ('Burger Buns (4pc)', 'Bread & Bakery', 'buns'),
    'instant_noodles.svg': ('Instant Noodles Pack', 'Ready-to-Eat', 'noodles'),
    'veg_momos.svg': ('Frozen Veg Momos (10pc)', 'Ready-to-Eat', 'momos'),
    'peanut_butter.svg': ('Peanut Butter', 'Spreads & Pantry', 'peanut_butter'),
    'tea.svg': ('Tea', 'Snacks & Beverages', 'tea'),
    'sunflower_oil.svg': ('Sunflower Oil', 'Oils & Condiments', 'sunflower_oil'),
    'mango_juice.svg': ('Mango Juice', 'Snacks & Beverages', 'mango_juice'),
    'disposable_plates.svg': ('Disposable Plates (50pc)', 'Other', 'plates'),
    'gulab_jamun_mix.svg': ('Gulab Jamun Mix', 'Other', 'gulab_jamun'),
    'eggs.svg': ('Eggs (12pc)', 'Other', 'eggs'),
}


PALETTES = {
    'Vegetables': ('#0B3B2E', '#0E6B52', '#27B26A', '#A7F3D0'),
    'Grains & Cereals': ('#3B2A1D', '#7C5A3C', '#D0A96B', '#F8E7B5'),
    'Dry Ingredients': ('#2F2417', '#6A4A2A', '#D6B779', '#F7E8BE'),
    'Spices & Condiments': ('#4A1D0A', '#A94410', '#F59E0B', '#FDE68A'),
    'Dairy Products': ('#12324A', '#1E5D85', '#93C5FD', '#E0F2FE'),
    'Bread & Bakery': ('#4A2D16', '#8B5E34', '#F59E0B', '#FEF3C7'),
    'Ready-to-Eat': ('#3B1F2F', '#7A3556', '#FB7185', '#FFE4E6'),
    'Spreads & Pantry': ('#2B1D3B', '#5A3C7C', '#C084FC', '#E9D5FF'),
    'Snacks & Beverages': ('#0F2942', '#245A8D', '#60A5FA', '#DBEAFE'),
    'Oils & Condiments': ('#2C2B12', '#6A6521', '#EAB308', '#FEF08A'),
    'Other': ('#2A2540', '#51437A', '#A78BFA', '#EDE9FE'),
}


def wrap_svg(title, category, palette, body):
    bg_a, bg_b, accent, light = palette
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">Illustrated showcase art for {title} in the {category} category.</desc>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_a}" />
      <stop offset="100%" stop-color="{bg_b}" />
    </linearGradient>
    <radialGradient id="glow" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="{light}" stop-opacity="0.55" />
      <stop offset="100%" stop-color="{light}" stop-opacity="0" />
    </radialGradient>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="20" stdDeviation="24" flood-color="#08131f" flood-opacity="0.28" />
    </filter>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg)" rx="48" />
  <circle cx="220" cy="180" r="220" fill="url(#glow)" />
  <circle cx="1030" cy="780" r="240" fill="{light}" opacity="0.08" />
  <circle cx="940" cy="160" r="120" fill="{accent}" opacity="0.12" />
  <rect x="56" y="58" width="270" height="54" rx="27" fill="#ffffff" opacity="0.11" />
  <text x="88" y="94" fill="#F8FAFC" font-family="Segoe UI, Arial, sans-serif" font-size="30" font-weight="700" letter-spacing="1.5">{category}</text>
  {body}
</svg>
'''


def tomato_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="760" rx="225" ry="42" fill="#08131f" opacity="0.18" />
    <circle cx="600" cy="455" r="170" fill="#EF4444" />
    <ellipse cx="540" cy="392" rx="68" ry="44" fill="#FCA5A5" opacity="0.42" />
    <path d="M600 250 C552 255 520 274 498 314 C552 302 574 322 600 354 C626 322 648 302 702 314 C680 274 648 255 600 250 Z" fill="#16A34A"/>
    <rect x="588" y="220" width="24" height="52" rx="10" fill="#14532D" />
  </g>
'''


def spinach_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="770" rx="240" ry="40" fill="#08131f" opacity="0.16" />
    <path d="M495 655 C470 545 485 425 560 322 C644 378 676 480 642 610 C612 676 540 694 495 655 Z" fill="#22C55E"/>
    <path d="M702 640 C744 536 736 420 676 310 C582 360 550 458 582 582 C612 656 678 690 702 640 Z" fill="#16A34A"/>
    <path d="M606 690 C634 575 628 432 594 286 C498 354 454 460 470 594 C500 676 564 720 606 690 Z" fill="#4ADE80"/>
    <path d="M610 690 C600 544 596 436 598 286" stroke="#14532D" stroke-width="14" stroke-linecap="round"/>
    <path d="M548 648 C556 542 568 442 584 342" stroke="#166534" stroke-width="10" stroke-linecap="round"/>
    <path d="M658 638 C648 542 636 448 622 352" stroke="#166534" stroke-width="10" stroke-linecap="round"/>
  </g>
'''


def carrot_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="778" rx="235" ry="36" fill="#08131f" opacity="0.16" />
    <g transform="rotate(-18 540 470)">
      <path d="M485 305 L608 354 L548 662 Q538 702 503 724 Q484 676 478 630 Z" fill="#F97316"/>
      <path d="M503 298 L468 244" stroke="#22C55E" stroke-width="22" stroke-linecap="round"/>
      <path d="M522 292 L514 214" stroke="#16A34A" stroke-width="18" stroke-linecap="round"/>
      <path d="M540 296 L574 238" stroke="#4ADE80" stroke-width="18" stroke-linecap="round"/>
      <path d="M506 394 L570 420" stroke="#FB923C" stroke-width="10" stroke-linecap="round"/>
      <path d="M494 470 L552 492" stroke="#FB923C" stroke-width="10" stroke-linecap="round"/>
      <path d="M486 548 L534 565" stroke="#FB923C" stroke-width="10" stroke-linecap="round"/>
    </g>
    <g transform="rotate(16 690 500)">
      <path d="M638 336 L752 390 L712 668 Q704 706 672 728 Q646 682 636 632 Z" fill="#EA580C"/>
      <path d="M652 332 L625 278" stroke="#4ADE80" stroke-width="20" stroke-linecap="round"/>
      <path d="M672 326 L676 248" stroke="#22C55E" stroke-width="16" stroke-linecap="round"/>
      <path d="M691 332 L728 278" stroke="#16A34A" stroke-width="16" stroke-linecap="round"/>
      <path d="M656 426 L716 454" stroke="#FB923C" stroke-width="10" stroke-linecap="round"/>
      <path d="M648 504 L702 529" stroke="#FB923C" stroke-width="10" stroke-linecap="round"/>
      <path d="M642 582 L690 602" stroke="#FB923C" stroke-width="10" stroke-linecap="round"/>
    </g>
  </g>
'''


def onion_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="780" rx="230" ry="38" fill="#08131f" opacity="0.18" />
    <path d="M600 274 C550 350 472 392 472 544 C472 664 548 726 600 726 C652 726 728 664 728 544 C728 392 650 350 600 274 Z" fill="#A855F7"/>
    <path d="M600 274 C576 352 556 418 556 544 C556 664 580 726 600 726" stroke="#E9D5FF" stroke-width="12" stroke-linecap="round"/>
    <path d="M600 274 C624 352 644 418 644 544 C644 664 620 726 600 726" stroke="#D8B4FE" stroke-width="12" stroke-linecap="round"/>
    <path d="M600 230 L560 150" stroke="#22C55E" stroke-width="18" stroke-linecap="round"/>
    <path d="M604 226 L610 126" stroke="#16A34A" stroke-width="15" stroke-linecap="round"/>
    <path d="M612 228 L666 162" stroke="#4ADE80" stroke-width="14" stroke-linecap="round"/>
  </g>
'''


def capsicum_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="780" rx="232" ry="40" fill="#08131f" opacity="0.18" />
    <path d="M520 348 C468 378 446 448 456 530 C466 632 532 712 600 712 C668 712 734 632 744 530 C754 448 732 378 680 348 C648 330 620 332 600 350 C580 332 552 330 520 348 Z" fill="#16A34A"/>
    <path d="M560 372 C534 398 526 460 532 538 C540 618 568 678 600 700" stroke="#4ADE80" stroke-width="12" stroke-linecap="round"/>
    <path d="M640 372 C666 398 674 460 668 538 C660 618 632 678 600 700" stroke="#22C55E" stroke-width="12" stroke-linecap="round"/>
    <path d="M596 270 C576 276 562 292 562 314 C578 314 594 320 606 330 C618 318 632 310 648 308 C646 286 628 270 596 270 Z" fill="#14532D"/>
    <rect x="592" y="236" width="20" height="54" rx="10" fill="#14532D" />
  </g>
'''


def broccoli_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="782" rx="240" ry="34" fill="#08131f" opacity="0.18" />
    <rect x="558" y="492" width="84" height="180" rx="28" fill="#65A30D"/>
    <circle cx="518" cy="430" r="74" fill="#16A34A"/>
    <circle cx="600" cy="392" r="98" fill="#15803D"/>
    <circle cx="690" cy="432" r="74" fill="#16A34A"/>
    <circle cx="572" cy="470" r="68" fill="#22C55E"/>
    <circle cx="646" cy="470" r="68" fill="#22C55E"/>
  </g>
'''


def cauliflower_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="782" rx="240" ry="34" fill="#08131f" opacity="0.18" />
    <path d="M520 612 C518 680 548 722 600 722 C652 722 682 680 680 612 Z" fill="#65A30D"/>
    <path d="M488 598 C446 560 432 516 444 474 C506 470 548 492 578 538 C558 572 530 592 488 598 Z" fill="#16A34A"/>
    <path d="M712 598 C754 560 768 516 756 474 C694 470 652 492 622 538 C642 572 670 592 712 598 Z" fill="#16A34A"/>
    <circle cx="524" cy="430" r="66" fill="#F8FAFC"/>
    <circle cx="600" cy="396" r="96" fill="#FFFBEB"/>
    <circle cx="680" cy="434" r="66" fill="#F8FAFC"/>
    <circle cx="564" cy="460" r="62" fill="#FEFCE8"/>
    <circle cx="636" cy="460" r="62" fill="#FEFCE8"/>
  </g>
'''


def cucumber_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="782" rx="260" ry="34" fill="#08131f" opacity="0.16" />
    <rect x="300" y="410" width="540" height="148" rx="74" fill="#15803D"/>
    <rect x="330" y="438" width="480" height="92" rx="46" fill="#22C55E" opacity="0.85"/>
    <circle cx="860" cy="496" r="86" fill="#A7F3D0"/>
    <circle cx="860" cy="496" r="62" fill="#DCFCE7"/>
    <circle cx="860" cy="496" r="34" fill="#BBF7D0"/>
    <circle cx="412" cy="470" r="10" fill="#86EFAC"/>
    <circle cx="472" cy="520" r="8" fill="#86EFAC"/>
    <circle cx="552" cy="466" r="9" fill="#86EFAC"/>
    <circle cx="632" cy="520" r="10" fill="#86EFAC"/>
    <circle cx="712" cy="468" r="8" fill="#86EFAC"/>
  </g>
'''


def rice_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="792" rx="240" ry="30" fill="#08131f" opacity="0.16" />
    <ellipse cx="600" cy="492" rx="146" ry="126" fill="#FFFBEB"/>
    <ellipse cx="600" cy="604" rx="198" ry="66" fill="#D1D5DB"/>
    <path d="M402 604 C430 690 500 742 600 742 C700 742 770 690 798 604 Z" fill="#94A3B8"/>
    <ellipse cx="600" cy="606" rx="170" ry="36" fill="#E2E8F0"/>
    <g fill="#F8F1D2">
      <ellipse cx="542" cy="450" rx="14" ry="6" transform="rotate(-18 542 450)" />
      <ellipse cx="602" cy="430" rx="14" ry="6" transform="rotate(12 602 430)" />
      <ellipse cx="654" cy="458" rx="14" ry="6" transform="rotate(-8 654 458)" />
      <ellipse cx="516" cy="510" rx="14" ry="6" transform="rotate(10 516 510)" />
      <ellipse cx="586" cy="500" rx="14" ry="6" transform="rotate(-12 586 500)" />
      <ellipse cx="652" cy="516" rx="14" ry="6" transform="rotate(18 652 516)" />
    </g>
  </g>
'''


def dal_art():
    lentils = [
        (514, 462), (560, 436), (612, 444), (664, 468), (704, 506),
        (536, 516), (584, 504), (634, 520), (682, 546), (560, 566),
        (612, 570), (662, 584), (516, 560), (708, 454),
    ]
    beans = '\n'.join(
        f'    <ellipse cx="{x}" cy="{y}" rx="20" ry="14" fill="#EAB308" transform="rotate(18 {x} {y})" />'
        for x, y in lentils
    )
    return f'''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="790" rx="246" ry="30" fill="#08131f" opacity="0.16" />
    <ellipse cx="600" cy="612" rx="214" ry="70" fill="#7C4A16"/>
    <ellipse cx="600" cy="574" rx="192" ry="54" fill="#A16207"/>
{beans}
  </g>
'''


def flour_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="792" rx="250" ry="30" fill="#08131f" opacity="0.16" />
    <path d="M470 296 H730 L692 694 C686 742 652 772 600 772 C548 772 514 742 508 694 Z" fill="#E5E7EB"/>
    <path d="M496 336 H704 L674 690 C670 722 646 744 600 744 C554 744 530 722 526 690 Z" fill="#F9FAFB"/>
    <path d="M508 344 H692 L676 460 C654 488 626 502 600 502 C574 502 546 488 524 460 Z" fill="#D1D5DB" opacity="0.55"/>
    <text x="600" y="624" text-anchor="middle" fill="#92400E" font-family="Segoe UI, Arial, sans-serif" font-size="72" font-weight="800">BESAN</text>
    <path d="M544 414 C574 372 626 372 656 414 C638 446 620 460 600 460 C580 460 562 446 544 414 Z" fill="#FDE68A"/>
  </g>
'''


def turmeric_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="790" rx="246" ry="30" fill="#08131f" opacity="0.16" />
    <ellipse cx="600" cy="610" rx="210" ry="66" fill="#7C2D12"/>
    <ellipse cx="600" cy="574" rx="190" ry="50" fill="#92400E"/>
    <path d="M450 574 C500 494 700 494 750 574 C700 626 500 626 450 574 Z" fill="#F59E0B"/>
    <path d="M770 402 L854 360 L898 472 L814 514 Z" fill="#D1A06B"/>
    <path d="M818 518 C792 560 754 584 700 590" stroke="#D1A06B" stroke-width="18" stroke-linecap="round"/>
  </g>
'''


def cumin_art():
    seed_positions = [
        (520, 476, -20), (566, 454, 18), (616, 468, -12), (660, 450, 22),
        (700, 476, -18), (538, 522, 14), (592, 508, -16), (640, 528, 18),
        (688, 510, -10), (564, 560, 22), (620, 552, -18), (676, 564, 16),
    ]
    seeds = '\n'.join(
        f'    <ellipse cx="{x}" cy="{y}" rx="16" ry="5" fill="#D4A373" transform="rotate({rot} {x} {y})" />'
        for x, y, rot in seed_positions
    )
    return f'''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="790" rx="246" ry="30" fill="#08131f" opacity="0.16" />
    <ellipse cx="600" cy="612" rx="214" ry="68" fill="#78350F"/>
    <ellipse cx="600" cy="574" rx="192" ry="52" fill="#92400E"/>
{seeds}
  </g>
'''


def peanut_butter_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="790" rx="220" ry="30" fill="#08131f" opacity="0.16" />
    <rect x="436" y="286" width="328" height="380" rx="54" fill="#E2E8F0"/>
    <rect x="470" y="206" width="260" height="92" rx="28" fill="#CBD5E1"/>
    <rect x="470" y="354" width="260" height="240" rx="26" fill="#B45309"/>
    <rect x="470" y="334" width="260" height="52" rx="14" fill="#F8FAFC"/>
    <ellipse cx="600" cy="472" rx="96" ry="66" fill="#D97706" opacity="0.52"/>
  </g>
'''


def milk_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="794" rx="238" ry="28" fill="#08131f" opacity="0.16" />
    <path d="M512 250 H678 L660 700 C656 744 626 772 596 772 C566 772 536 744 532 700 Z" fill="#F8FAFC"/>
    <path d="M546 174 H642 V250 H546 Z" fill="#DBEAFE"/>
    <rect x="556" y="132" width="76" height="52" rx="18" fill="#93C5FD"/>
    <path d="M540 360 H650 V690 C648 720 626 742 596 742 C566 742 544 720 542 690 Z" fill="#E0F2FE"/>
    <path d="M540 438 C584 418 624 418 650 438 V530 C620 548 576 548 540 530 Z" fill="#60A5FA" opacity="0.35"/>
    <text x="596" y="514" text-anchor="middle" fill="#1D4ED8" font-family="Segoe UI, Arial, sans-serif" font-size="64" font-weight="800">MILK</text>
  </g>
'''


def paneer_art():
    cubes = [
        (506, 398), (590, 376), (674, 406),
        (534, 482), (620, 462), (704, 492),
        (508, 570), (594, 550), (680, 580),
    ]
    blocks = '\n'.join(
        f'    <g transform="translate({x} {y})"><rect x="-34" y="-34" width="68" height="68" rx="14" fill="#FEF3C7"/><rect x="-24" y="-24" width="48" height="48" rx="10" fill="#FDE68A"/></g>'
        for x, y in cubes
    )
    return f'''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="792" rx="250" ry="30" fill="#08131f" opacity="0.16" />
    <rect x="414" y="304" width="372" height="362" rx="48" fill="#E2E8F0"/>
    <rect x="442" y="332" width="316" height="306" rx="40" fill="#F8FAFC"/>
{blocks}
  </g>
'''


def bread_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="794" rx="248" ry="28" fill="#08131f" opacity="0.16" />
    <path d="M438 420 C438 334 504 278 598 278 C692 278 758 334 758 420 V604 C758 666 708 714 646 714 H550 C488 714 438 666 438 604 Z" fill="#F59E0B"/>
    <path d="M470 430 C470 364 520 320 598 320 C676 320 726 364 726 430 V590 C726 634 692 670 646 670 H550 C504 670 470 634 470 590 Z" fill="#FEF3C7"/>
    <path d="M514 360 C540 332 576 318 598 318 C620 318 656 332 682 360" fill="none" stroke="#FCD34D" stroke-width="22" stroke-linecap="round"/>
    <circle cx="562" cy="466" r="12" fill="#F59E0B" opacity="0.55"/>
    <circle cx="628" cy="526" r="10" fill="#F59E0B" opacity="0.55"/>
    <circle cx="590" cy="588" r="11" fill="#F59E0B" opacity="0.55"/>
  </g>
'''


def buns_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="792" rx="246" ry="30" fill="#08131f" opacity="0.16" />
    <ellipse cx="494" cy="540" rx="130" ry="106" fill="#F59E0B"/>
    <ellipse cx="706" cy="540" rx="130" ry="106" fill="#D97706"/>
    <ellipse cx="494" cy="558" rx="114" ry="84" fill="#FEF3C7"/>
    <ellipse cx="706" cy="558" rx="114" ry="84" fill="#FDE68A"/>
    <g fill="#F8FAFC" opacity="0.7">
      <ellipse cx="452" cy="478" rx="10" ry="5" transform="rotate(18 452 478)" />
      <ellipse cx="506" cy="452" rx="10" ry="5" transform="rotate(-12 506 452)" />
      <ellipse cx="540" cy="496" rx="10" ry="5" transform="rotate(14 540 496)" />
      <ellipse cx="666" cy="468" rx="10" ry="5" transform="rotate(12 666 468)" />
      <ellipse cx="718" cy="446" rx="10" ry="5" transform="rotate(-8 718 446)" />
      <ellipse cx="754" cy="492" rx="10" ry="5" transform="rotate(16 754 492)" />
    </g>
  </g>
'''


def noodles_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="792" rx="246" ry="30" fill="#08131f" opacity="0.16" />
    <rect x="446" y="280" width="308" height="402" rx="42" fill="#FDE68A"/>
    <rect x="470" y="304" width="260" height="354" rx="34" fill="#FB7185" opacity="0.25"/>
    <path d="M520 392 C550 362 584 356 624 370 C670 386 692 430 682 474 C672 518 636 550 590 556 C542 560 500 534 484 490" fill="none" stroke="#F59E0B" stroke-width="18" stroke-linecap="round"/>
    <path d="M506 440 C536 404 590 394 634 414 C676 432 698 474 694 514" fill="none" stroke="#FCD34D" stroke-width="18" stroke-linecap="round"/>
    <path d="M512 500 C548 470 592 462 638 474 C666 482 688 502 700 528" fill="none" stroke="#FBBF24" stroke-width="18" stroke-linecap="round"/>
    <text x="600" y="618" text-anchor="middle" fill="#9F1239" font-family="Segoe UI, Arial, sans-serif" font-size="58" font-weight="800">NOODLES</text>
  </g>
'''


def momos_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="794" rx="248" ry="28" fill="#08131f" opacity="0.16" />
    <ellipse cx="600" cy="632" rx="228" ry="72" fill="#E2E8F0"/>
    <ellipse cx="600" cy="600" rx="206" ry="58" fill="#F8FAFC"/>
    <g fill="#FEF3C7">
      <path d="M468 560 C444 506 470 450 526 440 C554 480 560 524 542 564 C516 592 486 594 468 560 Z"/>
      <path d="M576 532 C552 478 580 422 636 412 C664 452 670 496 652 536 C626 564 594 566 576 532 Z"/>
      <path d="M664 570 C640 516 668 460 724 450 C752 490 758 534 740 574 C714 602 682 604 664 570 Z"/>
    </g>
    <g stroke="#F8FAFC" stroke-width="8" stroke-linecap="round" opacity="0.55">
      <path d="M492 492 C510 510 522 530 528 554"/>
      <path d="M600 464 C618 484 630 504 636 528"/>
      <path d="M688 502 C706 520 718 540 724 564"/>
    </g>
  </g>
'''


def tea_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="794" rx="248" ry="28" fill="#08131f" opacity="0.16" />
    <path d="M430 636 H738 C726 708 676 752 584 752 C498 752 448 712 430 636 Z" fill="#E2E8F0"/>
    <path d="M452 636 H716 C704 690 662 724 586 724 C514 724 474 694 452 636 Z" fill="#F8FAFC"/>
    <path d="M460 610 H712 C704 662 660 688 588 688 C520 688 478 662 460 610 Z" fill="#A16207"/>
    <path d="M738 618 C792 618 812 654 812 690 C812 732 778 754 738 754" fill="none" stroke="#E2E8F0" stroke-width="24" stroke-linecap="round"/>
    <path d="M540 384 C516 334 516 292 546 246" stroke="#DBEAFE" stroke-width="16" stroke-linecap="round" opacity="0.9"/>
    <path d="M610 372 C590 324 594 280 622 238" stroke="#DBEAFE" stroke-width="16" stroke-linecap="round" opacity="0.9"/>
    <path d="M660 540 C624 468 612 418 618 358 C696 382 742 452 734 538 C708 564 686 570 660 540 Z" fill="#22C55E"/>
  </g>
'''


def sunflower_oil_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="794" rx="250" ry="28" fill="#08131f" opacity="0.16" />
    <rect x="500" y="214" width="164" height="430" rx="56" fill="#F8FAFC"/>
    <rect x="522" y="286" width="120" height="304" rx="34" fill="#FCD34D" opacity="0.92"/>
    <rect x="534" y="166" width="96" height="74" rx="22" fill="#E5E7EB"/>
    <rect x="560" y="122" width="44" height="54" rx="16" fill="#CBD5E1"/>
    <circle cx="320" cy="496" r="96" fill="#F59E0B"/>
    <circle cx="320" cy="496" r="42" fill="#78350F"/>
    <g fill="#FDE047">
      <ellipse cx="320" cy="376" rx="22" ry="54"/>
      <ellipse cx="404" cy="412" rx="22" ry="54" transform="rotate(40 404 412)"/>
      <ellipse cx="430" cy="496" rx="22" ry="54" transform="rotate(90 430 496)"/>
      <ellipse cx="404" cy="580" rx="22" ry="54" transform="rotate(140 404 580)"/>
      <ellipse cx="320" cy="616" rx="22" ry="54"/>
      <ellipse cx="236" cy="580" rx="22" ry="54" transform="rotate(40 236 580)"/>
      <ellipse cx="210" cy="496" rx="22" ry="54" transform="rotate(90 210 496)"/>
      <ellipse cx="236" cy="412" rx="22" ry="54" transform="rotate(140 236 412)"/>
    </g>
    <path d="M320 592 C316 660 304 710 282 760" stroke="#16A34A" stroke-width="18" stroke-linecap="round"/>
  </g>
'''


def mango_juice_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="794" rx="246" ry="28" fill="#08131f" opacity="0.16" />
    <path d="M514 282 H676 L650 694 C646 738 616 764 596 764 C576 764 546 738 542 694 Z" fill="#DBEAFE"/>
    <path d="M536 332 H654 L634 688 C632 714 614 732 596 732 C578 732 560 714 558 688 Z" fill="#F59E0B" opacity="0.92"/>
    <path d="M600 286 L600 198" stroke="#F8FAFC" stroke-width="16" stroke-linecap="round"/>
    <path d="M600 198 L656 152" stroke="#F8FAFC" stroke-width="16" stroke-linecap="round"/>
    <path d="M376 560 C316 528 282 474 294 410 C314 322 404 278 494 304 C566 326 610 394 598 460 C582 548 494 612 376 560 Z" fill="#F59E0B"/>
    <path d="M470 286 C484 248 516 224 564 220 C550 262 520 290 470 286 Z" fill="#22C55E"/>
    <ellipse cx="412" cy="444" rx="70" ry="116" transform="rotate(34 412 444)" fill="#FDBA74" opacity="0.34"/>
  </g>
'''


def plates_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="794" rx="248" ry="28" fill="#08131f" opacity="0.16" />
    <circle cx="540" cy="500" r="160" fill="#F8FAFC"/>
    <circle cx="540" cy="500" r="122" fill="#EDE9FE"/>
    <circle cx="676" cy="560" r="160" fill="#F8FAFC" opacity="0.92"/>
    <circle cx="676" cy="560" r="122" fill="#DDD6FE" opacity="0.95"/>
    <circle cx="540" cy="500" r="88" fill="#FFFFFF"/>
    <circle cx="676" cy="560" r="88" fill="#FFFFFF"/>
  </g>
'''


def gulab_jamun_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="792" rx="248" ry="30" fill="#08131f" opacity="0.16" />
    <ellipse cx="600" cy="620" rx="224" ry="78" fill="#D1D5DB"/>
    <ellipse cx="600" cy="582" rx="206" ry="60" fill="#F8FAFC"/>
    <g fill="#92400E">
      <circle cx="520" cy="532" r="54"/>
      <circle cx="610" cy="504" r="54"/>
      <circle cx="692" cy="548" r="54"/>
      <circle cx="556" cy="604" r="54"/>
      <circle cx="650" cy="614" r="54"/>
    </g>
    <g fill="#FBBF24" opacity="0.35">
      <circle cx="504" cy="514" r="14"/>
      <circle cx="594" cy="488" r="14"/>
      <circle cx="676" cy="530" r="14"/>
      <circle cx="540" cy="590" r="14"/>
      <circle cx="634" cy="600" r="14"/>
    </g>
  </g>
'''


def eggs_art():
    return '''
  <g filter="url(#shadow)">
    <ellipse cx="600" cy="792" rx="250" ry="30" fill="#08131f" opacity="0.16" />
    <rect x="404" y="484" width="392" height="190" rx="38" fill="#A16207"/>
    <rect x="430" y="512" width="340" height="138" rx="28" fill="#B45309"/>
    <g fill="#FFFBEB">
      <ellipse cx="494" cy="516" rx="38" ry="52"/>
      <ellipse cx="578" cy="506" rx="38" ry="52"/>
      <ellipse cx="662" cy="518" rx="38" ry="52"/>
      <ellipse cx="536" cy="588" rx="38" ry="52"/>
      <ellipse cx="620" cy="596" rx="38" ry="52"/>
      <ellipse cx="704" cy="588" rx="38" ry="52"/>
    </g>
  </g>
'''


ART_FUNCTIONS = {
    'tomato': tomato_art,
    'spinach': spinach_art,
    'carrot': carrot_art,
    'onion': onion_art,
    'capsicum': capsicum_art,
    'broccoli': broccoli_art,
    'cauliflower': cauliflower_art,
    'cucumber': cucumber_art,
    'rice': rice_art,
    'dal': dal_art,
    'flour': flour_art,
    'turmeric': turmeric_art,
    'cumin': cumin_art,
    'milk': milk_art,
    'paneer': paneer_art,
    'bread': bread_art,
    'buns': buns_art,
    'noodles': noodles_art,
    'momos': momos_art,
    'peanut_butter': peanut_butter_art,
    'tea': tea_art,
    'sunflower_oil': sunflower_oil_art,
    'mango_juice': mango_juice_art,
    'plates': plates_art,
    'gulab_jamun': gulab_jamun_art,
    'eggs': eggs_art,
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, (title, category, art_key) in SHOWCASE_ART.items():
        palette = PALETTES[category]
        svg = wrap_svg(title, category, palette, ART_FUNCTIONS[art_key]())
        (OUTPUT_DIR / filename).write_text(svg, encoding='utf-8')
        print(f'Wrote {OUTPUT_DIR / filename}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
