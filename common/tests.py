# common/tests.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Any

# Importa lo que vas a probar
from common.geometry import (
    Point,
    Segment,
    Polygon,
    distance,
    point_in_polygon,
    segments_intersect,
    segment_intersects_polygon,
)

# Si tu geometry.py no tiene alguno de estos nombres, cambia SOLO el import.
# Por ejemplo: segments_intersect -> _segments_intersect, etc.


@dataclass
class TestResult:
    name: str
    ok: bool
    detail: str = ""


class GeometryTests:
    """
    Tests "a pelo" sin framework: asserts que lanzan AssertionError.
    run_all() recorre métodos test_* y devuelve resultados.
    """

    # ---------- helpers ----------
    def assert_true(self, cond: bool, msg: str = "assert_true falló") -> None:
        if not cond:
            raise AssertionError(msg)

    def assert_false(self, cond: bool, msg: str = "assert_false falló") -> None:
        if cond:
            raise AssertionError(msg)

    def assert_equal(self, a: Any, b: Any, msg: str = "assert_equal falló") -> None:
        if a != b:
            raise AssertionError(f"{msg}: {a!r} != {b!r}")

    def assert_almost(self, a: float, b: float, eps: float = 1e-9, msg: str = "assert_almost falló") -> None:
        if abs(a - b) > eps:
            raise AssertionError(f"{msg}: |{a} - {b}| = {abs(a-b)} > {eps}")

    # ---------- fixtures ----------
    def build_gotham(self) -> tuple[Polygon, Polygon, dict[str, Point]]:
        # Polígonos del ejemplo que pasaste (ZP1 y ZR1)
        zp1 = Polygon([
            Point(2.0, 1.0),
            Point(4.0, 1.0),
            Point(4.0, 3.0),
            Point(2.0, 3.0),
        ])

        zr1 = Polygon([
            Point(-1.0, 2.0),
            Point(1.0, 2.0),
            Point(1.0, 5.0),
            Point(-1.0, 5.0),
        ])

        nodes = {
            "H": Point(0.0, 0.0),
            "C1": Point(5.0, 2.0),
            "C2": Point(-3.0, 4.0),
            "R1": Point(1.0, 6.0),
        }
        return zp1, zr1, nodes

    # ---------- tests ----------
    def test_distance_3_4_5(self) -> None:
        self.assert_almost(distance(Point(0, 0), Point(3, 4)), 5.0)

    def test_segments_intersection_basic(self) -> None:
        s1 = Segment(Point(0, 0), Point(4, 4))
        s2 = Segment(Point(0, 4), Point(4, 0))
        s3 = Segment(Point(5, 5), Point(6, 6))
        self.assert_true(segments_intersect(s1, s2), "s1 y s2 deberían intersectar")
        self.assert_false(segments_intersect(s1, s3), "s1 y s3 NO deberían intersectar")

    def test_point_in_polygon_inside_outside_border(self) -> None:
        zp1, _, _ = self.build_gotham()

        inside = Point(3.0, 2.0)
        outside = Point(10.0, 10.0)
        border = Point(2.0, 2.0)

        self.assert_true(point_in_polygon(inside, zp1, include_boundary=True), "inside")
        self.assert_false(point_in_polygon(outside, zp1, include_boundary=True), "outside")
        self.assert_true(point_in_polygon(border, zp1, include_boundary=True), "borde included")
        self.assert_false(point_in_polygon(border, zp1, include_boundary=False), "borde excluded")

    def test_segment_intersects_polygon(self) -> None:
        zp1, _, nodes = self.build_gotham()

        # H->C1 cruza el rectángulo ZP1 (x de 2 a 4, y de 1 a 3)
        seg_cross = Segment(nodes["H"], nodes["C1"])
        self.assert_true(segment_intersects_polygon(seg_cross, zp1, include_boundary=True))

        # H->C2 no debería cruzar ZP1
        seg_free = Segment(nodes["H"], nodes["C2"])
        self.assert_false(segment_intersects_polygon(seg_free, zp1, include_boundary=True))

    # ---------- runner ----------
    def run_all(self) -> list[TestResult]:
        results: list[TestResult] = []
        test_methods = [name for name in dir(self) if name.startswith("test_")]

        for name in sorted(test_methods):
            fn = getattr(self, name)
            if not callable(fn):
                continue
            try:
                fn()
                results.append(TestResult(name=name, ok=True))
            except Exception as e:
                results.append(TestResult(name=name, ok=False, detail=str(e)))

        return results


def print_results(results: Iterable[TestResult]) -> None:
    results = list(results)
    ok = sum(1 for r in results if r.ok)
    bad = len(results) - ok

    print("\n=== TESTS GEOMETRY ===")
    for r in results:
        if r.ok:
            print(f"[OK ] {r.name}")
        else:
            print(f"[FAIL] {r.name} -> {r.detail}")

    print(f"\nResumen: {ok} OK / {bad} FAIL\n")
    if bad:
        raise SystemExit(1)