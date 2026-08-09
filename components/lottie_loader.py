"""Offline Lottie animation factory.

Builds small, valid Lottie JSON payloads programmatically so the app never
depends on external animation CDNs. `streamlit-lottie` only needs a dict.
"""
from __future__ import annotations

import hashlib

from streamlit_lottie import st_lottie

CANVAS = 400
FPS = 30
FRAMES = 60


def _anim(name: str, layers: list[dict], *, w: int = CANVAS, h: int = CANVAS, fr: int = FPS, op: int = FRAMES) -> dict:
    return {
        "v": "5.7.4",
        "fr": fr,
        "ip": 0,
        "op": op,
        "w": w,
        "h": h,
        "nm": name,
        "ddd": 0,
        "assets": [],
        "layers": layers,
    }


def _transform(scale_key: list | None = None, rotate_key: list | None = None,
               pos: list[int] | None = None, opacity: float = 100) -> dict:
    return {
        "o": {"a": 0, "k": opacity},
        "r": {"a": 0 if rotate_key is None else 1, "k": rotate_key or 0},
        "p": {"a": 0, "k": list(pos or [CANVAS / 2, CANVAS / 2, 0])},
        "a": {"a": 0, "k": [0, 0, 0]},
        "s": {"a": 1 if scale_key else 0, "k": scale_key or [100, 100, 100]},
    }


