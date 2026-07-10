import os

SVGS = {
    'hero_mandi_dawn.svg': """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617" />
      <stop offset="60%" stop-color="#0b1528" />
      <stop offset="100%" stop-color="#1e1b4b" />
    </linearGradient>
    <radialGradient id="sun" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f97316" stop-opacity="0.25" />
      <stop offset="50%" stop-color="#fb923c" stop-opacity="0.05" />
      <stop offset="100%" stop-color="#020617" stop-opacity="0" />
    </radialGradient>
    <linearGradient id="wave1" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f97316" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#429dfe" stop-opacity="0" />
    </linearGradient>
    <linearGradient id="wave2" x1="100%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="#429dfe" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#f97316" stop-opacity="0" />
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.03)" stroke-width="1" />
    </pattern>
  </defs>
  <!-- Background -->
  <rect width="1200" height="800" fill="url(#bg)" />
  <!-- Grid -->
  <rect width="1200" height="800" fill="url(#grid)" />
  <!-- Sun Glow -->
  <circle cx="900" cy="200" r="400" fill="url(#sun)" />
  <!-- Abstract Hills / Produce heaps -->
  <path d="M 0 500 Q 300 400 600 550 T 1200 450 L 1200 800 L 0 800 Z" fill="url(#wave1)" />
  <path d="M 0 600 Q 400 700 800 580 T 1200 650 L 1200 800 L 0 800 Z" fill="url(#wave2)" />
  <!-- Organic Lines (Chilli/Vegetable silhouette) -->
  <path d="M 850 350 C 900 300, 950 380, 1000 330 C 1050 280, 1020 200, 950 250 C 880 300, 800 400, 850 350 Z" fill="none" stroke="rgba(249, 115, 22, 0.2)" stroke-width="2" />
  <path d="M 920 280 Q 940 240 980 260" fill="none" stroke="rgba(66, 157, 254, 0.3)" stroke-width="2.5" stroke-linecap="round" />
  <!-- Abstract leaves -->
  <path d="M 150 250 Q 200 200 250 250 T 350 250" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1.5" />
</svg>""",

    'marketplace_staples.svg': """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080808" />
      <stop offset="50%" stop-color="#14110f" />
      <stop offset="100%" stop-color="#1c140e" />
    </linearGradient>
    <radialGradient id="goldGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#d97706" stop-opacity="0.2" />
      <stop offset="60%" stop-color="#f59e0b" stop-opacity="0.05" />
      <stop offset="100%" stop-color="#080808" stop-opacity="0" />
    </radialGradient>
    <linearGradient id="spiceGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#d97706" stop-opacity="0.12" />
      <stop offset="100%" stop-color="#020617" stop-opacity="0" />
    </linearGradient>
    <pattern id="grain_pattern" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
      <circle cx="10" cy="10" r="1.5" fill="rgba(217, 119, 6, 0.15)" />
      <circle cx="30" cy="30" r="1.5" fill="rgba(217, 119, 6, 0.1)" />
      <circle cx="50" cy="50" r="1.5" fill="rgba(217, 119, 6, 0.15)" />
    </pattern>
  </defs>
  <!-- Background -->
  <rect width="1200" height="800" fill="url(#bg)" />
  <!-- Grain Pattern -->
  <rect width="1200" height="800" fill="url(#grain_pattern)" />
  <!-- Gold Glow -->
  <circle cx="600" cy="400" r="500" fill="url(#goldGlow)" />
  <!-- Layered spice heap vectors -->
  <path d="M -100 800 L 200 400 Q 400 350 600 500 T 1300 800 Z" fill="url(#spiceGrad)" />
  <!-- Abstract wheat line art -->
  <g stroke="rgba(245, 158, 11, 0.15)" stroke-width="1.5" fill="none" stroke-linecap="round">
    <!-- Stem 1 -->
    <path d="M 800 700 Q 820 500 880 300" />
    <path d="M 880 300 Q 890 280 910 270" />
    <!-- Grains -->
    <path d="M 865 370 Q 885 360 880 345 Z" fill="rgba(245, 158, 11, 0.1)" />
    <path d="M 855 350 Q 840 340 850 325 Z" fill="rgba(245, 158, 11, 0.1)" />
    <path d="M 875 320 Q 895 310 890 295 Z" fill="rgba(245, 158, 11, 0.1)" />
    <path d="M 860 300 Q 845 290 855 275 Z" fill="rgba(245, 158, 11, 0.1)" />
  </g>
</svg>""",

    'vendor_stall_morning.svg': """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617" />
      <stop offset="60%" stop-color="#080e1a" />
      <stop offset="100%" stop-color="#1a120b" />
    </linearGradient>
    <radialGradient id="warmLight" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f97316" stop-opacity="0.18" />
      <stop offset="70%" stop-color="#ea580c" stop-opacity="0.03" />
      <stop offset="100%" stop-color="#020617" stop-opacity="0" />
    </radialGradient>
    <pattern id="streetGrid" width="80" height="80" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
      <line x1="0" y1="0" x2="0" y2="80" stroke="rgba(255, 255, 255, 0.02)" stroke-width="1" />
      <line x1="0" y1="0" x2="80" y2="0" stroke="rgba(255, 255, 255, 0.02)" stroke-width="1" />
    </pattern>
  </defs>
  <!-- Background -->
  <rect width="1200" height="800" fill="url(#bg)" />
  <!-- Street Grid -->
  <rect width="1200" height="800" fill="url(#streetGrid)" />
  <!-- Warm Light -->
  <circle cx="200" cy="600" r="500" fill="url(#warmLight)" />
  <!-- Abstract Kettle / Stall silhouette -->
  <g stroke="rgba(249, 115, 22, 0.25)" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <!-- Kettle body -->
    <path d="M 400 450 L 500 450 L 520 550 L 380 550 Z" />
    <!-- Lid and handle -->
    <path d="M 420 450 L 420 430 L 480 430 L 480 450" />
    <path d="M 450 430 Q 450 380 400 380 Q 350 380 350 450" stroke-width="1.5" />
    <!-- Spout -->
    <path d="M 510 480 Q 550 460 560 430" />
    <!-- Steam lines -->
    <path d="M 560 410 Q 565 390 560 380" stroke="rgba(255,255,255,0.15)" stroke-width="1.5" />
    <path d="M 570 415 Q 575 395 570 385" stroke="rgba(255,255,255,0.1)" stroke-width="1.5" />
  </g>
  <!-- Abstract stall lines -->
  <line x1="100" y1="200" x2="350" y2="200" stroke="rgba(255,255,255,0.06)" stroke-width="3" />
  <line x1="150" y1="200" x2="150" y2="600" stroke="rgba(255,255,255,0.06)" stroke-width="2" />
  <line x1="300" y1="200" x2="300" y2="600" stroke="rgba(255,255,255,0.06)" stroke-width="2" />
</svg>"""
}

OUTPUT_DIR = 'my_app/static/uploads'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, content in SVGS.items():
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Generated {name} at {path}")

if __name__ == '__main__':
    main()
