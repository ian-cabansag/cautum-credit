"""Compatibility entry point. Rebuild evidence exhibits without reverting to old placeholders."""

from .build_evidence_package import ROOT, build

if __name__ == "__main__":
    build(ROOT / "deliverables/vendor/reveal-6.0.2")
