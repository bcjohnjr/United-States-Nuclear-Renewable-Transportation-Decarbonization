# V9.14 response to the final V9.13 referee comments

| Referee request | Implemented correction | Verification |
| --- | --- | --- |
| Correct lifecycle coefficient subtraction | Single source coefficient (`us2_model.CI_RESIDUES_GRASSES_G_MJ=10`), crop-energy budget and matched sensitivity baseline adjustment; S32 adds unit-level trace | 431.6 TWh crop, 1,173.878 TWh total mixed route, 15.5376 Mt generic crop factor; invariance checks at 7/10/13 g/MJ |
| Abstract omits frequent zero-residue result | Adds 59.8% of 1,000 uncalibrated Monte Carlo draws selecting no residue | Word abstract length and MC summary checked |
| Delivery cost ambiguity | Defines an *incremental crop-only price surcharge over the baseline screened delivered tier*, distinct from nutrient, treatment and BT23 farmgate prices | Article, S31/S32, cover letter and release note |
| Flat environment / executable code | Windows quick/full launchers, Linux launcher and isolated full rebuild; all inputs and scripts at ZIP root | Quick validator and signed release; Windows .bat syntax inspected (not run on native Windows) |
| Figures and numerical contents | Regenerates current Fig. 1, Fig. 5, Fig. S30; compiles four Word files and 35 TIFFs into editor-only ZIP | Image-pixel match, 600-dpi RGB audit and exact archived-file equality |
| Grid Harvester preservation | Untouched mandatory S1/S22 and source engineering comparison | Source-versus-embedded pixel check and 90.9/33.9 MJ numerical comparison |
| Author approval/claims and AI permission | Cannot be inferred; clearly listed as unresolved. Company and patent disclosure statements now require confirmation rather than certifying no patents | `AUTHOR_CLEARANCE_PENDING_V9.14.md` and provenance table |
| GitHub/Zenodo DOI | Not fabricated. Current release carries hashes and deployment instructions | Publish exact ZIP contents later and verify tag/DOI before modifying manuscript |

This response closes *computational and manuscript-editing* comments. It does **not** close real-world authorship, competing interests, data availability, image permissions, Science editorial policy, or regional scientific-validation gaps.
