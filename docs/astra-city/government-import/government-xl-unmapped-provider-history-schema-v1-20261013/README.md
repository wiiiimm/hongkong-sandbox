# Four XL sources: public historical-ID route audit

Codex ROOT, 13 October 2026, HKS-203. No installations, model processing,
geometry edits, database writes or lease acquisition occurred in this audit.
The fixed XL scope remains 521, with 234 installed and 287 remaining.

The earlier identity pass proposed obtaining B1000 old/new CSUID lookup
records for four unchanged original sources. This audit captures the current
Building MapServer and every advertised layer/table, rather than repeating
feature queries already completed on 9 October. Its seven schemas explicitly
disable historical-moment queries and are neither archived nor versioned.
None advertises relationships or the B1000 old/new identity fields.
`BuildingWorksHistory` records works, providers and dates; it is not the
documented B1000 `BLDG_CSUID` lookup table containing `O_BLDG_CSUID`,
`O_GEO_REFNO` and `OPERATION`.

This closes that particular public-interface route. It does not prove that
the historical lookup is unavailable elsewhere, that any building was
demolished, or that any original source is corrupted or permanently
uninstallable. All four identity holds remain unaccepted. Nearby named
features and retained model-package membership cannot establish ownership.

| Original model | Original GeoRef | Type | Next evidence needed |
| --- | --- | --- | --- |
| B349971856402063C0 | 3499718564 | Podium | Exact old/new provider identity or source-epoch ownership |
| B360171738601063C0 | 3601717386 | Tower | Exact old/new provider identity or source-epoch ownership |
| B365201779201063C0 | 3652017792 | Tower | Exact old/new provider identity or source-epoch ownership |
| B352981210001063C0 | 3529812100 | Tower | Exact old/new provider identity or source-epoch ownership |

`root-four-source-review.json` binds each source key and SHA-256, the fixed
inventory reconciliation, the unchanged current manifest, the capture script,
every raw schema/receipt and the official B1000 contract. ROOT independently
verified all 23 references and every advertised schema assertion. The
original-model worker restart still awaits the previously requested approval;
this evidence audit does not restart those workers or resolve that approval.

Reproduction, in a fresh output location (the script deliberately refuses to
overwrite the retained evidence directory):

```sh
python3 source-scripts/city/government-import/xl_unmapped_provider_history_schema_20261013.py
```

Primary sources:
[Building MapServer](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer)
and [B1000 contract](https://www.hkmapmeta.gov.hk/mcs/home/web/data/lands/b1000.faq.html).
The latter documents identity history, not the historical records for these
four models. No external message or provider request has been sent.
