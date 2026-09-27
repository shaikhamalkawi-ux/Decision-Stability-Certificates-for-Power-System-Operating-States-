# Reviewed research drafts, version 1

This separate working-draft version records independently reviewed experimental evidence through commit 520fe5974a4d92892906c42ce51a9d12ef304d3a. It preserves V8/V8R1 and their releases. The active fresh-week energy continuation is not included.

Read the English research note or the Arabic scientific decision report in PDF. DOCX files contain editable text and native equations; JSON is the explicit source for src/research8h_build_manuscripts.py, and Markdown provides an accessible text version. The English PDF has 9 pages; the Arabic PDF has 5 pages. All final pages were visually checked; DOCUMENT_QA.json records structural checks. The figure file remains in results/research8h/energy_bound_figure and is embedded in both DOCX/PDF files.

Scientific review: ../DRAFT_MANUSCRIPT_SCIENTIFIC_REVIEW.md and ../DRAFT_MANUSCRIPT_DELTA_REVIEW.md. Evidence map: ../EVIDENCE_CLAIM_MAP.md. These drafts are not a submission-ready verdict or a new Zenodo release. The existing DOI records the frozen V8 release only.

Build from the repository root with Python and python-docx:

    python src/research8h_build_manuscripts.py --source docs/research8h/manuscript_v1/note_en.json --output NEW_DIRECTORY/Temporal_Feasibility_Research_Note_DRAFT.docx --root .

Use decision_ar.json analogously. Rendering used LibreOffice through the document skill renderer; page images are review intermediates, not delivery files. Review scripts perform no solver calls.
