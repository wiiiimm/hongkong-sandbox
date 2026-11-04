"""Verify saved public record plans or acquire them with a complete trusted chain.

This is document acquisition, never a model worker or a database operation.
The published intermediate is untrusted input until OpenSSL proves its chain to
the pre-existing system CA bundle. No partial-chain trust or TLS bypass is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import ssl
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/astra-city/government-import/government-xl-youth-square173512-record-plan-transport-v2-20261013"
INTERMEDIATE_SHA = "cb730c3a5fe958b8bdc5b363892c9f530b33f98a43ce3c2578fce096b4ae233c"
PDFS = {
    "english": ("e", "5697e976d22dfe88cd469c060f8b41376991521eacde33d8d6dffbb307991ebe"),
    "chinese": ("c", "472f49e493b27c62e4bfb7ad536d093652396ffea54948ff0716d832fe6acc85"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verified_context():
    intermediate = EVIDENCE / "published-intermediate.crt"
    if sha(intermediate.read_bytes()) != INTERMEDIATE_SHA:
        raise ValueError("Published intermediate differs from the captured revision")
    pem = subprocess.run(
        ["openssl", "x509", "-inform", "DER", "-in", str(intermediate), "-outform", "PEM"],
        check=True, capture_output=True, text=True,
    ).stdout
    # -untrusted supplies a chain member; it is not an additional trust anchor.
    verification = subprocess.run(
        ["openssl", "verify", "-show_chain", "-verify_hostname", "www.legco.gov.hk",
         "-CAfile", ssl.get_default_verify_paths().cafile,
         "-untrusted", str(EVIDENCE / "published-intermediate.pem"),
         str(EVIDENCE / "observed-legco-leaf.pem")],
        check=True, capture_output=True, text=True,
    )
    if pem != (EVIDENCE / "published-intermediate.pem").read_text():
        raise ValueError("Saved intermediate PEM does not match the pinned DER")
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cadata=pem)
    if ctx.verify_mode != ssl.CERT_REQUIRED or not ctx.check_hostname:
        raise ValueError("Strict TLS verification is required")
    if ctx.verify_flags & ssl.VERIFY_X509_PARTIAL_CHAIN:
        raise ValueError("Partial-chain trust is forbidden")
    return ctx, verification.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Read public HTTPS PDFs; never overwrite a saved revision")
    args = parser.parse_args()
    ctx, chain = verified_context()
    rows = []
    for language, (suffix, expected) in PDFS.items():
        url = f"https://www.legco.gov.hk/yr18-19/{language}/fc/pwsc/papers/pwsc20190111pwsc-71-1-{suffix}.pdf"
        path = EVIDENCE / f"original-record-plans-{language}.pdf"
        data = path.read_bytes()
        if not data.startswith(b"%PDF-") or sha(data) != expected:
            raise ValueError(f"Saved {language} PDF differs from the pinned source")
        if args.download:
            with urllib.request.urlopen(url, timeout=30, context=ctx) as response:
                fetched = response.read(25_000_001)
            if len(fetched) > 25_000_000 or sha(fetched) != expected:
                raise ValueError("Changed or oversized document requires a new revision; saved bytes retained")
        rows.append({"url": url, "path": str(path.relative_to(ROOT)), "bytes": len(data), "sha256": expected})
    print(json.dumps({"existingRootChain": chain, "hostnameVerified": True,
                      "partialChainTrust": False, "pdfs": rows, "modelWorkersStarted": False}, indent=2))


if __name__ == "__main__":
    main()