def _pulse_scale(lo: float = 92, hi: float = 118) -> list:
    """Alternating scale keyframes."""
    m = (lo + hi) / 2
    return [
        {"t": 0,  "s": [m, m, 100], "e": [hi, hi, 100], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
        {"t": 15, "s": [hi, hi, 100], "e": [lo, lo, 100], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
        {"t": 30, "s": [lo, lo, 100], "e": [hi, hi, 100], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
        {"t": 45, "s": [hi, hi, 100], "e": [m, m, 100], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
        {"t": 60, "s": [m, m, 100], "e": [m, m, 100], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
    ]


def _rotate_key(lo: float = 0, hi: float = 360) -> list:
    return [
        {"t": 0, "s": [lo], "e": [hi]},
        {"t": 60, "s": [hi], "e": [lo + 360]},
    ]


def _ellipse(radius: list[int], color: tuple[float, float, float, float]) -> dict:
    return {
        "ty": "gr", "nm": "g", "it": [
            {"ty": "el", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": radius}, "nm": "el"},
            {"ty": "fl", "c": {"a": 0, "k": list(color)}, "o": {"a": 0, "k": 100}, "r": 1, "nm": "fl"},
            {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]},
             "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}, "sk": {"a": 0, "k": 0}, "sa": {"a": 0, "k": 0}, "nm": "tr"},
        ], "nm": "ellipse",
    }


def _polygon_triangle(size: float, color: tuple[float, float, float, float]) -> dict:
    """A play-triangle using a star/path shape: 3 points, outer=inner, roundness 0."""
    return {
        "ty": "gr", "nm": "g", "it": [
            {
                "ty": "sr", "sy": 1, "d": 1, "pt": {"a": 0, "k": 3},
                "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 0},
                "or": {"a": 0, "k": 0}, "ir": {"a": 0, "k": 0}, "is": {"a": 0, "k": 0}, "os": {"a": 0, "k": 0},
                "s": {"a": 0, "k": size}, "nm": "sr",
            },
            {"ty": "fl", "c": {"a": 0, "k": list(color)}, "o": {"a": 0, "k": 100}, "r": 1, "nm": "fl"},
            {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]},
             "r": {"a": 0, "k": 90}, "o": {"a": 0, "k": 100}, "sk": {"a": 0, "k": 0}, "sa": {"a": 0, "k": 0}, "nm": "tr"},
        ], "nm": "triangle",
    }


def _rect(w: float, h: float, color: tuple[float, float, float, float], r: float = 14) -> dict:
    return {
        "ty": "gr", "nm": "g", "it": [
            {"ty": "rc", "d": 1, "s": {"a": 0, "k": [w, h]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": r}, "nm": "rc"},
            {"ty": "fl", "c": {"a": 0, "k": list(color)}, "o": {"a": 0, "k": 100}, "r": 1, "nm": "fl"},
            {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]},
             "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}, "sk": {"a": 0, "k": 0}, "sa": {"a": 0, "k": 0}, "nm": "tr"},
        ], "nm": "rect",
    }


def _layer(shape: dict, *, ind: int, scale: list | None = None, rotate: list | None = None,
           pos: list[int] | None = None, opacity: float = 100) -> dict:
    return {
        "ddd": 0, "ind": ind, "ty": 4, "nm": f"L{ind}", "sr": 1,
        "ks": _transform(scale, rotate, pos, opacity),
        "ao": 0, "shapes": [shape], "ip": 0, "op": FRAMES, "st": 0, "bm": 0,
    }


RED = (0.898, 0.035, 0.078, 1)
WHITE = (1.0, 1.0, 1.0, 1.0)
GOLD = (0.961, 0.773, 0.094, 1)


def lottie_pulse_play() -> dict:
    """Pulsing red play button with a white triangle."""
    pulse = _pulse_scale()
    return _anim("pulse_play", [
        _layer(_ellipse([170, 170], RED), ind=1, scale=pulse),
        _layer(_polygon_triangle(58, WHITE), ind=2, scale=pulse),
    ])


def lottie_spinner() -> dict:
    """Rotating gold ring with a red core."""
    return _anim("spinner", [
        _layer(_ellipse([150, 150], GOLD), ind=1, rotate=_rotate_key(0, 360)),
        _layer(_ellipse([60, 60], RED), ind=2, scale=_pulse_scale(85, 115)),
    ])


def lottie_equalizer() -> dict:
    """Three bouncing bars like a music equalizer."""
    layers = []
    base_y = 240
    for i, (x, color, h, delay) in enumerate([
        (150, RED, 150, 0), (200, GOLD, 90, 10), (250, WHITE, 130, 20),
    ]):
        keys = [
            {"t": 0,  "s": [h, 40], "e": [h, 120], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
            {"t": 30, "s": [h, 120], "e": [h, 40], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
            {"t": 60, "s": [h, 40], "e": [h, 40], "i": {"x": [0.4], "y": [1]}, "o": {"x": [0.6], "y": [0]}},
        ]
        layers.append(_layer(_rect(h, 40, color, r=10), ind=i + 1,
                             pos=[x, base_y], scale=None))
        layers[-1]["ks"]["s"] = {"a": 1, "k": keys}
    return _anim("equalizer", layers)


def lottie_heart() -> dict:
    """Pulsing heart built from two circles + rotated square."""
    pulse = _pulse_scale(90, 116)
    c1 = _ellipse([70, 70], RED)
    c2 = _ellipse([70, 70], RED)
    sq = _rect(96, 96, RED, r=18)
    layers = [
        _layer(c1, ind=1, pos=[150, 160], scale=pulse),
        _layer(c2, ind=2, pos=[250, 160], scale=pulse),
        _layer(sq, ind=3, pos=[200, 214], rotate=_rotate_key(45, 405), scale=pulse),
    ]
    return _anim("heart", layers)


_LOTTIE_BUILDERS = {
    "pulse_play": lottie_pulse_play,
    "spinner": lottie_spinner,
    "equalizer": lottie_equalizer,
    "heart": lottie_heart,
}


def get_lottie(name: str) -> dict:
    """Return a cached lottie dict by key name."""
    return _LOTTIE_BUILDERS[name]()


def render(name: str, height: int = 140, width: int | None = None, key: str | None = None) -> None:
    """Render a lottie animation through streamlit-lottie."""
    payload = get_lottie(name)
    if width is None:
        width = height
    st_lottie(
        payload,
        height=height,
        width=width,
        key=key or f"lottie-{name}-{hashlib.md5(name.encode()).hexdigest()[:6]}",
        loop=True,
    )
