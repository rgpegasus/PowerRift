# Plateformes et musique par map.
# Rouge (#cc3333) = solid   |   Orange (#cc8800) = platform traversable

MAP1_PLATFORMS = [
    ("solid",    "#2a2f26", False, (4.65, 1.75), (-3.25, -3.15)),
    ("solid",    "#2a2f26", False, (4.3,  1.75), ( 4.45, -3.15)),
    ("platform", "#636226", False, (3.24, 0.65), ( 0.69, -2.60)),
    ("solid",    "#2f2629", False, (2.2,  3.00), (-6.4,   2.20)),
    ("solid",    "#2f2629", False, (6.4,  1.00), ( 0.0,   1.70)),
    ("platform", "#636226", False, (2.1,  0.65), (-4.25,  1.875)),
    ("solid",    "#2f2629", False, (2.8,  1.15), ( 6.05,  3.90)),
]

# 4 blocs visibles placeholder — positions à ajuster via le debug
MAP2_PLATFORMS = [
    ("platform", "#cc8800", False, ( 4.723, 0.200), (-0.030,  1.682)),
    ("platform", "#cc8800", False, ( 5.005, 0.275), (-5.984, -0.525)),
    ("platform", "#cc8800", False, ( 5.074, 0.200), ( 5.980, -0.489)),
    ("solid",    "#cc3333", False, (10.687, 0.200), (-0.091, -3.509)),
]

MAP3_PLATFORMS = [
    ("platform", "#cc8800", False, ( 3.180, 0.200), (-5.772,  1.400)),
    ("platform", "#cc8800", False, ( 6.000, 0.325), ( 4.900,  1.080)),
    ("platform", "#cc8800", False, ( 3.120, 0.200), (-0.542, -1.480)),
    ("solid",    "#cc3333", False, (14.634, 0.409), (-0.713, -4.569)),
    ("solid",    "#cc3333", False, ( 1.285, 2.401), ( 6.352,  0.023)),
]

PLATFORM_CONFIGS = {
    "background": MAP1_PLATFORMS,
    "map2":       MAP2_PLATFORMS,
    "map3":       MAP3_PLATFORMS,
}

# Clé pour resourceManager.music(key) — fichiers: map2.flac, map3.mp3
MAP_MUSIC = {
    "map2": "map2",
    "map3": "map3",
}


def build_platforms(selected_map):
    from ursina import Entity, scene
    from game.core.state import state
    cfg = PLATFORM_CONFIGS.get(selected_map, MAP1_PLATFORMS)
    # Appliquer la luminosité au monde 3D
    try:
        b = state.brightness / 100.0
        scene.setColorScale(b, b, b, 1)
    except Exception:
        pass
    return [
        Entity(z=-1, name=n, collider='box', model='quad',
               color=c, visible=v, scale=s, position=p)
        for n, c, v, s, p in cfg
    ]
